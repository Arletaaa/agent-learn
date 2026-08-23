"""
项目四：Planning 策略对比实验

用纯 Python + DeepSeek API 实现三种 Planning 策略，
在同一任务上对比 Token 消耗、执行轨迹和输出质量。

策略：
  1. ReAct（基准线）    — Think → Act → Observe 循环
  2. Plan-and-Execute   — 先规划再执行
  3. Reflexion          — 执行 + 自我评估 + 反思重试

依赖安装：
  pip install openai

运行：
  set DEEPSEEK_API_KEY=sk-xxx
  python compare_planning.py
"""
import json
import os
import sys
import time
from openai import OpenAI

# 修复 Windows 中文终端编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ──────────────────────────────────────────────────────────
#  底层工具和 LLM 调用
# ──────────────────────────────────────────────────────────

TOOLS = {
    "search": lambda q: f'搜索"{q}"的结果：Python 3.12 在 2023 年 10 月发布，引入了更友好的错误信息和性能提升。大量 AI/ML 库（PyTorch、LangChain）均已支持。',
    "calculator": lambda expr: f"计算结果：{eval(expr)}",
    "weather": lambda city: f"{city}今天晴，气温 25°C，湿度 60%。",
    "translate": lambda text, target="英文": f'翻译结果（{target}）："{text}" → "Hello World"',
}

COST_PER_1K = {"deepseek-chat": {"prompt": 0.00014, "completion": 0.00028}}  # USD

_tracker = {"prompt_tokens": 0, "completion_tokens": 0, "total_calls": 0, "total_cost": 0.0}


def call_llm(messages, system_prompt=None, temperature=0, max_tokens=1024):
    """调用 DeepSeek API，返回文本 + 统计 Token"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as e:
        print(f"  ⚠️  LLM 调用失败: {e}")
        return "[LLM 调用失败]", 0, 0

    usage = resp.usage
    prompt_tokens = usage.prompt_tokens if usage else 0
    completion_tokens = usage.completion_tokens if usage else 0

    model = resp.model or "deepseek-chat"
    cost = (prompt_tokens / 1000) * COST_PER_1K.get(model, {}).get("prompt", 0) + \
           (completion_tokens / 1000) * COST_PER_1K.get(model, {}).get("completion", 0)

    _tracker["prompt_tokens"] += prompt_tokens
    _tracker["completion_tokens"] += completion_tokens
    _tracker["total_calls"] += 1
    _tracker["total_cost"] += cost

    return resp.choices[0].message.content, prompt_tokens, completion_tokens


def reset_tracker():
    for k in _tracker:
        _tracker[k] = 0


# ──────────────────────────────────────────────────────────
#  策略一：ReAct（基准线）
# ──────────────────────────────────────────────────────────

REACT_SYSTEM = """你是一个采用 ReAct 策略的 AI Agent。按以下格式回复：

对于每一步：
  Thought: <你的推理>
  Action: <工具名>[<输入>]

如果已获得最终答案：
  Thought: 我已经有足够信息回答了
  Action: Finish[<最终答案>]

可用工具：
- search[查询词] — 搜索信息
- calculator[表达式] — 数学计算
- weather[城市名] — 查询天气
- translate[文本] — 翻译文本
"""


def react_strategy(task: str, max_steps: int = 5):
    """ReAct: Think → Act → Observe 循环"""
    print("\n  ┌─ ReAct 策略 ─────────────────────────────")
    messages = [{"role": "user", "content": task}]
    trajectory = []

    for step in range(max_steps):
        raw, pt, ct = call_llm(messages, system_prompt=REACT_SYSTEM)
        trajectory.append(raw)
        print(f"  │ Step {step+1}:")
        for line in raw.strip().split("\n")[:3]:
            print(f"  │   {line}")

        if "Finish[" in raw:
            answer = raw.split("Finish[")[1].split("]")[0]
            print(f"  └─ ✅ 成功 ({step+1} 步)")
            return answer, trajectory
        elif "Search[" in raw:
            query = raw.split("Search[")[1].split("]")[0]
            obs = TOOLS["search"](query)
        elif "Calculator[" in raw:
            expr = raw.split("Calculator[")[1].split("]")[0]
            obs = TOOLS["calculator"](expr)
        elif "Weather[" in raw:
            city = raw.split("Weather[")[1].split("]")[0]
            obs = TOOLS["weather"](city)
        elif "Translate[" in raw:
            text = raw.split("Translate[")[1].split("]")[0]
            obs = TOOLS["translate"](text)
        else:
            obs = "工具调用格式错误，请检查 Action 格式。"
            print(f"  │   ⚠️ 无法解析工具调用")

        messages.append({"role": "assistant", "content": raw})
        messages.append({"role": "user", "content": f"Observation: {obs}"})
        print(f"  │   Observation: {obs[:60]}...")

    print(f"  └─ ⚠️ 达到最大步数 ({max_steps})，返回最后结果")
    return trajectory[-1] if trajectory else "无结果", trajectory


# ──────────────────────────────────────────────────────────
#  策略二：Plan-and-Execute
# ──────────────────────────────────────────────────────────

PLAN_SYSTEM = """你是一个采用 Plan-and-Execute 策略的 AI Agent。

请先为任务制定完整的执行计划，然后逐步执行。

输出格式（严格 JSON）：
{
  "plan": [
    {"step": 1, "description": "步骤描述", "tool": "search", "input": "搜索词"},
    {"step": 2, "description": "步骤描述", "tool": "calculator", "input": "表达式"},
    ...
  ]
}

可用工具：search, calculator, weather, translate

注意：确保 JSON 格式正确，不要有多余文字。
"""


def plan_and_execute_strategy(task: str):
    """Plan-and-Execute: 先规划再执行"""
    print("\n  ┌─ Plan-and-Execute 策略 ──────────────────")

    # 第一步：生成计划
    raw, pt1, ct1 = call_llm(
        [{"role": "user", "content": f"任务：{task}\n请生成执行计划。"}],
        system_prompt=PLAN_SYSTEM,
        max_tokens=2048,
    )
    print(f"  │ 生成计划 →")

    try:
        if "```json" in raw:
            json_str = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            json_str = raw.split("```")[1].split("```")[0]
        else:
            json_str = raw
        plan_data = json.loads(json_str.strip())
        steps = plan_data.get("plan", plan_data.get("steps", []))
    except json.JSONDecodeError:
        print(f"  │   ⚠️ JSON 解析失败，回退到简单模式")
        steps = [
            {"step": 1, "description": "搜索信息", "tool": "search", "input": task}
        ]

    for s in steps:
        print(f"  │   Step {s['step']}: {s.get('description', s.get('tool', '?'))}")

    # 第二步：逐步执行
    results = []
    for s in steps:
        tool = s.get("tool", "search")
        inp = s.get("input", task)
        obs = TOOLS.get(tool, TOOLS["search"])(inp) if callable(TOOLS.get(tool)) else TOOLS["search"](inp)
        results.append(f"Step {s['step']}: {obs}")
        print(f"  │   执行 Step {s['step']}: {obs[:60]}...")

    # 第三步：综合结果
    summary_prompt = f"""
任务：{task}

执行结果：
{chr(10).join(results)}

请基于以上执行结果给出最终答案。
"""
    final, pt2, ct2 = call_llm([{"role": "user", "content": summary_prompt}])
    print(f"  │ 综合结果 → {final[:80]}...")
    print(f"  └─ ✅ 完成 (2 次 LLM 调用)")
    return final, results


# ──────────────────────────────────────────────────────────
#  策略三：Reflexion
# ──────────────────────────────────────────────────────────

EVAL_SYSTEM = """你是一个评估者。判断以下回答是否完整正确地回答了原始问题。

回复格式：
- 如果回答正确完整 → "PASS"
- 如果回答不完整或有错误 → "FAIL: <具体原因>"
"""

REFLECT_SYSTEM = """你是一个反思者。你执行了以下任务但失败了。

请分析失败原因并给出改进建议，下次执行时你应该注意什么。

回复格式：
【反思】
1. 失败原因：...
2. 改进建议：...
"""


def reflexion_strategy(task: str, max_attempts: int = 3):
    """Reflexion: 执行 + 自我评估 + 反思重试"""
    print("\n  ┌─ Reflexion 策略 ─────────────────────────")
    memory = []

    for attempt in range(max_attempts):
        print(f"  │ 尝试 {attempt+1}/{max_attempts}...")

        # 构建带反思的 System Prompt
        system = REACT_SYSTEM
        if memory:
            system += f"\n\n【历史反思经验】\n{chr(10).join(memory)}"

        # Actor: 使用 ReAct 执行
        answer, trajectory = react_strategy(task)

        # Evaluator: 判断结果
        eval_prompt = [{
            "role": "user",
            "content": f"原始问题：{task}\n\n回答：{answer}\n\n请评估。"
        }]
        evaluation, pt, ct = call_llm(eval_prompt, system_prompt=EVAL_SYSTEM)
        print(f"  │   评估结果：{evaluation[:80]}")

        if evaluation.startswith("PASS"):
            print(f"  └─ ✅ 成功 ({attempt+1} 次尝试)")
            return answer, trajectory

        # Reflector: 反思失败原因
        reflect_prompt = [{
            "role": "user",
            "content": f"任务：{task}\n你的回答：{answer}\n评估：{evaluation}\n请反思。"
        }]
        reflection, pt2, ct2 = call_llm(reflect_prompt, system_prompt=REFLECT_SYSTEM)
        memory.append(reflection)
        print(f"  │   反思：{reflection[:80]}...")

    print(f"  └─ ⚠️ 达到最大尝试次数")
    return answer if 'answer' in dir() else "无结果", []


# ──────────────────────────────────────────────────────────
#  主程序：对比实验
# ──────────────────────────────────────────────────────────

def print_stats(label):
    """打印 Token 消耗统计"""
    tokens = _tracker["prompt_tokens"] + _tracker["completion_tokens"]
    print(f"  {label}:")
    print(f"    LLM 调用次数: {_tracker['total_calls']}")
    print(f"    Prompt Tokens: {_tracker['prompt_tokens']}")
    print(f"    Completion Tokens: {_tracker['completion_tokens']}")
    print(f"    总计 Tokens: {tokens}")
    print(f"    估算费用: ${_tracker['total_cost']:.6f}")


def main():
    task = "Python 3.12 有哪些新特性？这些特性对 AI 开发者有什么影响？"

    # 为了展示各策略差异，用一个实际有"陷阱"的问题：
    # 看起来简单，但需要搜索 + 推理 + 结构化回答，刚好能体现三种策略的区别

    print("=" * 65)
    print("   Planning 策略对比实验")
    print("=" * 65)
    print(f"\n测试任务：{task}")

    stats = {}

    # ── 1. ReAct ──
    reset_tracker()
    start = time.time()
    answer, traj = react_strategy(task)
    elapsed = time.time() - start
    stats["ReAct"] = {
        "answer": answer,
        "calls": _tracker["total_calls"],
        "tokens": _tracker["prompt_tokens"] + _tracker["completion_tokens"],
        "cost": _tracker["total_cost"],
        "time": elapsed,
    }

    # ── 2. Plan-and-Execute ──
    reset_tracker()
    start = time.time()
    answer, results = plan_and_execute_strategy(task)
    elapsed = time.time() - start
    stats["Plan-and-Execute"] = {
        "answer": answer,
        "calls": _tracker["total_calls"],
        "tokens": _tracker["prompt_tokens"] + _tracker["completion_tokens"],
        "cost": _tracker["total_cost"],
        "time": elapsed,
    }

    # ── 3. Reflexion ──
    reset_tracker()
    start = time.time()
    answer, traj = reflexion_strategy(task)
    elapsed = time.time() - start
    stats["Reflexion"] = {
        "answer": answer,
        "calls": _tracker["total_calls"],
        "tokens": _tracker["prompt_tokens"] + _tracker["completion_tokens"],
        "cost": _tracker["total_cost"],
        "time": elapsed,
    }

    # ── 对比报告 ──
    print("\n\n" + "=" * 65)
    print("   📊 对比报告")
    print("=" * 65)
    print(f"\n{'策略':<20} {'LLM调用':>8} {'Tokens':>10} {'费用(USD)':>12} {'耗时(秒)':>10}")
    print("-" * 65)

    # 找出最小值用于标注
    min_tokens = min(s["tokens"] for s in stats.values())
    min_cost = min(s["cost"] for s in stats.values())
    min_calls = min(s["calls"] for s in stats.values())
    min_time = min(s["time"] for s in stats.values())

    for name, s in stats.items():
        markers = []
        if s["tokens"] == min_tokens:
            markers.append("🏆最省Token")
        if s["cost"] == min_cost:
            markers.append("💰最省钱")
        if s["calls"] == min_calls:
            markers.append("⚡最少调用")
        if s["time"] == min_time:
            markers.append("🚀最快")
        marker_str = " ".join(markers)
        print(f"{name:<20} {s['calls']:>8} {s['tokens']:>10} ${s['cost']:.6f}  {s['time']:>8.1f}s  {marker_str}")

    print("\n" + "-" * 65)
    print("\n💡 结论：")
    print("  - ReAct 最通用灵活，是默认选择")
    print("  - Plan-and-Execute 在步骤明确、不需要动态调整时最省 Token")
    print("  - Reflexion 在质量要求高、可以接受多次重试时最有价值")
    print("  - 实际开发中应根据任务特征选择策略，而不是用最复杂的那个")
    print()

    # 打印各策略的最终回答（片段）
    for name, s in stats.items():
        print(f"\n── {name} 最终回答 ──")
        print(s["answer"][:200])


if __name__ == "__main__":
    main()

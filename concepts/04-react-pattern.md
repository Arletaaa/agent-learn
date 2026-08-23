# ReAct 范式（Reasoning + Acting）

---

**更新时间**：2026-07-22
**所属阶段**：阶段二 - 核心概念
**掌握程度**：🔵 理解

---

## 概念定义

ReAct（Reasoning + Acting）是 Yao 等人（2022）提出的一种 LLM 提示范式，**让模型以交错的方式生成"推理轨迹"和"任务特定动作"**，从而实现推理和行动的协同——推理帮助模型制定和调整计划，行动让模型与外部世界交互获取信息。

用一句话概括：**ReAct = Think → Act → Observe → Repeat**。

## 核心要点

1. **三个基本动作**：

   - **Thought（思考）**：分析当前状态，决定下一步做什么（拆解问题、推理、制定计划）
   - **Action（行动）**：执行一个具体操作（搜索、计算、调用 API）
   - **Observation（观察）**：接收外部环境返回的结果，注入下一轮思考
2. **为什么需要 ReAct？**：纯推理（CoT，Chain-of-Thought）只能靠 LLM 内部知识，会"编造事实"（幻觉）；纯行动（Act）只会机械执行，不会规划和调整。ReAct 把两者结合，让模型"边想边做、边做边想"。
3. **ReAct 的核心循环**：直到模型认为得到了最终答案才停止，否则持续 Thought → Action → Observation 循环。

## 工作原理

### 执行流程

```
用户提问
    ↓
┌─── 循环开始 ────────────────────────┐
│                                     │
│  Thought（思考）                     │
│  "我需要先搜索 XXX，然后..."          │
│        ↓                            │
│  Action（行动）                      │
│  Search["XXX"] / Calculator[...]    │
│        ↓                            │
│  Observation（观察）                 │
│  "搜索结果显示：..."                  │
│        ↓                            │
│  够回答了吗？── 否 ──→ 继续循环      │
│        │                            │
│        是                            │
│        ↓                            │
│  Final Answer（最终答案）            │
└─────────────────────────────────────┘
```

### 具体示例：回答一个问题

**问题**：科罗拉多造山带东部区域延伸到的区域的海拔范围是多少？

```
Thought 1: 我需要先搜索"科罗拉多造山带"，找到东部区域延伸到哪里
Action 1: Search[科罗拉多造山带]
Observation 1: 科罗拉多造山带是科罗拉多及其周边地区造山运动的一段。

Thought 2: 没提到东部区域，需要查"东部区域"
Action 2: Lookup[东部区域]
Observation 2: 东部区域延伸至高平原，称为中原造山带。

Thought 3: 东部区域延伸到高平原，需要搜索高平原的海拔范围
Action 3: Search[高平原]
Observation 3: 高平原指两个不同的陆地地区...

Thought 4: 不够精确，改搜"高平原（美国）"
Action 4: Search[高平原（美国）]
Observation 4: 从东到西，海拔从 1800 到 7000 英尺不等。

Thought 5: 已经有答案了，海拔范围是 1800 到 7000 英尺
Action 5: Finish[1800 到 7000 英尺]
```

可以看到：每一步思考引导行动，每一次观察修正思考——推理和行动交替进行。

## ReAct vs CoT vs Act

| 维度             | CoT（思维链）        | Act（纯行动）        | ReAct（推理+行动）            |
| ---------------- | -------------------- | -------------------- | ----------------------------- |
| 能推理吗？       | ✅ 能拆解问题        | ❌ 不推理            | ✅ 结合行动推理               |
| 能查外部信息吗？ | ❌ 只能靠内部知识    | ✅ 能调用工具        | ✅ 能调用工具                 |
| 最大问题         | 事实幻觉（编造答案） | 不会规划（机械执行） | 搜索失败时难以恢复            |
| 适用场景         | 数学、逻辑推理       | 简单工具调用         | 需要外部知识 + 推理的复杂任务 |

**最佳实践**：论文发现 **ReAct + CoT + Self-Consistency** 的组合效果最好——先用 ReAct 获取外部信息，再用 CoT 推理，多次采样取一致结果。

## 代码示例

### 简化版 ReAct 循环（Python 伪代码）

```python
def react_loop(user_question, max_steps=10):
    """ReAct 范式的最简实现"""
  
    messages = [{"role": "user", "content": user_question}]
    tools = {
        "search": lambda q: f"搜索结果：关于'{q}'的信息...",
        "calculator": lambda expr: f"计算 {expr} = {eval(expr)}",
    }
  
    for step in range(max_steps):
        # 1. Think：让 LLM 生成"思考"和"行动"
        response = llm(messages, tools_definition=tools)
      
        thought = response.get("thought")
        action = response.get("action")
      
        print(f"Step {step+1} - Thought: {thought}")
      
        if action is None or response.get("is_final"):
            # 给出最终答案，结束
            print(f"Final Answer: {response.get('answer')}")
            break
      
        # 2. Act：执行工具
        tool_name = action["name"]
        tool_input = action["input"]
        observation = tools[tool_name](tool_input)
      
        print(f"Step {step+1} - Action: {tool_name}({tool_input})")
        print(f"Step {step+1} - Observation: {observation}")
      
        # 3. Observe：将结果注入上下文，继续循环
        messages.append({"role": "assistant", "content": f"Thought: {thought}\nAction: {tool_name}({tool_input})"})
        messages.append({"role": "system", "content": f"Observation: {observation}"})
```

### LangChain ReAct Agent 使用

```python
from langchain.agents import load_tools, initialize_agent
from langchain.llms import OpenAI

llm = OpenAI(temperature=0)
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# "zero-shot-react-description" 就是 ReAct 模式
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

agent.run("2024 年诺贝尔物理学奖得主是谁？他今年多大？")
# Agent 会自动执行：
# Thought → Action(搜索获奖者) → Observation(结果)
# Thought → Action(搜索年龄) → Observation(结果)
# Thought → Final Answer
```

## 与其他概念的关系

- 前置概念：CoT（Chain-of-Thought，纯推理链）、Function Calling
- 后置概念：Reflexion（带自我反思的 ReAct 增强版）、Multi-Agent 协作
- 相关概念：Harness Engineering（ReAct 定义了 Agent Loop 的基本范式）、Planning 策略（Plan-and-Execute 是 ReAct 的变体）

## 常见误区

- **误区一："ReAct 只是一个 Prompt 技巧"**：ReAct 不仅是提示模板，更是一套架构范式——定义了 Agent 的推理-行动-观察循环，是现代 AI Agent 的核心骨架。
- **误区二："ReAct 里每一步都必须有 Thought"**：论文发现，对于简单决策任务，Thought 可以稀疏使用（不必要每一步都写思考）。但在知识密集型任务中，详细的 Thought 对结果影响很大。
- **误区三："ReAct 只能做搜索问答"**：ReAct 是一个通用框架，可以适配任何需要推理+工具调用的场景——编程、游戏、购物、数据分析都可以。

## 参考资源

- [ReAct 论文 (arXiv)](https://arxiv.org/abs/2210.03629) — Yao et al., 2022
- [Prompt Engineering Guide 中文版 - ReAct](https://www.promptingguide.ai/zh/techniques/react) — 中文 ReAct 教程
- [LangChain ReAct Agent 文档](https://python.langchain.com/docs/modules/agents/agent_types/react) — 官方 ReAct 使用指南
- [ReAct 项目网站](https://react-lm.github.io) — 论文代码和 Demo

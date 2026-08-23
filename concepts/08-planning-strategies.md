# Planning 策略对比

---

**更新时间**：2026-08-01
**所属阶段**：阶段二 - 核心概念
**掌握程度**：🔵 理解

---

## 概念定义

Planning 策略是 Agent 在执行任务时"如何规划行动步骤"的方案。不同的策略决定了 Agent 是先想好再做、还是边想边做、做错了要不要回头改。核心问题是：**在有限的信息和 Token 预算下，如何最大化任务成功率？**

## 核心策略总览

| 策略                       | 一句话概括                           | 规划方式           | 执行方式       | Token 消耗              | 容错能力               |
| -------------------------- | ------------------------------------ | ------------------ | -------------- | ----------------------- | ---------------------- |
| **ReAct**            | 边想边做，交替进行                   | 每步一个 Thought   | 顺序执行       | 高（每步都要 LLM 调用） | 中（能中途调整）       |
| **Plan-and-Execute** | 先列完整计划，再逐步执行             | 一次性生成完整计划 | 顺序执行       | 中                      | 低（计划错了只能重来） |
| **Reflexion**        | 做错了就反思，再来一遍               | 执行后评估反思     | 重试循环       | 很高（反复重试）        | 高（自我修正）         |
| **ReWOO**            | 先列出所有需要的工具调用，再批量执行 | 一次性规划工具链   | 并行执行独立步 | 低                      | 低                     |
| **Tree of Thoughts** | 多路径探索，选最优路径               | 树形分叉探索       | BFS/DFS + 剪枝 | 极高（指数级）          | 高（可回溯）           |

---

## 一、ReAct（基准线，已掌握）

参见 [04 - ReAct 范式](./04-react-pattern.md)。作为所有 Planning 策略的基准，ReAct 的核心特征是 **Think → Act → Observe 的紧密循环**。每步都要等上一步的观察结果才能决定下一步，因此：

- **优点**：灵活，能动态调整计划
- **缺点**：Token 消耗大（每步一次 LLM 调用），无并行化，容易在错误路径上越走越远

---

## 二、Plan-and-Execute（先规划，后执行）

### 核心思想

Agent 在收到任务后，**先用一次 LLM 调用生成一个完整的步骤计划（Plan）**，然后按顺序逐步执行每个步骤。这相当于把 ReAct 的"Thinking"从每一步中剥离出来，集中到开头一次性完成。

### 执行流程

```
用户任务："比较 Python 和 Rust 在 Web 后端领域的生态"

┌── 规划阶段（1 次 LLM 调用） ──────────────┐
│                                           │
│  Step 1: 搜索 "Python web framework 2024" │
│  Step 2: 搜索 "Rust web framework 2024"   │
│  Step 3: 对比 Step 1 和 Step 2 的结果，    │
│          从性能、生态、学习曲线三个方面总结  │
│                                           │
└───────────────────────────────────────────┘
     ↓
┌── 执行阶段（逐步执行） ────────────────────┐
│                                           │
│  → 执行 Step 1: 搜索 → 获得结果 A          │
│  → 执行 Step 2: 搜索 → 获得结果 B          │
│  → 执行 Step 3: 使用 LLM 对比 A 和 B       │
│     → 输出最终答案                         │
│                                           │
└───────────────────────────────────────────┘
```

### 伪代码

```python
def plan_and_execute(task: str, tools: dict, llm):
    # 第一步：生成计划
    plan_prompt = f"""
    为以下任务制定一个逐步执行计划，每步以一个具体行动描述：

    任务：{task}

    可用工具：{list(tools.keys())}

    输出格式（JSON）：
    {{"steps": [{{"step": 1, "description": "...", "tool": "tool_name", "input": "..."}}, ...]}}
    """

    plan = llm(plan_prompt)  # 1 次 LLM 调用
    steps = parse_json(plan)["steps"]

    # 第二步：逐步执行
    context = []
    results = {}

    for step in steps:
        tool_name = step["tool"]
        tool_input = step["input"]
        observation = tools[tool_name](tool_input)
        results[f"step_{step['step']}"] = observation
        context.append(f"Step {step['step']} ({step['description']}): {observation}")

    # 第三步：综合所有结果
    final_prompt = f"""
    任务：{task}

    执行过程：
    {chr(10).join(context)}

    请基于以上执行结果，给出最终答案。
    """

    return llm(final_prompt)  # 1 次 LLM 调用（总计 2 次）
```

### 优缺点

| 优点                             | 缺点                                     |
| -------------------------------- | ---------------------------------------- |
| LLM 调用次数少（2 次即可）       | 计划一旦制定就无法根据中间结果调整       |
| 适合确定性任务（已知步骤的任务） | 搜索类任务中，第一步结果可能改变后续步骤 |
| Token 消耗远低于 ReAct           | 如果计划本身错误，全部执行结果都作废     |

### 改进变体：Plan-and-Solve

在 Plan-and-Execute 基础上增加一个 **"重新规划"步骤**：如果执行到某一步发现结果不符合预期，触发一次 Replan 调用重新生成剩余计划。

---

## 三、Reflexion（自我反思）

### 核心思想

Reflexion 给 Agent 增加了一个"自我反思"机制。Agent 执行完一个完整的任务后，**由 Evaluator 判断结果是否合格**；如果不合格，**生成一段"反思文本"注入上下文**，然后 Agent 重新执行。循环直到通过评估或达到最大重试次数。

这是一个 **"事后反思"** 模式，不是实时调整。

### 三个核心角色

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│   Actor（执行者）  →  执行任务，产生结果              │
│       ↓                                              │
│   Evaluator（评估者）→  判分：结果合格吗？           │
│       ↓ (不合格)                                     │
│   Self-Reflection（反思者）→  分析失败原因，生成经验  │
│       ↓                                              │
│   将反思注入 Actor 的上下文 →  Actor 重新执行         │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 执行流程

```
尝试 1:
  Actor 执行任务 → 结果 X
  Evaluator: "结果 X 不完整，缺少第二部分" → 不合格
  Self-Reflection: "第一次尝试遗漏了...原因是搜索关键词不够精确"
  
  → 将反思文本追加到 Actor 的 memory 中

尝试 2:
  Actor（已包含反思）执行任务 → 结果 Y
  Evaluator: "结果 Y 完整且正确" → 合格
  → 返回结果 Y
```

### 伪代码

```python
def reflexion(task: str, tools: dict, llm, max_attempts=3):
    memory = []  # 反思经验积累

    for attempt in range(max_attempts):
        # Actor: 执行任务（使用 react 或 plan-execute 均可）
        result = actor_execute(task, tools, llm, memory)

        # Evaluator: 评估结果
        eval_prompt = f"""
        评估以下回答是否完整正确地回答了问题：

        问题：{task}
        回答：{result}

        如果回答正确，回复 "PASS"。
        如果不正确，回复 "FAIL: <原因>"
        """
        evaluation = llm(eval_prompt)

        if evaluation.startswith("PASS"):
            return result

        # Self-Reflection: 分析失败原因
        reflect_prompt = f"""
        你执行以下任务时失败了：

        任务：{task}
        你的回答：{result}
        失败原因：{evaluation}

        请反思：
        1. 哪里出错了？
        2. 下次应该如何改进？
        """
        reflection = llm(reflect_prompt)
        memory.append(reflection)

    return result  # 最终尝试的结果
```

### 优缺点

| 优点                                    | 缺点                                   |
| --------------------------------------- | -------------------------------------- |
| 能自我修正，适合需要反复优化的任务      | Token 消耗极高（每次重试都是完整执行） |
| 反思经验可跨任务复用（持久化记忆）      | 评估标准难以量化，依赖 LLM 自身判断    |
| 不依赖特定框架，可与任意 Agent 模式组合 | 如果反思本身也错误，可能越改越差       |

### 典型应用

- 代码生成与调试（生成代码 → 运行测试 → 失败 → 反思 → 修复）
- 写作与编辑（生成草稿 → 自我审阅 → 修改）
- 推理任务（HumanEval、HotpotQA 等基准测试）

---

## 四、ReWOO（Reasoning WithOut Observation）

### 核心思想

ReAct 每次工具调用后都要让 LLM"思考"下一步做什么，这很浪费 Token——因为很多时候工具调用的依赖关系是预先可以确定的。ReWOO 的做法是：**先让 LLM 规划出所有需要的工具调用和它们之间的变量依赖关系，然后批量并行执行，最后一次性综合结果**。

### 为什么 ReAct 浪费 Token？

ReAct 的世界里，Agent 至少有 3 次 LLM 调用：

```
Task → Plan → Tool1 → LLM思考 → Tool2 → LLM思考 → ... → Final
```

但实际上很多思考是多余的。比如查询"A 公司和 B 公司的市值差"，显然需要：

1. 查 A 市值
2. 查 B 市值
3. 相减

步骤 1 和步骤 2 完全独立，不需要等一个结果出来再决定第二个。

ReWOO 把上述过程压缩为：**1 次规划 + 批量执行 + 1 次综合 = 2 次 LLM 调用**。

### 执行流程

```
用户任务："对比 Python 和 Rust 在 Web 后端领域的生态"

   Planner（规划器，1 次 LLM 调用）
   ↓
   生成计划（带变量依赖）：
   
   #E1 = Google["Python web framework ecosystem 2024"]
   #E2 = Google["Rust web framework ecosystem 2024"]
   #E3 = LLM["从性能、生态、学习曲线三个维度对比 #E1 和 #E2"]
   
   ↓
   Worker（执行器，并行执行独立步骤）
   ↓
   Step 1 和 Step 2 并行执行（互相独立）
   Step 3 等 Step 1、2 完成后执行（依赖 #E1 和 #E2）
   
   ↓
   Solver（综合器，1 次 LLM 调用）
   ↓
   基于 #E3 的结果生成最终答案
```

### 伪代码

```python
def rewoo(task: str, tools: dict, llm):
    # Step 1: Planner 生成带变量的工具调用计划
    planner_prompt = f"""
    任务：{task}
    可用工具：{list(tools.keys())}

    请生成一个执行计划，使用 #E1, #E2, ... 作为变量名引用上一步结果。
    独立步骤用不同的变量名，有依赖的步骤引用前面变量的变量名。

    格式：
    Plan: 步骤说明
    #E1 = ToolName[input]
    #E2 = ToolName[input]
    #E3 = LLM["基于 #E1 和 #E2 的结果，做 XXX"]
    """

    plan = llm(planner_prompt)  # 1 次 LLM 调用

    # Step 2: 解析计划，构建依赖图并执行
    steps = parse_plan(plan)  # 解析出变量赋值
    results = {}
    for var_name, tool_name, tool_input in steps:
        # 替换输入中的变量引用（如 "#E1" → 实际值）
        resolved_input = resolve_variables(tool_input, results)
        if tool_name == "LLM":
            results[var_name] = llm(resolved_input)
        else:
            results[var_name] = tools[tool_name](resolved_input)

    # Step 3: Solver 综合结果（如果有 LLM 步骤则已包含）
    return results  # 或进一步用 LLM 格式化
```

### 优缺点

| 优点                               | 缺点                                  |
| ---------------------------------- | ------------------------------------- |
| Token 消耗极低（仅 2 次 LLM 调用） | 无法处理"结果决定下一步"的动态任务    |
| 独立步骤可并行执行，延迟低         | 计划中的依赖关系可能不准确            |
| 变量引用机制使数据流可追踪         | 要求 Planner 一次性生成准确的完整计划 |

---

## 五、Tree of Thoughts（思维树）

### 核心思想

人类解决复杂问题时，经常在脑海中模拟多个方案、比较优劣、回溯到之前的岔路口。ToT 把这个过程形式化：**在每个推理步骤，让 LLM 生成多个可能的"下一步"，然后评估每个分支的价值，选择最有希望的方向继续探索**。

### 四个关键组件

1. **Thought Generator**：给定当前状态，生成 K 个候选的下一步思考
2. **State Evaluator**：给每个候选思考打分（0~1 或 1~10）
3. **Search Algorithm**：BFS（广度优先，每层保留 Top-N）或 DFS（深度优先，回溯）
4. **Termination Condition**：找到满意解 or 搜索预算耗尽

### 执行示意

```
                    问题：24 点游戏 [4, 9, 10, 13]

                    当前状态: 4 9 10 13
                   /        |        \
         4+9=13         4*9=36        10-4=6
      剩[13,10,13]   剩[36,10,13]  剩[6,9,13]
         /   \           /   \         /   \
    13+13=26  ...    36-10=26  ...  6*9=54  ...
    (剪枝)           (剪枝)           (继续)

                    10-4=6 → 13-9=4 → 6*4=24 ✅
```

### 伪代码

```python
def tree_of_thoughts(problem: str, llm, max_depth=5, branching_factor=3, beam_width=2):
    root = State(problem, [])
    beam = [root]  # 当前层保留的状态

    for depth in range(max_depth):
        candidates = []

        for state in beam:
            # 1. 生成 K 个候选的下一步思考
            thoughts = generate_candidates(state, llm, k=branching_factor)

            for thought in thoughts:
                new_state = state.apply(thought)

                # 2. 评估每个候选
                score = evaluate(new_state, llm)
                candidates.append((new_state, score))

                # 3. 检查是否找到解
                if is_solution(new_state):
                    return new_state

        # 4. 保留 Top-N 进入下一层（Beam Search）
        candidates.sort(key=lambda x: x[1], reverse=True)
        beam = [s for s, _ in candidates[:beam_width]]

    return best_of(beam)  # 返回最优的未完成方案

def generate_candidates(state, llm, k):
    """让 LLM 为当前状态生成 K 个可能的下一步"""
    prompt = f"""
    当前问题：{state.problem}
    当前推理路径：{state.path}
  
    请生成 {k} 个不同的下一步推理方案，每个方案单独一行。
    """
    response = llm(prompt)
    return parse_thoughts(response, k)

def evaluate(state, llm):
    """让 LLM 评估一个状态的价值（sure/maybe/impossible）"""
    prompt = f"""
    评估以下推理路径是否可行，给出评分（1-10）：

    问题：{state.problem}
    路径：{state.path}

    评分标准：10=确定可行，1=完全不可行
    """
    return int(llm(prompt))
```

### 优缺点

| 优点                             | 缺点                                |
| -------------------------------- | ----------------------------------- |
| 能找到最优解（而非第一个可行解） | Token 消耗极高（指数级 LLM 调用）   |
| 可回溯，不会被错误路径卡住       | 评估 LLM 本身可能不准，导致错误剪枝 |
| 适合需要搜索/规划/博弈的复杂任务 | 简单任务上杀鸡用牛刀                |

### 典型应用

- 24 点游戏、填字游戏等需要搜索的任务
- 创意写作（多方案头脑风暴，选最佳）
- 数学证明（多路径探索）
- 代码生成（生成多个实现方案，测试后选最优）

---

## 六、策略选择决策树

面对一个新任务，如何选择 Planning 策略？

```
任务分析
    │
    ├── 步骤之间依赖关系明确？
    │   ├── 是 → 所有步骤可预先知道？
    │   │   ├── 是 → ReWOO（Token 最省）
    │   │   └── 否 → Plan-and-Execute
    │   │
    │   └── 否 → 需要边做边看？
    │       ├── 需要多次试错优化？
    │       │   ├── 是 → Reflexion
    │       │   └── 否 → ReAct
    │       │
    │       └── 需要找最优解（非首个可行解）？
    │           └── 是 → Tree of Thoughts
    │
    └── 综合建议：
        - 日常通用 → ReAct（最稳妥）
        - Token 敏感 → ReWOO
        - 质量要求高 → Reflexion
        - 确定性任务 → Plan-and-Execute
        - 复杂搜索 → Tree of Thoughts
```

---

## 七、核心对比表

| 维度         | ReAct      | Plan-Execute | Reflexion    | ReWOO          | ToT       |
| ------------ | ---------- | ------------ | ------------ | -------------- | --------- |
| LLM 调用次数 | N~10       | 2~4          | N×重试次数  | 2              | 指数级    |
| 并行能力     | 无         | 无           | 无           | 有             | 部分      |
| 动态调整     | 强         | 弱           | 强（事后）   | 极弱           | 强        |
| 自我修正     | 弱         | 弱           | 强           | 无             | 中        |
| 最佳场景     | 探索性任务 | 流程化任务   | 质量敏感任务 | Token 敏感任务 | 搜索/博弈 |
| 实现难度     | 低         | 低           | 中           | 中             | 高        |

---

## 与其他概念的关系

- **前置概念**：[ReAct 范式](./04-react-pattern.md) — 所有 Planning 策略的基础和对比基准
- **后置概念**：Multi-Agent 协作 — 多 Agent 系统通常会在单个 Agent 内部使用某种 Planning 策略
- **相关概念**：
  - [Agent Memory](./06-agent-memory.md) — Reflexion 的反思结果就是一种长期记忆
  - [Function Calling](./05-function-calling.md) — 所有策略都依赖工具调用能力
  - LangGraph — 状态图编排可以在框架层面实现这些策略

## 常见误区

- **误区一："Planning 策略越复杂越好"**：实际业务中，简单的 ReAct 或 Plan-and-Execute 足以解决大部分问题。ToT 和 Reflexion 的 Token 成本往往是 ReAct 的 5~10 倍，只在特定场景值得。
- **误区二："ReWOO 比 ReAct 好，因为 Token 更省"**：ReWOO 省 Token 的前提是计划必须正确。如果 Planner 生成的计划有误，ReWOO 无法中途纠正，而 ReAct 可以。两者是 Trade-off，不是替代关系。
- **误区三："Reflexion 就是让 LLM 多想想"**：Reflexion 的关键不是多想，而是把反思结果持久化存储，让后续任务也能受益。这是一种"learning from mistakes"机制，类似人类的经验积累。

## 参考资源

- [ReAct 论文](https://arxiv.org/abs/2210.03629) — Yao et al., 2022 — 基准策略
- [Plan-and-Solve 论文](https://arxiv.org/abs/2305.04091) — Wang et al., 2023 — Plan-and-Execute 改进版
- [Reflexion 论文](https://arxiv.org/abs/2303.11366) — Shinn et al., 2023 — 自我反思 Agent
- [ReWOO 论文](https://arxiv.org/abs/2305.18323) — Xu et al., 2023 — 去观察化的高效推理
- [Tree of Thoughts 论文](https://arxiv.org/abs/2305.10601) — Yao et al., 2023 — 思维树搜索
- [LangGraph Planning Agent 示例](https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/plan-and-execute/) — 官方 Plan-and-Execute 实现

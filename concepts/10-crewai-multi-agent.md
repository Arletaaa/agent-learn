# CrewAI 多 Agent 协作

---

**更新时间**：2026-08-05
**所属阶段**：阶段三 - 主流框架
**掌握程度**：🔵 理解

---

## 概念定义

CrewAI 是一个**多 Agent 协作编排框架**，让你像管理一个团队一样管理 AI Agent。每个 Agent 有明确的角色（Role）、目标（Goal）和背景（Backstory），由 Crew 统一调度执行。

一句话：**CrewAI = 你定义"谁做什么"，框架负责"怎么配合"**。

## 为什么需要多 Agent？

单 Agent 的瓶颈：
- 一个 Agent 很难同时精通多个领域（搜索 + 分析 + 写作）
- 复杂任务天然需要分工协作（市场调研 → 策略制定 → 报告撰写）
- 多个视角能相互校验，减少单点错误

CrewAI 的核心思想：**按人类组织的分工方式设计 Agent 团队**——有研究员、分析师、写作者、审核员。

## 核心概念

### 1. Agent（智能体）—— "团队成员"

每个 Agent 定义三个要素：

```python
from crewai import Agent

researcher = Agent(
    role="资深技术研究员",
    goal="全面收集指定技术领域的相关资料，覆盖最新进展和行业趋势",
    backstory="你是一位拥有十年经验的技术研究员，擅长从多维度收集和归纳信息",
    tools=[search_tool],
    verbose=True,
)
```

| 属性 | 含义 | 为什么重要 |
|------|------|-----------|
| `role` | 角色名称 | 给 LLM 一个明确的身份定位 |
| `goal` | 核心目标 | Agent 的"KPI"，决定行为方向 |
| `backstory` | 背景故事 | 补充上下文，提升回答质量（相当于 System Prompt 的自然语言版） |
| `tools` | 可用工具列表 | Agent 的能力边界 |
| `verbose` | 是否打印日志 | 调试时观察内部推理 |

### 2. Task（任务）—— "要做什么"

```python
from crewai import Task

research_task = Task(
    description="搜索并总结 2024 年 AI Agent 框架的最新进展，包括 LangGraph、CrewAI、AutoGen 的对比",
    expected_output="一份包含 3 个框架的技术对比表格和 300 字总结的 Markdown 文档",
    agent=researcher,
)
```

| 属性 | 含义 |
|------|------|
| `description` | 任务描述 |
| `expected_output` | 期望输出格式（约束 LLM 的回答结构） |
| `agent` | 分配给哪个 Agent |
| `context` | 依赖的前置任务结果（可选） |

### 3. Crew（团队）—— "怎么协作"

```python
from crewai import Crew, Process

crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, writing_task, review_task],
    process=Process.sequential,  # 或 Process.hierarchical
    verbose=True,
)
result = crew.kickoff()
```

**两种协作模式：**

| 模式 | 执行方式 | 适用场景 |
|------|---------|---------|
| `Process.sequential` | 按 Task 顺序逐个执行 | 流水线型任务 |
| `Process.hierarchical` | 指定一个 Manager Agent 分配任务 | 动态决策型任务 |

### 4. Task 依赖（Context 传递）

任务之间通过 `context` 传递结果：

```python
research_task = Task(description="调研 XXX", agent=researcher)
writing_task = Task(
    description="基于调研结果写报告",
    agent=writer,
    context=[research_task],  # writer 能看到 researcher 的结果
)
```

这样 CrewAI 会自动把前一个 Task 的输出注入后一个 Task 的 Prompt。

## 代码示例：最小多 Agent 团队

```python
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# 共同 LLM
llm = ChatOpenAI(model="deepseek-chat", base_url="https://api.deepseek.com")

# Agent 1：研究员
researcher = Agent(
    role="研究员",
    goal="调研 LangGraph 和 CrewAI 的优劣势",
    backstory="你是技术调研专家",
    llm=llm,
    allow_delegation=False,
)

# Agent 2：写作者
writer = Agent(
    role="技术作者",
    goal="用清晰的对比表展示两个框架的差异",
    backstory="擅长将复杂技术信息转化为易读文档",
    llm=llm,
    allow_delegation=False,
)

# Task 1
task1 = Task(
    description="对比 LangGraph 和 CrewAI 的架构设计、适用场景和学习曲线",
    expected_output="分三个维度的详细分析",
    agent=researcher,
)

# Task 2（依赖 Task 1）
task2 = Task(
    description="基于调研结果，生成一个 Markdown 对比表",
    expected_output="包含对比表格和推荐结论的 Markdown 文档",
    agent=writer,
    context=[task1],
)

# 组建团队并执行
crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process=Process.sequential)
result = crew.kickoff()
```

## 执行流程（Sequential 模式）

```
用户触发 kickoff()
    │
    ↓
┌─────────────────────────────────────────────────┐
│                                                  │
│  Task 1: 研究员执行调研                          │
│    ├── Agent: 研究员                             │
│    ├── LLM 推理 → 需要搜索？→ 调用 search 工具    │
│    └── 输出：调研结果（TechnicalReport）           │
│                                                  │
│  Task 2: 写作者基于上下文生成文档                  │
│    ├── Agent: 写作者                             │
│    ├── Context: Task 1 的调研结果自动注入 Prompt  │
│    └── 输出：对比表 Markdown                       │
│                                                  │
└─────────────────────────────────────────────────┘
    │
    ↓
最终输出（Task 2 的结果）
```

## CrewAI vs LangGraph：选型指南

| 维度 | CrewAI | LangGraph |
|------|--------|-----------|
| 抽象层次 | 高（角色扮演、自然语言定义） | 低（节点/边/状态直接定义） |
| 学习曲线 | 低，10 分钟上手 | 中，需要理解图论概念 |
| 适合场景 | 分工明确的多人协作任务 | 需要精确控制执行的单/多 Agent |
| 灵活性 | 受限于框架规范 | 完全自由 |
| 底层机制 | 每个 Agent 内部是一个 ReAct 循环 | 显式的图——可自定义任意流程 |
| 并行执行 | 有限（Task 级别的依赖管理） | 完善（Send API + 条件边） |
| 人机协作 | 有限 | 完善（interrupt_before/after） |
| 典型用例 | 内容创作流水线、市场研究 | 自定义 Agent 循环、复杂状态机 |

**选择原则：**

```
你的任务像"流水线"吗？
  └── 是 → CrewAI（研究员→写作者→审核员，天然就是顺序的）
  └── 否 → 你的任务有复杂的分支/循环/回溯吗？
      └── 是 → LangGraph
      └── 否 → 单 Agent 够用吗？
          └── 是 → 直接用 LangChain Agent 或纯 LLM
          └── 否 → CrewAI
```

## 内部机制：每个 Agent 就是一个 ReAct Loop

CrewAI 的 Agent 内部执行流程本质上是完整的 ReAct：

```
Agent 收到 Task
    ↓
System Prompt = Role + Goal + Backstory + Task Description
    ↓
┌─ ReAct Loop ────────────────────────┐
│  Thought → Action → Observation     │
│  Thought → Action → Observation     │
│  ...                                │
└─────────────────────────────────────┘
    ↓
输出结果 → 传递给下一个 Task（作为 Context）
```

CrewAI 的创新不在于 Agent 内部的推理机制（它复用了 ReAct），而在于：
1. **Agent 角色的自然语言定义**（Role/Goal/Backstory → 自动生成 System Prompt）
2. **Task 的流水线编排**（依赖管理 + 结果传递）
3. **团队级别的调度**（Sequential / Hierarchical）

## 高级特性

### Hierarchical Process（层级式）

指定一个 Manager Agent 自动分配任务：

```python
crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[...],
    process=Process.hierarchical,
    manager_llm=llm,  # Manager 用哪个 LLM
)
```

Manager Agent 由 CrewAI 自动创建，它会根据 Agent 的 role/goal 动态分配 Task。

### Memory（记忆）

```python
crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True,  # 开启记忆
)
```

CrewAI 支持三种记忆：
- **Short-term memory**：单次 Crew 执行内的上下文
- **Long-term memory**：跨 Crew 执行的经验积累（持久化存储）
- **Entity memory**：关键实体的结构化信息

### Tools（工具）

```python
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

agent = Agent(
    role="研究员",
    tools=[SerperDevTool(), ScrapeWebsiteTool()],
)
```

除了 LangChain 工具，CrewAI 有自建的工具生态（`crewai_tools` 包）。

## 与其他概念的关系

- **前置概念**：[ReAct 范式](./04-react-pattern.md)（每个 Agent 内部就是一个 ReAct 循环）、[Function Calling](./05-function-calling.md)（工具调用是 Agent 能力的基础）、[LangGraph](./09-langgraph.md)（同样能实现多 Agent，但抽象层次不同）
- **后置概念**：AutoGen（微软的对话式多 Agent 框架，与 CrewAI 互补）、Multi-Agent 协作模式（CrewAI 本身就是多 Agent 协作的实现）
- **相关概念**：[Planning 策略](./08-planning-strategies.md)（Crew 级别的 Sequential 就是一种 Plan-and-Execute）

## 常见误区

- **误区一："CrewAI 的 Agent 是真多人格 LLM"**：底层是同一个 LLM（或不同实例）被不同 System Prompt 驱动。不是多个独立的大脑，而是同一个模型扮演多个角色。
- **误区二："Agent 越多越好"**：每个 Agent 都消耗 Token。一个 3 人的 Crew（研究员→写作者→审核员）通常已经足够。Agent 太多会导致信息传递衰减和 Token 浪费。
- **误区三："CrewAI 替代 LangGraph"**：两者是不同抽象层次——CrewAI 适合"定义团队"式的高层编排，LangGraph 适合"定义流程"式的底层控制。实际项目中可以组合使用。

## 参考资源

- [CrewAI 官方文档](https://docs.crewai.com/) — 完整指南
- [CrewAI GitHub](https://github.com/crewaiInc/crewAI) — 源码
- [CrewAI 入门教程](https://docs.crewai.com/introduction) — 官方起步教程
- [CrewAI Tools 文档](https://docs.crewai.com/tools/) — 工具生态
- [Multi-Agent 协作模式论文综述](https://arxiv.org/abs/2308.10848) — 学术背景

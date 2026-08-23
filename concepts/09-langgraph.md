# LangGraph 状态图编排

---

**更新时间**：2026-08-04
**所属阶段**：阶段三 - 主流框架
**掌握程度**：🔵 理解

---

## 概念定义

LangGraph 是 LangChain 生态中的**有状态图编排框架**，让你用**图的思维**来构建 Agent。与传统的链式调用（Chain）不同，图可以包含循环、条件分支和并行路径——这正是 Agent 循环所需要的。

一句话：**LangGraph = 把 Agent 的执行流程建模成一个 StateGraph（状态图）**。

## 为什么需要 LangGraph？

传统的 LangChain Chain 是一条直线：

```
输入 → LLM → 工具调用 → 输出
```

但实际的 Agent 不是直线：

```
输入 → LLM → 需要工具？──是→ 执行工具 → 返回 LLM
                     │                        │
                     否                        │
                     ↓                        │
                   输出  ←─────────────────────┘
```

这里有**循环**和**条件分支**——Chain 做不到，Graph 可以。

## 核心概念

### 1. State（状态）

State 是图中所有节点共享的数据容器，用 TypedDict 或 Pydantic 模型定义：

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # 用 add_messages 做增量累加
    next_step: str                            # 控制下一步跳转
```

`add_messages` 是关键——它不是覆盖，而是**追加**，形成对话历史。

### 2. Nodes（节点）

每个节点是一个 Python 函数，接收当前 State，返回要更新的字段：

```python
def llm_node(state: AgentState) -> dict:
    """调用 LLM，返回结果"""
    response = llm.invoke(state["messages"])
    return {"messages": [response], "next_step": "decision"}  # 只返回要更新的字段

def tool_node(state: AgentState) -> dict:
    """执行工具调用"""
    last_message = state["messages"][-1]
    results = execute_tools(last_message.tool_calls)
    return {"messages": results, "next_step": "llm"}
```

### 3. Edges（边）

**普通边**：无条件跳转

```python
graph.add_edge("tool_node", "llm_node")  # 执行完工具后总是返回 LLM
```

**条件边**：根据 State 决定下一个节点

```python
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:      # LLM 想调用工具
        return "tool_node"
    return "__end__"                  # 对话结束

graph.add_conditional_edges(
    "llm_node",
    should_continue,                  # 决策函数
    {"tool_node": "tool_node", "__end__": "__end__"}  # 返回值 → 节点映射表
)
```

### 4. Graph 构建流程

```python
from langgraph.graph import StateGraph, MessagesState, START, END

# 1. 定义 State
class MyState(TypedDict):
    messages: Annotated[list, add_messages]

# 2. 创建 Graph
graph = StateGraph(MyState)

# 3. 添加节点
graph.add_node("agent", llm_node)        # LLM 推理节点
graph.add_node("tools", tool_node)       # 工具执行节点

# 4. 添加边
graph.add_edge(START, "agent")           # 入口 → agent
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")         # 工具 → 回到 agent

# 5. 编译（冻结为可运行的 app）
app = graph.compile()
```

## Agent 循环的核心拓扑

```
        ┌──────────────────────────────┐
        │                              │
        ↓                              │
    ┌───────┐    tool_calls?    ┌──────┴──┐
    │ agent │ ────────────────→  │  tools  │
    │ (LLM) │                    │         │
    └───┬───┘                    └────────┘
        │ 无 tool_calls
        ↓
     ┌─────┐
     │ END │
     └─────┘
```

这就是经典的 Agent Loop 在图中的表达。

## 进阶特性

### Checkpointing（状态持久化）

每次 state 更新后自动保存快照，支持：

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# 运行时需要 thread_id
config = {"configurable": {"thread_id": "user-123"}}
app.invoke({"messages": [HumanMessage(content="你好")]}, config)

# 同一 thread_id 的后续调用会从上次状态继续（记忆保持）
app.invoke({"messages": [HumanMessage(content="我刚才问了什么？")]}, config)

# 查看历史
for snapshot in app.get_state_history(config):
    print(snapshot)
```

关键点：`thread_id` 就是会话 ID，同一 thread_id 共享状态。这比手动管理 messages 列表高级得多。

### Human-in-the-Loop（人机协作）

在执行到某个节点前暂停，等待人工确认：

```python
# 执行工具前暂停
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["tools"]  # 在进入 tools 节点前中断
)

# 正常调用
config = {"configurable": {"thread_id": "1"}}
result = app.invoke({"messages": [...]}, config)

# 如果被中断，result 就是一个 Interrupt
# 人工确认后继续
app.invoke(None, config)  # 传入 None 表示"批准继续"
```

### Streaming（流式输出）

```python
# 流式输出每个节点的结果
for output in app.stream({"messages": [...]}, config):
    for node_name, node_output in output.items():
        print(f"Node '{node_name}' 输出: {node_output}")
```

### Subgraphs（子图组合）

将一个 Graph 作为另一个 Graph 的节点——用于多 Agent 编排：

```python
research_agent = build_research_graph().compile()    # 子图
writer_agent = build_writer_graph().compile()         # 子图

main_graph = StateGraph(MainState)
main_graph.add_node("research", research_agent)       # 嵌套子图
main_graph.add_node("write", writer_agent)
main_graph.add_edge("research", "write")
```

## 代码示例：最小 Agent

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

# 1. 定义工具
search = DuckDuckGoSearchRun()
tools = [search]

# 2. 创建 LLM（绑定工具）
llm = ChatOpenAI(model="deepseek-chat", base_url="...")
llm_with_tools = llm.bind_tools(tools)

# 3. 定义节点函数
def agent(state: MessagesState):
    """Agent 节点：调用 LLM"""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: MessagesState) -> str:
    """条件边：判断是否需要调用工具"""
    last_msg = state["messages"][-1]
    if last_msg.tool_calls:
        return "tools"
    return "__end__"

# 4. 构建图
graph = StateGraph(MessagesState)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")

app = graph.compile(checkpointer=MemorySaver())

# 5. 运行
result = app.invoke(
    {"messages": ["今天深圳天气怎么样？"]},
    {"configurable": {"thread_id": "1"}}
)
```

## LangGraph vs LangChain Chain

| 维度              | LangChain Chain     | LangGraph            |
| ----------------- | ------------------- | -------------------- |
| 抽象模型          | 线性管道            | 有向图（节点+边）    |
| 循环支持          | ❌ 不支持           | ✅ 天然支持          |
| 条件分支          | 有限（RouterChain） | ✅ 任意条件边        |
| 状态管理          | 手动传递            | ✅ 自动注入 State    |
| 持久化            | 需自己实现          | ✅ 内置 Checkpointer |
| 流式输出          | callback            | ✅ stream() API      |
| Human-in-the-Loop | ❌                  | ✅ interrupt         |
| 并行执行          | ❌                  | ✅ Send API          |

### 本质区别：能不能"回头"

一句话概括：**LangChain 是"链"（DAG，只能往前），LangGraph 是"图"（Graph，可以循环）。**

**LangChain 的 Chain 是单向的**

```
输入 → A → B → C → 输出
```

数据只能朝一个方向流。哪怕最复杂的 `SequentialChain` 也只是把多条链拼起来，**本质上仍是一个有向无环图（DAG）**——数据永远不会回到已经走过的节点。

**LangGraph 的 Graph 是可以循环的**

```
输入 → A → B → C
            ↑   │
            └───┘   （循环回来了）
```

数据可以回到之前的节点，形成循环。这正是 Agent 最需要的：`LLM 想 → 调工具 → 拿到结果 → 再想 → 再调工具`。

### 为什么 Agent 一定要循环？

看一个真实 Agent 的执行：

```
用户问"今天深圳天气怎么样，适合跑步吗？"
  → LLM 思考：需要查天气
  → 调用 weather 工具
  → 拿到结果：晴天 25°C
  → LLM 再思考：25°C 适合跑步
  → 回答：适合
```

LLM 被调用了**两次**，中间夹着工具调用。在 LangChain 里你要么写 `while` 循环手动套 Chain（等于自己造轮子），要么用 `AgentExecutor`（LangChain 团队发现 Chain 不够用后打的补丁——内部是个死循环 while，难控制、难调试）。

**LangGraph 就是把这个"补丁"变成一等公民**：循环不再是 hack，而是图的天然能力。

### 它们不是竞品，是分工

关键点：**你可以在 LangGraph 里用 LangChain 的组件。**

```python
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI      # ← LangChain 的 LLM 组件
from langchain_community.tools import DuckDuckGoSearchRun  # ← LangChain 的工具

# 用 LangGraph 编排，用 LangChain 提供"积木"
graph.add_node("agent", agent_node)         # agent_node 里调 ChatOpenAI
graph.add_node("tools", ToolNode(tools))    # ToolNode 里调 LangChain 工具
```

分工：

- **LangChain**：提供组件（LLM 封装、工具、Prompt 模板、检索器）
- **LangGraph**：提供编排（状态、循环、分支、持久化）

类比：

- **LangChain = 工厂流水线**：零件从 A 传到 B 传到 C，永远不会传回 A。
- **LangGraph = 程序的控制流**：有 `for` 循环、`if` 分支、`while` 条件，状态不断更新。

> 一句话总结：LangChain 解决"用什么零件"，LangGraph 解决"零件怎么流动"；Agent 需要循环流动，所以 Agent 要用 LangGraph。二者不是二选一，**LangGraph 是 LangChain 团队推出的、替代 Chain 的下一代编排层**。

## 常见 Pattern 模板

LangGraph 内置了预制模板类，可以直接用：

```python
# 方法一：手写图（最大灵活性）
from langgraph.graph import StateGraph, MessagesState
# ... 完全手动定义节点和边

# 方法二：使用 create_react_agent（最快上手）
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(llm, tools, checkpointer=memory)

# 实际上 create_react_agent 内部就是一个 StateGraph：
# agent → [conditional] → tools → agent
```

## 与其他概念的关系

- **前置概念**：[ReAct 范式](./04-react-pattern.md)（LangGraph 的 Agent 循环就是 ReAct）、[Function Calling](./05-function-calling.md)（ToolNode 依赖 Function Calling）、[Planning 策略](./08-planning-strategies.md)（LangGraph 为实现任意策略提供了图基板）
- **后置概念**：CrewAI / AutoGen（更上层的多 Agent 框架，底层也可用 LangGraph）
- **相关概念**：LangChain（LangGraph 是 LangChain 的一部分）、Multi-Agent 协作（Subgraph 机制）

## 常见误区

- **误区一："LangGraph 必须用 LangChain 的 LLM"**：LangGraph 只负责编排，不限定 LLM 实现。直接用 openai SDK 的 LLM 也可以——只要实现了 invoke 方法。
- **误区二："图越大越好"**：图应该反映 Agent 的真实决策逻辑，不是画得越复杂越好。一个经典的 3 节点循环（agent → tools → agent）就能解决大部分问题。
- **误区三："LangGraph 只能做 Agent"**：实际上任何有状态的多步骤工作流都可以用 LangGraph——数据 ETL 管道、多阶段审核流程、游戏状态机等。

## 参考资源

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/) — 完整指南
- [LangGraph 教程集](https://langchain-ai.github.io/langgraph/tutorials/) — 从零到 Agent
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph) — 源码
- [LangGraph 概念指南](https://langchain-ai.github.io/langgraph/concepts/) — 核心概念详解
- [LangGraph 如何实现 Agent（视频）](https://www.youtube.com/watch?v=PdDPwSq0nGM) — LangChain 官方讲解

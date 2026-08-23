# AutoGen 对话式多 Agent

---

**更新时间**：2026-08-13
**所属阶段**：阶段三 - 主流框架
**掌握程度**：🔵 理解

---

## 概念定义

AutoGen 是微软开源的多 Agent 对话框架。它的核心理念是：**让多个 Agent 通过"对话"来协作解决问题**——而不是通过显式的流水线或图来编排。

一句话：**AutoGen = Agent 之间像同事一样开会讨论，直到问题解决。**

## 为什么用"对话"而非"流水线"？

CrewAI 和 LangGraph 的编排都是"预先规划好"的：

- CrewAI：研究员 → 分析师 → 写作者（顺序固定）
- LangGraph：agent → tools → agent（循环固定）

但真实的团队协作往往是**动态的**——谁发言、发言几次、什么时候该换人，都是临场决定的。

AutoGen 把协作建模成**多 Agent 对话**：
- 每个 Agent 都能"发言"（生成消息）
- 发言会广播给其他 Agent
- 任何 Agent 都能接话、追问、纠正
- 直到某个 Agent 说"完成了"，对话结束

## 核心概念

### 1. ConversableAgent（可对话 Agent，基类）

所有 Agent 的基类，核心能力是 `generate_reply()`——收到消息后生成回复：

```python
from autogen import ConversableAgent

agent = ConversableAgent(
    name="助手",
    system_message="你是一个乐于助人的 AI 助手",
    llm_config={"config_list": [{"model": "deepseek-chat", ...}]},
)
```

### 2. AssistantAgent（助手 Agent）

有 LLM 推理能力的 Agent，负责思考、分析、生成方案：

```python
from autogen import AssistantAgent

coder = AssistantAgent(
    name="程序员",
    system_message="你是一名资深 Python 工程师，擅长编写清晰正确的代码",
    llm_config=config,
)
```

### 3. UserProxyAgent（用户代理 Agent）

代表人类的 Agent，通常**能执行代码**。它是 AutoGen 的招牌特性：

```python
from autogen import UserProxyAgent

user_proxy = UserProxyAgent(
    name="用户",
    human_input_mode="NEVER",          # 不打断，全自动
    code_execution_config={"use_docker": False},  # 本地执行代码
)
```

`human_input_mode` 三种取值：
| 值 | 含义 |
|----|------|
| `"ALWAYS"` | 每次都要人工确认（Human-in-the-Loop） |
| `"TERMINATE"` | 只在结束时确认 |
| `"NEVER"` | 全自动，不打断 |

### 4. 双 Agent 对话（最小协作）

```python
import autogen

# 配置 LLM（DeepSeek 走 OpenAI 兼容接口）
config = {
    "config_list": [{
        "model": "deepseek-chat",
        "api_key": "...",
        "base_url": "https://api.deepseek.com/v1",
    }]
}

# 助手 Agent：负责写代码
assistant = AssistantAgent(
    name="assistant",
    system_message="你是一名 Python 专家，写出可运行的代码并解释",
    llm_config=config,
)

# 用户代理：负责执行代码并反馈结果
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False},
)

# 发起对话
user_proxy.initiate_chat(
    assistant,
    message="写一个函数，计算斐波那契数列前 10 项，并运行验证",
)
```

### 5. GroupChat（群聊模式）

多个 Agent（>2）参与的协作，由 GroupChatManager 管理：

```python
from autogen import GroupChat, GroupChatManager

groupchat = GroupChat(
    agents=[user_proxy, researcher, coder, reviewer],
    messages=[],                    # 聊天记录
    max_round=10,                   # 最多 10 轮
)

manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=config,             # Manager 决定"下一个该谁发言"
)

user_proxy.initiate_chat(manager, message="做一个数据分析项目...")
```

GroupChatManager 的职责：**每轮由 LLM 决定下一个发言的 Agent**（类似主持人）。

## 对话执行流程（双 Agent 代码任务）

```
user_proxy 发起任务："写个函数算斐波那契，并运行验证"
    │
    ↓
┌────────── 对话循环 ──────────┐
│                              │
│  assistant 发言：             │
│  "这是代码：                  │
│   ```python                  │
│   def fib(n): ...            │
│   ```                        │
│   "                          │
│        ↓                     │
│  user_proxy 发言：            │
│  执行代码 → 得到结果           │
│  "运行成功，输出 [0,1,1,...]" │
│        ↓                     │
│  assistant 发言：             │
│  "验证通过，代码正确..."       │
│        ↓                     │
│  发送 TERMINATE 信号          │
│                              │
└──────────────────────────────┘
```

关键点：**代码执行是闭环的**——assistant 写代码，user_proxy 执行，结果反馈给 assistant 修正。这就是 AutoGen 最强大的地方：代码 Agent 能自我验证。

## 与 CrewAI / LangGraph 对比

| 维度 | LangGraph | CrewAI | AutoGen |
|------|-----------|--------|---------|
| 编排范式 | 图（状态机） | 流水线（角色+任务） | 对话（自由发言） |
| 核心抽象 | State / Nodes / Edges | Agent / Task / Crew | ConversableAgent / GroupChat |
| 控制粒度 | 最细（显式控制流） | 中（任务级） | 最粗（靠对话涌现） |
| 代码执行 | 需自定义节点 | 有限 | ✅ 原生支持 |
| 动态性 | 低（预先定义） | 低（顺序固定） | 高（临场决定） |
| 可预测性 | 高 | 高 | 低（对话可能跑偏） |
| 适合场景 | 精确控制的 Agent | 分工明确的流水线 | 需要代码执行/自由协作 |
| 学习曲线 | 中 | 低 | 中 |

## 核心优势：代码执行闭环

这是 AutoGen 区别于其他框架的杀手锏：

```
程序员 Agent 写代码
    → 执行器 Agent 运行代码
    → 报错信息反馈给程序员
    → 程序员修正代码
    → 再执行
    → 直到通过
```

不需要人肉把报错贴回 ChatGPT，全自动闭环。这天然适合：
- 自动化脚本生成
- 数据分析任务（写 pandas 代码 → 执行 → 看结果 → 调整）
- 单元测试生成与修复

## 三种协作模式总结

| 模式 | 用法 | 比喻 |
|------|------|------|
| 双 Agent 对话 | `user_proxy.initiate_chat(assistant, ...)` | 一对一面谈 |
| GroupChat | `GroupChat(agents=[...], max_round=...)` | 团队开会 |
| Nested Chat | 对话中触发子对话 | 会中会（私下协商） |

## 与其他概念的关系

- **前置概念**：[ReAct 范式](./04-react-pattern.md)（单个 Agent 内部仍是推理+行动）、[CrewAI](./10-crewai-multi-agent.md)（同为多 Agent 框架，但编排范式不同）、[LangGraph](./09-langgraph.md)（同为编排层，抽象层次互补）
- **后置概念**：Multi-Agent 协作模式（AutoGen 的 GroupChat 就是一种协作模式）
- **相关概念**：[Function Calling](./05-function-calling.md)（Agent 间消息传递依赖它）、[Agent Memory](./06-agent-memory.md)（对话历史就是短期记忆）

## 常见误区

- **误区一："对话式 = 完全不可控"**：AutoGen 也有 `max_round`、`human_input_mode`、终止条件等控制手段，只是控制粒度比 LangGraph 粗。
- **误区二："AutoGen 只能写代码"**：代码执行是它的招牌，但也能做通用多 Agent 对话（调研、写作、审核）。
- **误区三："三个框架要选一个"**：它们解决不同层次的问题，可以混用。例如用 LangGraph 做底层状态机，用 AutoGen 的代码执行 Agent 做工具。

## 参考资源

- [AutoGen 官方文档](https://microsoft.github.io/autogen/) — 完整指南
- [AutoGen GitHub](https://github.com/microsoft/autogen) — 源码
- [AutoGen 入门教程](https://microsoft.github.io/autogen/docs/tutorial/introduction) — 官方起步
- [AutoGen 论文](https://arxiv.org/abs/2308.08155) — Wu et al., 2023

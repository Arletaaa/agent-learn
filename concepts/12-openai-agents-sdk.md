# OpenAI Agents SDK

---

**更新时间**：2026-08-15
**所属阶段**：阶段三 - 主流框架
**掌握程度**：🔵 理解

---

## 概念定义

OpenAI Agents SDK 是 OpenAI 官方发布的轻量级 Agent 框架，前身是实验性项目 Swarm。它围绕一个核心思想设计：**Agent 是"带指令和工具的 LLM"，通过 Handoff（移交）和 Guardrail（护栏）来协作与控制**。

一句话：**OpenAI Agents SDK = 极简的 Agent 原语 + 优雅的 Handoff 委托 + 内置 Tracing**。

## 设计哲学：极简原语

相比 LangGraph 的"图"、CrewAI 的"角色流水线"、AutoGen 的"自由对话"，OpenAI Agents SDK 只提供**最少的核心原语**：

| 原语 | 作用 | 一句话 |
|------|------|--------|
| `Agent` | 带 instructions + tools 的 LLM | 最小执行单元 |
| `Handoff` | Agent 之间移交控制权 | 委托给专家 |
| `Guardrail` | 输入/输出校验 | 安全护栏 |
| `Session` | 多轮对话状态管理 | 会话记忆 |
| `Runner` | 执行 Agent 的运行时 | 跑起来 |
| `Tracing` | 内置可观测性 | 免费追踪 |

它刻意**不做** LangGraph 那种图编排，也不做 CrewAI 那种角色系统——就是把"一个 LLM + 工具 + 委托"做到极致简单。

## 核心概念

### 1. Agent

```python
from agents import Agent

agent = Agent(
    name="客服助手",
    instructions="你是一个友好的客服助手，帮助用户解决问题",
    tools=[lookup_order, search_faq],
)
```

最小定义只需要 `name` 和 `instructions`（自然语言指令，相当于 System Prompt）。

### 2. Handoff（委托）—— 特色机制

Handoff 让一个 Agent 把对话"移交"给另一个更专业的 Agent：

```python
from agents import Agent, handoff

# 专业 Agent
billing_agent = Agent(
    name="账单专员",
    instructions="处理账单、退款、发票相关问题",
)

support_agent = Agent(
    name="客服",
    instructions="你是客服入口，遇到账单问题移交给账单专员",
    handoffs=[billing_agent],   # 遇到账单问题 → 移交
)
```

**关键点**：Handoff 是"控制权转移"，而不是"消息传递"。移交后，对话上下文会一起带过去，原 Agent 不再参与（除非再移回来）。

这比 CrewAI 的流水线和 AutoGen 的群聊都更清晰地表达了"**这个任务该换人做了**"。

### 3. Guardrails（护栏）

在 Agent 输入/输出两侧做校验：

```python
from agents import Agent, InputGuardrail, GuardrailFunctionOutput
from pydantic import BaseModel

class HomeWorkCheck(BaseModel):
    is_homework: bool
    reasoning: str

@input_guardrail
async def homework_guardrail(ctx, agent, input):
    # 检测是否是作业代写请求
    result = await classify(input)
    return GuardrailFunctionOutput(
        output_info=HomeWorkCheck(is_homework=result.is_homework, reasoning=...),
        tripwire_triggered=result.is_homework,   # True 则触发拦截
    )

agent = Agent(
    name="数学老师",
    instructions="...",
    input_guardrails=[homework_guardrail],
)
```

Guardrail 触发时可以用异常拦截（`tripwire_triggered`），防止不安全/不合适的请求继续。

### 4. Session（会话）

自动管理多轮对话状态：

```python
from agents import Agent, Runner

session = Session()  # 创建会话

result = await Runner.run(agent, "你好", session=session)
# 第二次调用带着同一个 session，自动记住上下文
result2 = await Runner.run(agent, "我刚才问了什么？", session=session)
```

对比 LangGraph 的 `thread_id`、CrewAI 的 Memory，Session 是同类概念的更简表达。

### 5. Tracing（可观测性）—— 免费内置

无需额外配置，每次运行自动生成 Trace，可在 OpenAI 的 dashboard 查看：

```
[Run 开始]
  → Agent: 客服助手
    → LLM 调用 (prompt + completion tokens)
    → Tool 调用: lookup_order
    → Handoff: 账单专员
    → LLM 调用
  → 最终输出
```

这是它的竞争力之一——其他框架的 Tracing 通常要自己接 LangSmith 等第三方工具，而这里**开箱即用**。

## 完整代码示例：客服 Agent + Handoff

```python
import asyncio
from agents import Agent, Runner, handoff, function_tool

# 1. 定义工具
@function_tool
def lookup_order(order_id: str) -> str:
    """根据订单号查询订单状态"""
    return f"订单 {order_id}：已发货"

# 2. 专业 Agent（账单）
billing_agent = Agent(
    name="账单专员",
    instructions="你是账单专家，处理退款、发票、账单疑问",
    tools=[lookup_order],
)

# 3. 入口 Agent（客服，含 Handoff）
support_agent = Agent(
    name="客服",
    instructions="你是客服入口。遇到账单/退款问题，移交给账单专员。",
    handoffs=[billing_agent],
)

# 4. 运行
async def main():
    result = await Runner.run(support_agent, "我的订单 12345 能退款吗？")
    print(result.final_output)

asyncio.run(main())
```

## 与已学框架的定位对比

| 维度 | LangGraph | CrewAI | AutoGen | OpenAI Agents SDK |
|------|-----------|--------|---------|-------------------|
| 出品方 | LangChain | CrewAI | 微软 | OpenAI |
| 编排范式 | 图（状态机） | 流水线（角色） | 对话（自由） | 原语 + Handoff |
| 抽象层级 | 低（最灵活） | 中 | 中 | 低-中（极简） |
| 代码量 | 多 | 少 | 少 | 最少 |
| 特色 | 精确控制 | 角色分工 | 代码执行 | Handoff + Tracing |
| 可观测性 | 需 LangSmith | 需自接 | 需自接 | ✅ 内置 |
| 人机协作 | interrupt | 有限 | human_input_mode | Guardrail + Agent as tool |
| 最佳场景 | 复杂自定义工作流 | 内容流水线 | 代码生成 | 客服/路由/简单多 Agent |

**选择直觉：**

```
你想要什么？
  ├── 精确控制每一步 → LangGraph
  ├── 明确的角色分工流水线 → CrewAI
  ├── 代码自动执行验证 → AutoGen
  └── 极简 + 委托 + 免费追踪 → OpenAI Agents SDK
```

## 关键特性：Agent 作为工具

除了 Handoff，还可以把一个 Agent 当作另一个 Agent 的工具：

```python
from agents import Agent, Runner

translator = Agent(name="翻译", instructions="把文本翻译成英文")

research_agent = Agent(
    name="研究员",
    instructions="...",
    tools=[
        translator.as_tool(tool_name="translate"),  # Agent 变成工具
    ],
)
```

这比 Handoff 更灵活——Handoff 是"交出去不回来"，`as_tool` 是"调用完拿结果继续"。

## 与其他概念的关系

- **前置概念**：[Function Calling](./05-function-calling.md)（OpenAI Agents SDK 完全建立在 tool/function calling 之上）、[ReAct 范式](./04-react-pattern.md)（Runner 内部就是 ReAct 循环）、[Message Role](./07-message-role.md)（instructions/tools 对应 system/tool 角色）
- **后置概念**：Multi-Agent 协作模式（Handoff 是一种协作模式）、Agent 可观测性（内置 Tracing 是它的亮点）
- **相关概念**：[LangGraph](./09-langgraph.md)（同为编排层，但哲学相反——极简 vs 完备）、[CrewAI](./10-crewai-multi-agent.md)（同为多 Agent，但用 Handoff 而非流水线）

## 常见误区

- **误区一："OpenAI Agents SDK 只能用 OpenAI 模型"**：它针对 OpenAI API 优化（尤其 Tracing 和 Responses API），但通过 `model` 参数也能配置兼容端点（如 DeepSeek、Azure OpenAI）。只是第三方模型的 Tracing 等高级功能可能受限。
- **误区二："Handoff 和 CrewAI 的 context 是一回事"**：CrewAI 的 context 是"把上一个任务的结果作为输入"，Agent 还是各干各的；Handoff 是"把对话控制权整体移交"，带走了完整上下文。语义不同。
- **误区三："它比 LangGraph 弱，因为原语少"**：少不是弱，是定位不同。OpenAI Agents SDK 刻意做薄，追求"10 分钟上手 + 免费追踪"，把复杂编排留给 LangGraph。

## 参考资源

- [OpenAI Agents SDK 官方文档](https://openai.github.io/openai-agents-python/) — 完整指南
- [OpenAI Agents SDK GitHub](https://github.com/openai/openai-agents-python) — 源码
- [Swarm → Agents SDK 迁移说明](https://openai.github.io/openai-agents-python/migrating/) — 历史沿革
- [OpenAI Agents SDK 发布博客](https://openai.com/index/new-tools-for-building-agents/) — 官方发布说明

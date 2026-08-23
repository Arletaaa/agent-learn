# 开发笔记

## 设计思路

聚焦 OpenAI Agents SDK 最独特的两个能力：**Handoff（委托）** 和 **Guardrail（护栏）**。

客服场景是 Handoff 最自然的用例：入口 Agent 识别意图，遇到专业问题移交给专家 Agent。这比用 LangGraph 画图、CrewAI 排流水线都更贴合"委托"的语义。

## 关键实现

### Handoff 委托

```python
support_agent = Agent(name="客服", instructions="...", handoffs=[billing_agent, tech_agent])
```

入口 Agent 通过 LLM 判断应该移交给谁，然后 `Runner` 自动完成控制权转移。

### function_tool

```python
@function_tool
def lookup_order(order_id: str) -> str:
    """根据订单号查询状态"""
    ...
```

用装饰器 + docstring 自动生成工具 schema，比 LangChain 的 `bind_tools` 更简洁。

### Guardrail

```python
@input_guardrail
async def refuse_abuse(ctx, agent, input):
    # 检测辱骂/攻击性内容
    ...
```

在输入进入 Agent 前拦截，触发 `tripwire_triggered` 则抛异常终止。

## 遇到问题

1. **DeepSeek 适配**：默认用 OpenAI 的 Responses API，DeepSeek 走 OpenAI 兼容的 Chat Completions 接口，需要设置环境变量让 SDK 切换到兼容模式。
2. **异步 API**：SDK 全异步（`asyncio`），`Runner.run` 是 async 方法，需要 `asyncio.run()` 包裹。

## 对比感受

OpenAI Agents SDK 是四个框架里**代码量最少、上手最快**的：

- LangGraph：要理解图、节点、边、状态
- CrewAI：要理解角色、任务、流水线
- AutoGen：要理解对话、群聊、代码执行器
- **OpenAI Agents SDK：定义 Agent → 声明 handoffs → Runner.run()，完事**

代价是：复杂的自定义流程（并行、条件回溯、精确状态管理）做不了，那得回 LangGraph。

这是"极简原语"哲学的体现——把 80% 的常见场景做到 10 行以内，剩下 20% 交给别的框架。

## 后续延伸

- 体验 `Agent.as_tool()`（把 Agent 当工具调用，区别于 Handoff）
- 开启 Tracing，在 OpenAI dashboard 看执行链路
- 用 Guardrail 实现更复杂的业务校验

# 概念索引

> 按学习阶段的分类索引，每个概念对应一个独立文档。

## 阶段一：基础认知

- [01 - Harness Engineering（驾驭工程）](./01-harness-engineering.md) — AI Agent 运行时的工程范式
- [13 - 多模态模型 vs 大语言模型](./13-multimodal-vs-llm.md) — 离散符号 vs 连续信号，多模态的 Encoder+Adapter 实现方式

## 阶段二：核心概念

- [02 - MCP 协议](./02-mcp-protocol.md) — 模型上下文协议，LLM 与外部工具的标准化接口
- [04 - ReAct 范式](./04-react-pattern.md) — Reasoning + Acting，Agent Loop 的理论基础
- [05 - Function Calling](./05-function-calling.md) — LLM 原生 JSON 工具调用，替代正则解析
- [06 - Agent Memory 架构](./06-agent-memory.md) — 短期/长期/工作记忆，Token 爆炸的三种解决方案
- [07 - Message Role](./07-message-role.md) — system/user/assistant/tool 四角色，Agent 与 LLM 的对话协议
- [08 - Planning 策略对比](./08-planning-strategies.md) — ReAct / Plan-Execute / Reflexion / ReWOO / Tree of Thoughts 五种策略对比

## 阶段三：主流框架

- [03 - Claude Code](./03-claude-code.md) — Anthropic 的终端内 AI 编程 Agent
- [09 - LangGraph 状态图编排](./09-langgraph.md) — 有状态图编排框架，Agent 循环的标准实现
- [10 - CrewAI 多 Agent 协作](./10-crewai-multi-agent.md) — 角色扮演式多 Agent 编排，Sequential / Hierarchical 协作模式
- [11 - AutoGen 对话式多 Agent](./11-autogen.md) — 对话式协作，代码执行闭环，GroupChat 群聊模式
- [12 - OpenAI Agents SDK](./12-openai-agents-sdk.md) — 极简 Agent 原语，Handoff 委托，Guardrail 护栏，内置 Tracing

## 阶段四：关键能力

- [14 - System Prompt 设计方法论](./14-system-prompt-design.md) — 四要素框架，Few-shot / CoT / 分层设计，Agent 指令设计
- [15 - RAG + Agent 联合架构](./15-rag-agent.md) — 检索增强生成，索引四步管线，检索作为工具调用，间接注入安全

## 阶段五：进阶实践

暂无内容

## 阶段六：项目实战

暂无内容

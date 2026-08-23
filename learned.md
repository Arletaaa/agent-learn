# 已学习内容

> 本文件按学习顺序记录已掌握的知识点，每个条目包含概念名称、掌握程度和学习日期。

## 已掌握概念

- [🔵 理解] Harness Engineering（驾驭工程） — 2026-07-22 — AI Agent 运行时的工程范式，LLM 调用的编排与框架化
- [🟢 掌握] MCP 协议（Model Context Protocol） — 2026-07-22 — 开放协议，LLM 与外部工具的标准化接口；深入掌握了 stdio/HTTP SSE 传输机制和 Server 三层架构
- [🔵 理解] Claude Code — 2026-07-22 — Anthropic 的终端内 AI 编程 Agent，终端原生 + MCP 原生
- [🟢 掌握] ReAct 范式 — 2026-07-22 — Reasoning + Acting，Agent 核心循环；理解了从理论到 159 行 Python 实现的完整链路
- [🔵 理解] Function Calling / Tool Use — 2026-07-28 — LLM 原生 JSON 格式工具调用，通过项目三实战理解了 tool_calls 机制
- [🔵 理解] Agent Memory 架构 — 2026-07-28 — 三种记忆类型（短期/长期/工作），三种裁剪策略（窗口/摘要/向量）
- [🔵 理解] Message Role 体系 — 2026-07-28 — system/user/assistant/tool 四角色及其在 Agent Loop 中的对应
- [🔵 理解] Planning 策略对比 — 2026-08-01 — ReAct / Plan-Execute / Reflexion / ReWOO / Tree of Thoughts 五种策略及适用场景
- [🔵 理解] LangGraph 状态图编排 — 2026-08-04 — StateGraph / Nodes / Edges / Checkpointer，手写图与预制库的底层一致性
- [🔵 理解] CrewAI 多 Agent 协作 — 2026-08-05 — Agent/Task/Crew 三层模型，Sequential vs Hierarchical，角色扮演式编排
- [🔵 理解] AutoGen 对话式多 Agent — 2026-08-13 — 对话式协作、代码执行闭环、GroupChat，三框架编排范式对比
- [🔵 理解] OpenAI Agents SDK — 2026-08-15 — 极简原语、Handoff 委托、Guardrail 护栏、内置 Tracing，四框架选型对比
- [🔵 理解] 多模态模型 vs 大语言模型 — 2026-08-15 — 离散符号 vs 连续信号，多模态的 Encoder+Adapter 对齐实现，LLM 向多模态的转换路径
- [🔵 理解] System Prompt 设计方法论 — 2026-08-22 — 四要素框架（角色/任务/约束/输出），Few-shot 与 Chain-of-Thought 手段，分层设计，Agent 指令的职责定位
- [🔵 理解] RAG + Agent 联合架构 — 2026-08-22 — 检索增强生成，索引四步管线（Load/Split/Embed/Store），检索作为工具调用，间接注入攻击面

## 已完成项目

- [✅] [project-01-react-agent](../projects/project-01-react-agent/) — 2026-07-22 — 从零手写 ReAct Agent（Python + DeepSeek API），159 行代码完成走读
- [✅] [project-02-mcp-server](../projects/project-02-mcp-server/) — 2026-07-22 — 手写 MCP Server（Tools / Resources / Prompts），269 行代码完成走读
- [✅] [project-03-langchain-agent](../projects/project-03-langchain-agent/) — 2026-07-28 — LangChain + DeepSeek + DuckDuckGo 搜索，成功运行并对比了 Function Calling vs 正则解析
- [✅] [project-04-planning-strategies](../projects/project-04-planning-strategies/) — 2026-08-01 — 纯 Python 实现三种 Planning 策略对比实验（ReAct / Plan-Execute / Reflexion）
- [✅] [project-05-langgraph](../projects/project-05-langgraph/) — 2026-08-04 — 手写 StateGraph vs create_react_agent，验证 Checkpointer / 流式输出
- [✅] [project-06-crewai](../projects/project-06-crewai/) — 2026-08-05 — 三人调研团队（研究员→分析师→写作者），CrewAI Sequential 流水线
- [✅] [project-07-autogen](../projects/project-07-autogen/) — 2026-08-13 — 双 Agent 代码执行闭环 + GroupChat 多角色协作
- [✅] [project-08-openai-agents](../projects/project-08-openai-agents/) — 2026-08-15 — 客服 Handoff 系统 + Session 记忆 + Guardrail 护栏

## 阶段性了解

- [⚪ 了解] 生产级 Agent 架构 — 2026-07-22 — 了解了原型与生产级在错误处理、流式输出、并发调用、可观测性等方面的差异

---

格式：
```
- [掌握程度] 概念名称 — 学习日期 — 简要说明
```

掌握程度标记：⚪ 了解 / 🔵 理解 / 🟢 掌握 / 🟣 精通

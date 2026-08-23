# 项目三：LangChain Agent + 真实搜索

---

**开始日期**：2026-07-28
**完成日期**：2026-07-28
**状态**：✅ 已完成
**所属阶段**：阶段三

---

## 项目目标

用 LangChain + LangGraph 搭建一个能**真正上网搜索**的 Agent，与项目一的纯手写版做对比，深入理解：
1. Function Calling 如何替代正则解析（更稳定）
2. LangChain 框架帮你做了什么（工具管理、输出解析、循环控制）
3. 手写版和框架版的差异

## 技术栈

- 框架：LangChain + LangGraph
- 模型：DeepSeek Chat API（OpenAI 兼容模式）
- 搜索：Tavily Search API（免费 1000 次/月）或 DuckDuckGo（免费免 Key）
- 语言：Python 3

## 核心功能

1. 用 `ChatOpenAI` 连接 DeepSeek API
2. 用 `create_react_agent` 创建 Agent（LangGraph 内置的 ReAct 实现）
3. 接入真实 Web 搜索 API，不再是内置字典
4. 对比 `tool_calls`（JSON）和手写版的 `_parse_output`（正则）
5. 代码量：框架版约 50 行 vs 手写版 159 行

## 关键学习点

| 对比维度 | 项目一（手写版） | 项目三（LangChain 版） |
|------|------|------|
| LLM 输出格式 | 自由文本 "Thought: ..." | 结构化 JSON `tool_calls` |
| 解析方式 | 正则 `re.search` | 框架自动解析 |
| 工具管理 | 硬编码字典 `{"search": func}` | LangChain Tool 对象 |
| Agent Loop | 自己写 `for step in range(10)` | 框架内置循环 |
| 搜索工具 | 内置 6 条假数据 | 真实 Web 搜索 API |
| 代码行数 | 159 行 | ~50 行 |
| Function Calling | 不支持（文本解析） | 支持（精准 JSON） |

## 项目总结

- 成功跑通了 Function Calling 的真实工作流程——LLM 返回精确 JSON `tool_calls` 而非文本
- 对比手写版（项目一）深刻理解了框架的价值：100 行减少到了 50 行，且稳定性和容错性大幅提升
- DuckDuckGo 免费可用但搜索质量有限，生产环境建议 Tavily
- DeepSeek 的模型倾向于过度搜索（8 轮），需注意 recursion_limit 设置

## 相关资源

- [Tavily Search API](https://tavily.com) — 注册即得 API Key，免费 1000 次/月
- [LangGraph create_react_agent](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent)
- [DeepSeek API 文档](https://api-docs.deepseek.com/)

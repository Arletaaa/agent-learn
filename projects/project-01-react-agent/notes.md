# 开发笔记

---

## 关键设计决策

### 为什么不直接用 OpenAI SDK？
DeepSeek 的 API 与 OpenAI 完全兼容，用 `requests` 直接调用可以减少依赖，同时加深对 API 协议的理解。生产环境中建议用 SDK。

### 输出解析策略
LLM 的 ReAct 格式输出可能不稳定（多空格、多余文本）。当前使用简单的正则匹配，容错性一般。更好的做法是使用 Function Calling 模式（让 LLM 直接返回 JSON），但这超出了"手写 ReAct"的范围。

### 搜索工具的局限
当前`search`工具使用硬编码的知识库，仅用于演示 Agent Loop。实际项目中应接入 SerpAPI、Tavily 等真实搜索 API。

## 遇到的问题

### 问题一：LLM 有时不按格式输出
**现象**：LLM 有时直接输出答案而不用 Action 格式
**解决**：在检测到没有 Final Answer 也没有 Action 时，将原始输出作为最终答案返回

### 问题二：正则匹配多行 Thought
**现象**：Thought 可能跨多行，单行匹配会截断
**解决**：使用 `re.DOTALL` 模式匹配多行

## 延伸方向

- 接入真实搜索 API（Tavily / SerpAPI）
- 增加更多工具（文件读写、SQL 查询、Python 执行）
- 用 Function Calling 替代文本解析，提高稳定性
- 添加流式输出支持
- 包装成 CLI 工具，模仿 Claude Code 的交互体验

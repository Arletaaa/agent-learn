# 开发笔记

---

## 关键设计决策

### 为什么用 LangGraph 而不是 LangChain 旧版 Agent？

LangChain 的旧版 `initialize_agent` 已不推荐使用。`langgraph.prebuilt.create_react_agent` 是官方推荐的新方式，基于图结构（Graph）管理 Agent 状态流转，更灵活也更清晰。

### 为什么 DeepSeek API 走 ChatOpenAI？

DeepSeek API 兼容 OpenAI 格式——同一个 `base_url` 和 API Key 即可接入。这意味着你写的代码可以无缝切换到 GPT、Gemini 等任何 OpenAI 兼容的 API。

### Function Calling 比正则好在哪里？

```
正则版（手写）:
  LLM 输出："Action: search\nAction Input: langchain"
  问题：LLM 多打一个空格、换行不对 → 解析崩溃

Function Calling 版（框架）:
  LLM 返回精确 JSON:
  {"tool_calls": [{"name": "search", "arguments": {"query": "langchain"}}]}
  问题：没有——JSON 永远是准确的
```

### 搜索 API 选择

- **Tavily**：专门为 AI Agent 优化的搜索引擎，免费 1000 次/月，推荐使用
- **DuckDuckGo**：完全免费不需要 API Key，适合快速测试，但速度和质量不如 Tavily

## LangGraph create_react_agent 内部做了什么

```
create_react_agent(model, tools)
        │
        ├── 1. 构造 System Prompt（告诉 LLM 可以用的工具）
        ├── 2. 将 tools 转为 OpenAI Function Calling 的 tools 参数
        ├── 3. 创建状态图：
        │       agent 节点（LLM 决策）
        │       tools 节点（执行工具并返回 observation）
        │       └── 两个节点之间自动循环，直到 LLM 不再调用工具
        └── 4. 返回 CompiledGraph，调用 .invoke() 即可运行
```

## 遇到的问题

待记录

## 延伸方向

- 接入更多工具：文件读写、Git 操作、数据库查询
- 用 LangSmith 追踪 Agent 每一步的执行
- 对比 Tavily 和 DuckDuckGo 的搜索结果质量
- 尝试 LangGraph 的自定义状态图（多节点、条件分支）

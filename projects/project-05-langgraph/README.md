# 项目五：LangGraph Agent 手写图 vs 预制库对比

---

**开始日期**：2026-08-04
**完成日期**：2026-08-04
**状态**：✅ 已完成
**所属阶段**：阶段三 - 主流框架

---

## 项目目标

用 LangGraph 实现同一个搜问答 Agent，用**两种方式**对比：

1. **手写 StateGraph**：手动定义节点、边、条件逻辑——理解底层机制
2. **create_react_agent**：一行代码生成 Agent——对比效率提升

通过对比两者的底层结构，理解"LangGraph 在帮你做什么"。

## 技术栈

- 框架：LangGraph + LangChain OpenAIIntegration
- 模型：DeepSeek Chat
- 工具：Tavily Web 搜索 / DuckDuckGo

## 核心功能

1. 手写 StateGraph Agent（80 行）
2. create_react_agent 一行版（5 行核心逻辑）
3. Checkpointer 持久化 + 多轮对话测试
4. 流式输出对比

## 运行方式

```bash
# 安装依赖
pip install langgraph langchain-openai langchain-community tavily-python

# 设置 API Key
set DEEPSEEK_API_KEY=sk-xxx
set TAVILY_API_KEY=tvly-xxx

# 运行对比
python compare_graph.py
```

## 相关资源

- 概念文档：[09 - LangGraph 状态图编排](../../concepts/09-langgraph.md)
- LangGraph 官方文档：https://langchain-ai.github.io/langgraph/
- LangGraph 教程：https://langchain-ai.github.io/langgraph/tutorials/

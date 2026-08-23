# Function Calling / Tool Use

---

**更新时间**：2026-07-28
**所属阶段**：阶段二 - 核心概念
**掌握程度**：🔵 理解

---

## 概念定义

Function Calling（工具调用）是 LLM **原生支持的 JSON 格式工具调用机制**——不再让 LLM 输出自由文本然后正则解析（ReAct 文本模式），而是让 LLM 直接返回结构化的 `tool_calls` 数组，精确指定要调用的工具名称和参数。

## 核心要点

1. **LLM 输出的是 JSON，不是文本**：当 LLM 判断需要调用工具时，返回 `{"name": "search", "arguments": {"query": "XXX"}}`，不是 `Action: search\nAction Input: XXX`
2. **LLM 本身不执行工具**：Function Calling 只是让 LLM 告诉调用方"我需要调什么、参数是什么"，实际执行在本地代码
3. **tools 参数注入**：调用 API 时，通过 `tools` 参数将工具的 JSON Schema 定义传给 LLM，LLM 据此知道有哪些工具可用

## 工作原理

### 请求流程

```
API 请求中包含 tools 定义 →
LLM 推理是否需要工具 →
如果需要 → 返回 tool_calls JSON →
本地代码执行工具 → 将结果以 tool role 消息注入 →
再次调用 LLM → 继续推理直到给出最终答案
```

### DeepSeek API 调用示例（OpenAI 兼容格式）

**请求**：告诉 LLM 有哪些工具可用

```json
{
  "model": "deepseek-chat",
  "messages": [{"role": "user", "content": "今天西安天气怎么样"}],
  "tools": [{
    "type": "function",
    "function": {
      "name": "search",
      "description": "搜索网络获取实时信息",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {"type": "string", "description": "搜索关键词"}
        },
        "required": ["query"]
      }
    }
  }],
  "temperature": 0
}
```

**LLM 返回**（JSON 格式，不是文本）：

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "search",
          "arguments": "{\"query\": \"西安 天气 2026-07-28\"}"
        }
      }]
    }
  }]
}
```

**执行后注入结果**：

```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "content": "西安今天晴，气温 28-38°C"
}
```

**LLM 收到结果后继续推理** → 最终返回答案

### 对比：Function Calling vs ReAct 文本模式

| 维度 | ReAct 文本模式（项目一） | Function Calling（项目三） |
|------|------|------|
| LLM 输出格式 | 自由文本 `Action: search\nAction Input: XXX` | JSON `{"name": "search", "args": {"query": "XXX"}}` |
| 解析方式 | 正则 `re.search(r"Action:\s*(.+)")` | 框架自动解析 `tool_calls` |  
| 容错性 | 低——格式稍有不一致就崩 | 高——JSON 结构保证精确 |
| 并行调用 | 不支持 | 支持——一次返回多个 `tool_calls` |
| 参数类型 | 全部为字符串 | 支持任意 JSON 类型（数字、布尔、对象） |

### 代码对比

```python
# 项目一（手写正则解析）
raw = llm_response  # "Action: search\nAction Input: langchain"
action = re.search(r"Action:\s*(.+)", raw).group(1)
action_input = re.search(r"Action Input:\s*(.+)", raw).group(1)

# 项目三（Function Calling，框架自动处理）
# LLM 直接返回 tool_calls JSON，无需解析
for tc in msg.tool_calls:
    name = tc["name"]       # "duckduckgo_search"
    args = tc["args"]       # {"query": "2026年7月 科技新闻"}
```

## 与其他概念的关系

- 前置概念：ReAct 范式（文本模式 → JSON 模式的升级）
- 后置概念：MCP 协议（Function Calling 定义"怎么描述工具"，MCP 定义"怎么连接工具"）
- 相关概念：Agent Loop、结构化输出、Tool Use

## 常见误区

- **误区一："Function Calling 就是 LLM 执行了函数"**：LLM 只返回"请调这个函数"的 JSON，实际执行永远是本地代码。LLM 没有能力真正调用外部函数。
- **误区二："Function Calling 和 MCP 是同一回事"**：Function Calling 是 LLM 层面的接口（OpenAI/DeepSeek API 的 `tools` 参数），MCP 是工具注册和发现的协议层。两者互补，不是替代关系。
- **误区三："有 Function Calling 就不用 ReAct 了"**：Function Calling 只是改变了"输出格式"（文本→JSON），ReAct 的 Thought-Action-Observation 循环逻辑依然存在——只不过 LLM 的 Thought 不再显式输出，而是在一次 JSON 调用中隐式完成。

## 参考资源

- [OpenAI Function Calling 指南](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use 文档](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [DeepSeek API 文档 - Function Calling](https://api-docs.deepseek.com/guides/function_calling)
- 项目三实战代码：[`project-03-langchain-agent/main.py`](../projects/project-03-langchain-agent/main.py)

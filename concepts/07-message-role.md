# Message Role（消息角色体系）

---

**更新时间**：2026-07-28
**所属阶段**：阶段二 - 核心概念
**掌握程度**：🔵 理解

---

## 概念定义

Message Role 是 LLM API 中对消息发送者身份的标记——LLM 根据不同的 role 采用不同的处理策略。四种角色定义了 Agent 与 LLM 之间的完整对话协议。

## 四种 Role

| role | 谁说的 | 在 Agent 中的作用 |
|------|------|------|
| `system` | 开发者 | 设定人设、规则、可用工具，**贯穿整个对话，权重最高** |
| `user` | 用户 / Agent 执行端 | 用户提问 + 传统 ReAct 模式下的工具结果（Observation） |
| `assistant` | LLM | LLM 的上一次回答 / 工具调用请求（`tool_calls`） |
| `tool` | Agent 执行端 | Function Calling 模式下的工具返回结果（替代旧的 user+Observation 写法） |

## 为什么不能混用

LLM 训练时对不同 role 有不同处理逻辑：

| role | LLM 被训练成的理解 |
|------|------|
| `system` | "这是最高指令，我需要严格遵循" |
| `user` | "这是别人对我说的，我需要回应" |
| `assistant` | "这是我说过的话，我需要保持一致性" |
| `tool` | "这是工具返回的客观数据，不是用户的意图或情感" |

混用的后果：把工具结果写成 `user`，LLM 可能把搜索噪音当成用户的对话意图，导致跑偏。

## 代码对比

### ReAct 文本模式（项目一）

```python
messages = [
    {"role": "system",    "content": "你是一个Agent，可用工具：search, calculator"},
    {"role": "user",      "content": "Question: LangChain是什么？"},
    {"role": "assistant", "content": "Thought: 我需要搜索\nAction: search\nAction Input: langchain"},
    {"role": "user",      "content": "Observation: LangChain是最成熟的LLM框架..."},  # 工具结果用 user
    {"role": "assistant", "content": "Thought: 信息足够了\nFinal Answer: LangChain是..."},
]
```

**问题**：Observation 用 `user` role——LLM 无法区分"用户说天气好"和"工具返回了搜索结果"。

### Function Calling 模式（项目三）

```python
messages = [
    {"role": "system",    "content": "..."},
    {"role": "user",      "content": "今天天气怎么样"},
    {"role": "assistant", "content": None,
     "tool_calls": [{"id": "call_001", "type": "function",
                     "function": {"name": "search", "arguments": '{"query":"西安天气"}'}}]},
    {"role": "tool",      "tool_call_id": "call_001", "content": "西安晴，28°C"},  # 精确区分
    {"role": "assistant", "content": "西安今天晴天，28°C"},
]
```

**优势**：`tool` role 让 LLM 明确知道"这是工具数据，不需要你共情或追问"。

## 四个 Role 配合 ReAct Loop 的完整映射

```
system    → Agent 的"宪法"，定义行为边界和可用能力
user      → 用户的原始输入
assistant → Think 的结果（推理 + 工具调用决策）
tool      → Observation 的标准化格式
assistant → 最终答案
```

## 与其他概念的关系

- 前置概念：ReAct 范式（定义了 Thought / Action / Observation 三类消息，Message Role 是它们在 API 层的实现）
- 后置概念：Function Calling（引入 `tool` role + `tool_calls` 机制）
- 相关概念：Agent 输入输出抽象、System Prompt 设计

## 常见误区

- **误区一："role 只是标签，写什么都行"**：LLM 对不同 role 的处理逻辑是训练时固化的，把 Observation 写成 `user` 会导致行为异常。
- **误区二："system 和 user 没区别"**：system 的指令权重更高，且不会被后续对话稀释。Agent 的工具定义应该放 system 而不是 user。
- **误区三："不用 tool role 也能跑"**：能跑，但不稳定。Function Calling 的标准要求 `tool` role + `tool_call_id` 关联，否则 LLM 可能失去对工具调用链路的追踪。

## 参考资源

- [OpenAI Chat Completion API - Message Roles](https://platform.openai.com/docs/guides/text-generation) — 官方 role 定义
- [Anthropic Messages API](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) — Claude 的 role 体系
- 项目一实战：[project-01-react-agent/main.py](../projects/project-01-react-agent/main.py) — ReAct 文本模式的 role 使用
- 项目三实战：[project-03-langchain-agent/main.py](../projects/project-03-langchain-agent/main.py) — Function Calling 的 tool role 使用

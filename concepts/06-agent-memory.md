# Agent Memory 架构

---

**更新时间**：2026-07-28
**所属阶段**：阶段二 - 核心概念
**掌握程度**：🔵 理解

---

## 概念定义

Agent Memory 是指 AI Agent 系统中**存储、管理和检索信息的机制**——决定了 Agent 能记住什么、记住多久、以及如何使用这些记忆。没有 Memory 的 Agent 是"金鱼脑"，每一轮对话都是新的开始。

## 核心要点

1. **三种记忆类型**：短期记忆（当前会话的 messages 列表）、长期记忆（跨会话持久化的知识）、工作记忆（当前任务相关的中间结果）
2. **核心矛盾**：LLM 有 token 上限，messages 不能无限增长，必须"选择性失忆"
3. **三种裁剪策略**：窗口滑动（只留最近 N 条）、自动摘要（LLM 把旧消息压缩成一段话）、向量检索（只取与当前问题最相关的历史消息）

## 三种记忆类型

### 1. 短期记忆（Short-Term Memory）

**是什么**：当前会话中所有的对话消息列表。

**在你的项目一里**，就是这个 messages 数组：

```python
messages = [
    {"role": "system",  "content": "你是一个能使用工具的 AI Agent..."},
    {"role": "user",    "content": "Question: LangChain 是什么？"},
    {"role": "assistant","content": "Thought: 我需要搜索\nAction: search..."},
    {"role": "user",    "content": "Observation: LangChain 是最成熟的..."},
    {"role": "assistant","content": "Thought: 信息足够了\nFinal Answer: ..."},
]
```

**特点**：

- 随会话结束而消失
- 受 LLM token 上限限制（DeepSeek 最大 128K，但越长越慢越贵）
- 所有 Agent 都有这一层——这是最低限度的记忆

### 2. 长期记忆（Long-Term Memory）

**是什么**：跨会话持久化的知识库。关了终端、明天再开，Agent 还记得你。

**三种实现方式**：

| 方式                 | 存储                 | 例子                                 | 适用场景               |
| -------------------- | -------------------- | ------------------------------------ | ---------------------- |
| **关系数据库** | 用户偏好、事实       | "用户喜欢用中文回答"                 | 个性化设置             |
| **向量数据库** | 对话摘要的 embedding | 用`chroma`/`pinecone` 存历史对话 | 语义检索过去的讨论     |
| **文件系统**   | 完整对话记录         | JSON 文件存全部历史消息              | 审计、调试、简单持久化 |

**LangChain 的实现**：

```python
from langchain.memory import VectorStoreRetrieverMemory

# 把每个对话回合存成向量
# 新问题时：搜索最相关的历史对话 → 注入当前上下文
memory = VectorStoreRetrieverMemory(retriever=vector_store.as_retriever(k=3))

# Agent 用上了长期记忆：能看到 3 天前的对话
```

### 3. 工作记忆（Working Memory）

**是什么**：当前任务所需的临时上下文。不是完整历史，而是"当前需要的"那部分。

**包含**：

- 工具调用的返回结果（Observation）
- 中间推理步骤
- 任务拆分出的子目标状态

**实例**：在你的项目三里，Agent 连续搜了 8 次。每搜一次，结果注入 messages，但这个结果只在"回答 2026 年 7 月科技新闻"这个任务期间有效——任务完成就不需要了。这就是工作记忆。

## 核心问题：Token 爆炸

### 问题

```
第 1 轮: messages 长度 = 1K token
第 5 轮: messages 长度 = 5K token（每次工具调用注入搜索结果）
第 10 轮: messages 长度 = 12K token
第 30 轮: messages 长度 = 40K token  →  LLM 开始"遗忘"最早的上下文
第 50 轮: messages 长度 = 70K token  →  可能超出 API 限制
```

### 三种解决方案

#### 方案一：窗口滑动（Sliding Window）

只保留最近 **N 条**消息，旧的全删。

```
messages = messages[-10:]   # 只要最后 10 条
```

**优点**：最简单，代码一行
**缺点**：5 步前的关键上下文丢了——比如你第 1 步搜到"北京人口 2184 万"，第 11 步要用时已经没了

#### 方案二：自动摘要（Summarization）

让 LLM 把旧消息压缩成一段话。

```python
# LangChain 的 ConversationSummaryMemory
# 背后做的事：
# 1. 当 messages 超过阈值时
# 2. 把最老的一半消息发给 LLM："请把以上对话总结成一段话"
# 3. 用这段话替代原始消息
```

```
原始（3000 token）:
  User: 帮我查北京、上海、广州的人口
  Agent: 北京 2184 万
  User: 再查深圳、杭州
  Agent: 深圳 1766 万...

摘要后（80 token）:
  "用户在调查中国主要城市的人口数据，已获取北京(2184万)、
   上海(2487万)、广州(1881万)、深圳(1766万)、杭州(1237万)的信息"
```

**优点**：省 token + 保留关键信息
**缺点**：摘要可能丢失细节，依赖 LLM 概括质量

#### 方案三：向量检索（Vector Retrieval）

把每条消息转成向量存起来，新问题时只检索最相关的。

```
用户当前问："北京房价多少钱？"
    ↓ 向量相似度匹配
检索到历史："北京人口 2184 万" ← 相关！
跳过历史："今天天气不错" ← 不相关，跳过
```

**优点**：语义匹配，智能选择该记住什么
**缺点**：需要向量数据库，增加复杂度

### 三种策略对比

| 策略               | 保留什么   | 丢失什么         | 代码复杂度   |
| ------------------ | ---------- | ---------------- | ------------ |
| **窗口滑动** | 最近 N 条  | 旧但可能重要的   | 极低（1 行） |
| **自动摘要** | 摘要文本   | 细节             | 中           |
| **向量检索** | 语义相关的 | 无关但可能有用的 | 高           |

**实际应用：三种混用**

生产级 Agent 通常组合使用：

```
短期记忆：Sliding Window（当前会话，保留最近 20 条）
    +
长期记忆：Vector Store（跨会话，检索相关历史）
    +
摘要兜底：Summarization（定期压缩，防止 token 爆炸）
```

## 在你的项目里看 Memory

### 项目一（手写 ReAct）

```python
# 这就是短期记忆——全保留，不做任何裁剪
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": question},
]

for step in range(10):
    raw = self._call_llm(messages)
    # 每条 Observation 都被追加
    messages.append({"role": "assistant", "content": raw})
    messages.append({"role": "user", "content": f"Observation: {observation}"})
    # 问题：如果 step 跑到 50，messages 就 50 条了
```

### 项目三（LangGraph Agent）

```python
# LangGraph 默认也是全保留
# 但可以配置 checkpoint 实现长期记忆：
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
agent = create_react_agent(llm, tools, checkpointer=memory)

# 同一个 thread_id → Agent 记住了之前的对话
agent.invoke({"messages": [("user", "你好我叫小明")]},
              config={"configurable": {"thread_id": "user-123"}})

agent.invoke({"messages": [("user", "我叫什么？")]},
              config={"configurable": {"thread_id": "user-123"}})
# → "你叫小明"  ← 跨轮次记住了！
```

## 与其他概念的关系

- 前置概念：ReAct 范式（messages 列表 = 短期记忆）、Function Calling
- 后置概念：RAG（向量检索 + Agent 结合）、Multi-Agent 协作（各 Agent 之间的记忆共享）
- 相关概念：上下文压缩（Compaction）、Planning 策略（长任务 → 需要更好的记忆管理）

## 常见误区

- **误区一："Memory 就是对话历史"**：对话历史只是短期记忆。真正的 Memory 系统包含短期、长期、工作三层，以及裁剪策略。
- **误区二："直接把所有消息发 LLM 就行"**：token 有上限，超过就报错。即使没超过，越长越慢、越贵、LLM 越"糊涂"。
- **误区三："Memory 越详细越好"**：过多无关历史会稀释当前问题的注意力。好 Memory 的核心不是"记多少"，而是"找到对当前有用的"。

## 代码示例：把 Memory 加到项目一

```python
class ReActAgentWithMemory(ReActAgent):
    def __init__(self, api_key=None, max_history=10):
        super().__init__(api_key)
        self.max_history = max_history  # 最多保留 10 轮
        self.long_term = {}  # 长期记忆：用户偏好

    def run(self, question):
        # 尝试检索长期记忆中的相关信息
        if "北京" in question:
            # 上次查过北京人口，直接注入工作记忆
            cache = self.long_term.get("北京人口")
            if cache:
                question = f"{question}\n（已知：{cache}）"

        messages = [
            {"role": "system", "content": self._system_prompt()},
            {"role": "user", "content": f"Question: {question}"},
        ]

        for step in range(self.max_steps):
            # 窗口滑动：只保留 system prompt + 最近 10 条
            if len(messages) > self.max_history + 1:
                # 保留 system prompt + 最后 max_history 条
                messages = [messages[0]] + messages[-(self.max_history):]

            raw = self._call_llm(messages)
            parsed = self._parse_output(raw)

            if parsed["final_answer"]:
                return parsed["final_answer"]

            observation = self.tools[parsed["action"]](parsed["action_input"])
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": f"Observation: {observation}"})

            # 有价值的结果存入长期记忆
            if "人口" in observation:
                self.long_term[question] = observation
```

## 参考资源

- [LangChain Memory 文档](https://python.langchain.com/docs/modules/memory/) — 官方 Memory 模块指南
- [LangGraph Checkpointer](https://langchain-ai.github.io/langgraph/reference/checkpoints/) — 跨会话记忆保存
- [OpenCode Compaction 配置](https://opencode.ai/docs/config/#compaction) — 上下文压缩实践

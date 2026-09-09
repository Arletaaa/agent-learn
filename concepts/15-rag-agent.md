# RAG + Agent 联合架构

---

**更新时间**：2026-08-22
**所属阶段**：阶段四 - 关键能力
**掌握程度**：🔵 理解

---

## 概念定义

检索增强生成（Retrieval Augmented Generation，RAG）是 Meta AI 提出（Lewis et al., 2021）的方法：**把一个信息检索组件和文本生成模型结合**，让 LLM 基于检索到的真实文档生成答案，而不是只靠训练时学到的静态知识。

一句话：**RAG = 给 LLM 外接一个"可查询的资料库"，答案基于检索到的真实文档，而不是模型记忆。**

## 为什么需要 RAG

LLM 的"参数化知识"（训练时学到的东西）是**静态的**——不更新、会过期、可能幻觉。让模型回答"最新 API 用法"或"公司内部政策"，它只能靠猜。

RAG 解决这个问题的核心价值：

1. **知识可即时更新**：改库即可，模型**不用重新训练**
2. **更符合事实**：生成的答案更可靠、更具体、更一致
3. **缓解幻觉**：回答基于真实检索材料
4. **可溯源**：答案可附带来源出处（引用具体文档）

```
用户问题 ──► [检索器：从知识库取相关文档] ──► [把文档+问题拼成上下文] ──► [LLM 生成答案]
```

## 完整管线

### 索引阶段（离线，建库一次，4 步）

| 步骤     | 动作     | 说明                                             |
| -------- | -------- | ------------------------------------------------ |
| 1. Load  | 加载文档 | 把数据源（网页/PDF/数据库）读成`Document` 对象 |
| 2. Split | 切分     | 用 Text Splitter 把大文档切成小块（chunk）       |
| 3. Embed | 向量化   | Embedding 模型把每块转成"语义向量"               |
| 4. Store | 存储     | 向量和文本一起存进 VectorStore（向量数据库）     |

LangChain 官方示例：

```python
# 1. 加载
docs = load_langchain_docs()

# 2. 切分（chunk_size=1000，overlap=200）
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200
)
all_splits = text_splitter.split_documents(docs)

# 3. 向量化
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# 4. 存储
from langchain_core.vectorstores import InMemoryVectorStore
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_documents(all_splits)
```

### 查询阶段（在线，每次回答都跑，2 步）

1. **Retrieve 检索**：用户问题转成向量，在库里做相似度搜索，取 Top-K 相关块
2. **Generate 生成**：LLM 基于「问题 + 检索到的文档」生成答案

```
相似度搜索：question 向量 vs 库中所有 chunk 向量 → 按余弦相似度排序 → 取 top_k
```

## 切分（Chunking）与 Overlap

切分粒度是 RAG 效果的关键工程参数：

- **chunk_size 过小**：语义被切断，单块信息不完整 → 检索不到完整答案
- **chunk_size 过大**：块内噪声多、检索精度下降，且占用 token 多、上下文昂贵
- **chunk_overlap 重叠**：相邻块之间保留重叠部分，防止关键句子被切断在边界上丢失
- 常用默认：`chunk_size=1000, chunk_overlap=200`（LangChain 默认建议）

## RAG 与 Agent 结合：从"前缀拼接"到"工具调用"

进阶模式（按复杂度递进）：

| 模式                           | 说明                                                                       |
| ------------------------------ | -------------------------------------------------------------------------- |
| 1. Skills-guided retrieval     | Agent 加载"搜索技能"（用哪个索引、怎么构造查询、引用格式），再调用检索工具 |
| 2. Rubric-checked grounding    | 检索→草稿→评分子 Agent 检查答案是否基于检索材料，不通过则修订            |
| 3. Todo-driven investigation   | Agent 用规划工具把复杂问题拆成多个搜索项，逐项检索后综合                   |
| 4. Retrieve, offload, delegate | 检索到的 chunk 写入文件系统，并行子 Agent 分析，避免主上下文爆炸           |

**核心转变**：在 Agent 中，**检索变成一个工具调用**——Agent 决定何时搜、搜什么、怎么用结果，而不是把检索结果硬拼进每轮 prompt。这对应已学的 Function Calling 机制（工具 schema + 模型自主决策）。

## 安全警告：间接提示注入

> RAG 应用极易遭受**间接提示注入**。检索到的文档里可能藏着伪装成指令的文字。因为检索内容和 System Prompt **共享同一上下文窗口**，模型可能去执行文档里的指令，而不是你的提示。

**防御现状**：

- **没有任何 prompt 或分隔符策略能完全防住**间接注入
- 缓解手段：提示词要求"把检索内容当纯数据"、加 `# Source:` 头区分元数据与正文——**有帮助但不可靠**
- 真正可靠的办法：**对输出做校验**（确认答案引用的文档路径、核对声明与检索材料是否一致）

## 与其他概念的关系

- **前置概念**：[Message Role](./07-message-role.md)（检索结果作为上下文注入）、[System Prompt 设计](./14-system-prompt-design.md)（RAG 与 System Prompt 共享上下文窗口，是注入攻击面）、[Function Calling](./05-function-calling.md)（RAG 在 Agent 中作为工具调用）
- **后置概念**：Agent 安全性（间接注入防御）、Agent 评估（RAG 质量评测：检索召回率、生成忠实度）
- **相关概念**：[LangGraph](./09-langgraph.md)（可用状态图编排 RAG 多步流程）、[Agent Memory](./06-agent-memory.md)（向量记忆与 RAG 检索共享向量库技术）

## 常见误区

- **误区一："RAG 就是往 prompt 里拼文档"**：简单场景是的，但工程化 RAG 要处理切分、检索质量、引用溯源、注入防御等，是完整系统设计
- **误区二："向量库越大检索越准"**：检索质量取决于切分、Embedding 模型、Top-K 设置与相关度阈值，不是越大越好
- **误区三："检索到就能防幻觉"**：只有模型被约束"基于检索材料回答"并校验输出，才有效；否则模型仍会凭记忆补充编造
- **误区四："检索结果和 System Prompt 一样安全"**：检索内容是外部数据，可能含恶意指令（间接注入），必须当不可信输入处理

## 引导问题（自学自检）

1. RAG 相比"把全文直接塞进 prompt"的核心优势是什么？代价是什么？
2. 切分粒度（chunk_size）大了/小了各有什么问题？overlap 起什么作用？
3. 为什么说 RAG 是"间接注入"高发区？System Prompt 挡不住的本质原因是什么？
4. 结合 LangChain 教程，"检索作为工具调用"和"检索结果拼进上下文"的区别？

## 参考资源

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — RAG 开创性论文（Lewis et al., 2021）
- [LangChain RAG 教程](https://python.langchain.com/docs/tutorials/rag/) — 官方 RAG 全流程教程
- [OpenAI Cookbook](https://cookbook.openai.com/) — 检索增强生成入门
- [Prompt Engineering Guide - RAG 章节](https://www.promptingguide.ai/zh/techniques/rag) — RAG 概念中文讲解
- [Simon Willison - Prompt Injection 系列](https://simonwillison.net/series/prompt-injection/) — 间接注入权威资料

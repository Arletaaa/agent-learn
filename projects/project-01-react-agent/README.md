# 项目一：从零手写 ReAct Agent

---

**开始日期**：2026-07-22
**完成日期**：2026-07-22
**状态**：✅ 已完成
**所属阶段**：阶段二

---

## 项目目标

不依赖任何 Agent 框架（LangChain 等），用纯 Python 实现一个 ReAct Agent，通过 DeepSeek API 驱动，验证 Thought → Action → Observation 循环。

## 技术栈

- 模型：DeepSeek Chat API（OpenAI 兼容接口）
- 语言：Python 3
- 依赖：`requests`（HTTP 调用）

## 核心功能

1. 调用 DeepSeek API，获取 LLM 的 Thought/Action/Action Input
2. 解析 LLM 输出，区分工具调用和最终答案
3. 在本地执行搜索和计算工具
4. 将 Observation 反馈给 LLM，形成闭环循环
5. 纯 Python 约 120 行代码

## 实现过程

### 步骤一：API 调用层

使用 `requests` 库直接调用 DeepSeek API（OpenAI 兼容接口），发送 messages + tools 描述，获取 LLM 的文本响应。

### 步骤二：输出解析

用正则表达式从 LLM 输出中提取 4 种信息：
- `Thought:` — 推理过程
- `Action:` — 工具名称
- `Action Input:` — 工具参数
- `Final Answer:` — 最终答案

### 步骤三：工具执行

定义两个本地工具：
- `search` — 从内置知识库检索（模拟搜索 API）
- `calculator` — 执行数学表达式求值

### 步骤四：Agent Loop

将工具执行结果（Observation）注入消息列表，继续调用 LLM，直到 LLM 返回 Final Answer 或达到最大步数。

## 项目总结

- 核心代码只有约 120 行，串起了 ReAct 的全部核心概念
- 深刻理解了 Agent Loop 的本质：LLM 只管"思考"和"决策"，本地端负责"执行"
- 与 LangChain 的 ReAct Agent 对比：框架帮你封装了解析、工具注册、循环控制——但本质完全一样
- 后续可扩展：接入真实的 Web Search API、文件系统操作、代码执行

## 相关资源

- [DeepSeek API 文档](https://api-docs.deepseek.com/)
- [ReAct 论文](https://arxiv.org/abs/2210.03629)

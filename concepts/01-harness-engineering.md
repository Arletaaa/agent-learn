# Harness Engineering（驾驭工程）

---

**更新时间**：2026-07-22
**所属阶段**：阶段二 - 核心概念
**掌握程度**：🔵 理解

---

## 概念定义

Harness Engineering（驾驭工程）是指在 AI Agent 系统中，**将 LLM 调用"装配"进一套可控、可复用的运行时框架的工程范式**。它决定了大模型调用的"位置、时机与方式"——不再像 Prompt Engineering 那样关注"如何写好一句提示词"，而是关注"如何系统地编排多轮推理、工具调用与上下文管理"。

## 核心要点

1. **Harness = LLM 的"驾驶舱"**：它包装了 LLM 调用，负责输入构造（prompt + context）、输出解析（thinking / tool_call / final_answer）和循环控制（loop → observe → act）。
2. **关注点从"提示词"转向"工程架构"**：传统 prompt engineering 关注怎么写出更好的指令；harness engineering 关注怎么构建让 agent 稳定运行的工程骨架——包括 memory、tool registry、error recovery、streaming、human-in-the-loop 等。
3. **共识 > 分歧**：主流框架在"agent loop（推理→执行→观察→循环）""function calling 抽象""消息驱动的通信模型"上高度趋同；真正的分歧在于 planning 粒度（隐式 vs 显式规划）、memory 架构（短期/长期/向量记忆）和 multi-agent 编排（顺序/并行/辩论/层级）。

## 工作原理 / 架构

```
┌─────────────────────────────────────────────┐
│                 Harness Runtime              │
│                                             │
│   ┌─────────┐  ┌──────────┐  ┌───────────┐ │
│   │  LLM    │  │  Tool    │  │  Memory   │ │
│   │ Adapter │  │ Registry │  │  Manager  │ │
│   └────┬────┘  └────┬─────┘  └─────┬─────┘ │
│        │            │              │        │
│   ┌────┴────────────┴──────────────┴─────┐  │
│   │           Agent Loop                  │  │
│   │  think → act(tool_call) → observe     │  │
│   │   ↑                         ↓         │  │
│   │   └─────── repeat ──────────┘         │  │
│   └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

一个典型 Harness 的执行流程：

1. **think**：将当前上下文（system prompt + 历史消息 + 工具定义）发送给 LLM，获取响应
2. **parse**：解析 LLM 输出，判断是最终答案、工具调用、还是需要继续推理
3. **act**：如果是工具调用，执行对应工具，获取结果
4. **observe**：将工具结果注入上下文
5. **loop**：回到 step 1，直到 LLM 给出最终答案或达到最大轮次

## 各框架共识与分歧

### 共识

- **Agent Loop 模式**：几乎所有框架都采用 "推理 → 行动 → 观察 → 循环" 的基本模式（源自 ReAct）
- **Tool/Function Calling 抽象**：统一的工具注册、参数定义、调用接口
- **消息驱动的状态管理**：以消息列表（message list）作为 agent 的"工作记忆"

### 分歧

| 维度 | 隐式规划派（LangChain/LangGraph） | 显式规划派（Plan-and-Execute） | 极简派（Claude Code/ccagent） |
|------|------|------|------|
| Planning 方式 | LLM 自行在 loop 中隐式推理 | 先制定计划，再按步骤执行 | 不显式规划，由用户驱动 |
| Memory 设计 | 复杂 memory 中间件（向量/图/关系） | 依赖任务描述和步骤状态 | 文件系统 + shell 即是记忆 |
| 多 Agent | 图编排 / Supervisor / 辩论 | 步骤级并行 | 单 Agent 为主 |
| 代码量 | 重框架（万行级） | 中等 | 极轻量（百行级） |

## 与其他概念的关系

- 前置概念：ReAct 范式、Function Calling / Tool Use
- 后置概念：Multi-Agent 协作模式、Agent 生产部署
- 相关概念：MCP 协议（工具标准化）、Agent Memory 架构、Planning 策略

## 常见误区

- **误区一："Harness Engineering 就是写个 while loop"**：虽然最简形式确实是一个循环，但生产级 Harness 需要考虑上下文压缩（compaction）、流式输出、错误恢复、并发工具调用、权限控制等大量工程细节。
- **误区二："用 LangChain 就等于做了 Harness Engineering"**：框架只是工具，真正的 Harness Engineering 关注的是设计决策——为什么在这个场景下选择某种 loop 结构、某种 memory 策略、某种 tool 组织方式。

## 参考资源

- 菜鸟教程：初识 AI Harness — Harness Engineering 入门介绍
- 知乎：Harness Engineering 深度解析 — AI Agent 时代的工程范式革命
- [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) — "Bash is all you need"，从 0 到 1 构建纳米级 agent harness

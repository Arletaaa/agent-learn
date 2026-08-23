laude Code

---

**更新时间**：2026-07-22
**所属阶段**：阶段三 - 主流框架
**掌握程度**：🔵 理解

---

## 概念定义

Claude Code 是 Anthropic 推出的**终端内 AI 编程 Agent**，在终端中以对话方式协助开发者理解代码、完成任务和进行重构。它的设计哲学是"文件系统 + Shell 即是 Agent 的交互界面"，体现了极简 Harness Engineering 理念。

## 背景：Anthropic 公司

Anthropic 由前 OpenAI 研究员 Dario Amodei 和 Daniela Amodei 于 2021 年创立，核心使命是构建**安全、可靠、可控**的 AI 系统。公司代表产品包括：

- **Claude 系列模型**：主打安全对齐的大语言模型，采用 Constitutional AI（宪法 AI）训练方法
- **Claude Code**：终端内编程 Agent，2025 年发布
- **MCP 协议**：开放的工具连接协议，已获行业广泛关注
- **Claude Desktop**：桌面端 AI 助手

## 核心要点

1. **终端原生（Terminal-Native）**：Claude Code 运行在终端内，直接操作文件系统和执行 Shell 命令，没有 GUI 层的抽象。这种设计让 Agent 的能力边界就是开发者本身的能力边界。
2. **Agent Loop 内建**：采用标准的 think → act → observe 循环，Claude Code 可以自主读取文件、执行命令、修改代码，并在每轮循环中根据观察结果调整下一步策略。
3. **MCP 原生支持**：Claude Code 天然支持 MCP 协议，可以通过配置 MCP Server 扩展能力（连接数据库、外部 API、Git 平台等），是 MCP 生态的旗舰级 Client。
4. **多模型接入**：虽然名为 "Claude Code"，但通过配置可以接入多种大模型（如 OpenAI GPT、DeepSeek、Gemini 等），本质上是一个模型无关的 Agent Harness。

## 工作原理 / 架构

```
┌────────────────────────────────────────────────┐
│                 Terminal（终端）                │
│                                                │
│   User Prompt ──────────────────────┐          │
│                                     ▼          │
│   ┌──────────────────────────────────────┐     │
│   │           Claude Code Agent          │     │
│   │                                      │     │
│   │  ┌────────┐  ┌────────┐  ┌───────┐  │     │
│   │  │ System │  │ Tool   │  │ Agent │  │     │
│   │  │Prompt  │  │ Set    │  │ Loop  │  │     │
│   │  └────────┘  └────────┘  └───┬───┘  │     │
│   │                              │       │     │
│   │  ┌───────────────────────────┘       │     │
│   │  ▼                                   │     │
│   │  ┌────────────────────┐              │     │
│   │  │    LLM Provider    │              │     │
│   │  │  Claude / GPT /    │              │     │
│   │  │  DeepSeek / ...    │              │     │
│   │  └────────────────────┘              │     │
│   └──────────────────────────────────────┘     │
│          │                    │                │
│          ▼                    ▼                │
│   ┌────────────┐    ┌──────────────────┐      │
│   │ File System│    │  MCP Servers     │      │
│   │ (读写代码)  │    │  (扩展能力)       │      │
│   └────────────┘    └──────────────────┘      │
└────────────────────────────────────────────────┘
```

### 核心工具集

Claude Code 内置的工具能力：

| 工具          | 功能          | 说明                       |
| ------------- | ------------- | -------------------------- |
| `Read`      | 读取文件/目录 | 查看代码内容               |
| `Write`     | 创建/覆写文件 | 生成新文件或重写           |
| `Edit`      | 精确编辑文件  | 基于字符串替换的精确修改   |
| `Bash`      | 执行终端命令  | 运行测试、构建、Git 操作等 |
| `Glob`      | 文件模式匹配  | 按通配符查找文件           |
| `Grep`      | 内容搜索      | 正则搜索代码内容           |
| `Task`      | 启动子 Agent  | 将复杂任务委托给子 Agent   |
| `Skill`     | 加载技能指令  | 载入特定场景的工作流       |
| `TodoWrite` | 任务清单管理  | 跟踪多步骤任务进度         |

## 可接入的大模型

Claude Code 通过 provider 配置可以接入多种模型：

| 类别                | 模型示例                                             |
| ------------------- | ---------------------------------------------------- |
| **Anthropic** | Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.5 |
| **OpenAI**    | GPT-4.1, GPT-4o, o4-mini                             |
| **Google**    | Gemini 2.5 Pro/Flash                                 |
| **DeepSeek**  | DeepSeek-V3, DeepSeek-R1                             |
| **OpenCode**  | Zen 提供的优化模型                                   |
| **本地模型**  | 通过 Ollama 等接入本地部署模型                       |

配置方式：在 `opencode.json` 中通过 `provider`、`model`、`small_model` 字段指定。

## 与其他概念的关系

- 前置概念：ReAct 范式、Function Calling / Tool Use、MCP 协议
- 后置概念：Multi-Agent 协作、Agent 生产部署
- 相关概念：Harness Engineering（Claude Code 是 Harness 的典型实现）、ccagent（极简复刻版）

## 与其他 Agent 工具的对比

| 维度     | Claude Code            | Cursor          | GitHub Copilot  | Aider            |
| -------- | ---------------------- | --------------- | --------------- | ---------------- |
| 运行方式 | 终端 CLI               | IDE 插件        | IDE 插件        | 终端 CLI         |
| 交互模式 | 对话式 Agent           | 内联补全 + Chat | 内联补全 + Chat | 对话式 Agent     |
| 工具调用 | 文件读写 + Shell + MCP | 文件编辑        | 内联编辑        | 文件编辑 + Shell |
| MCP 支持 | 原生支持               | 有限支持        | 不支持          | 不支持           |
| 开源     | 否                     | 否              | 否              | 是               |

## 常见误区

- **误区一："Claude Code 只能用 Claude 模型"**：Claude Code 是一个 agent harness，支持接入多种 LLM provider，不仅仅是 Claude。
- **误区二："Claude Code = 一个更聪明的 IDE 补全"**：Claude Code 的核心能力不是代码补全，而是自主理解任务、分解步骤、执行工具、观察反馈的完整 Agent 循环。

## 参考资源

- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code/overview) — 官方概述
- [Claude Code 接入所有大模型配置教程](https://zhuanlan.zhihu.com/) — 知乎教程
- 知乎：每天了解一家大模型公司 — Anthropic 篇
- [OpenCode](https://github.com/anomalyco/opencode) — 开源 AI 编程 Agent（类似 Claude Code）

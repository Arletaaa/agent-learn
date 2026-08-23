# MCP 协议（Model Context Protocol）

---

**更新时间**：2026-07-22
**所属阶段**：阶段二 - 核心概念
**掌握程度**：🟢 掌握

---

## 概念定义

MCP（Model Context Protocol）是 Anthropic 发布的**开放协议**，旨在为 AI 模型与外部工具/数据源之间的交互提供一个标准化接口。它类比 USB-C 协议——无论设备内部多复杂，都可以通过统一的接口连接和通信。

## 核心要点

1. **标准化工具连接**：MCP 解决了 AI 应用需要逐个适配不同 API 的痛点，定义了一套统一的 Client-Server 协议，让任何 MCP Server 都可以被任何 MCP Client 发现和调用。
2. **三原语：Resources / Tools / Prompts**：MCP Server 可以暴露三类能力——Resources（数据资源，如文件、数据库表）、Tools（可执行的工具函数）、Prompts（预定义的提示词模板）。
3. **传输层灵活**：MCP 支持 stdio（标准输入输出，本地进程间通信）和 HTTP SSE（远程服务器通信）两种传输方式，兼顾本地开发和远程部署。

## 工作原理 / 架构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  MCP Host    │────▶│  MCP Client  │────▶│  MCP Server  │
│  (Claude     │     │  (协议客户端) │     │  (工具/数据   │
│   Desktop/   │     │              │     │   提供方)     │
│   Claude     │     │  - stdio     │     │              │
│   Code)      │     │  - HTTP SSE  │     │  文件系统    │
└──────────────┘     └──────────────┘     │  数据库      │
                                           │  API 网关    │
                                           │  Git 仓库    │
                                           └──────────────┘
```

### 核心交互流程

1. **初始化握手**：Client 发送 `initialize` 请求，Server 返回能力列表（支持的功能和能力）
2. **能力发现**：Client 通过 `tools/list`、`resources/list`、`prompts/list` 探索 Server 的能力
3. **调用执行**：Client 通过 `tools/call` 执行具体工具，Server 返回执行结果
4. **资源读取**：Client 通过 `resources/read` 读取 Server 管理的数据资源
5. **通知机制**：Server 可主动推送变更通知，触发 Client 更新上下文

### 三原语

| 原语 | 描述 | 示例 |
|------|------|------|
| **Resources** | 暴露数据资源供模型读取 | 文件内容、数据库查询结果、API 返回数据 |
| **Tools** | 暴露可执行的工具函数 | 创建文件、发送 HTTP 请求、执行 SQL |
| **Prompts** | 预定义的提示词模板 | 代码审查模板、单元测试生成模板 |

## 传输层详解：stdio vs HTTP SSE

| 维度 | stdio（本地模式） | HTTP + SSE（网络模式） |
|------|------|------|
| **访问范围** | 本机，同一操作系统进程 | 局域网 / 公网 |
| **启动方式** | Client 启动子进程运行 Server | Server 独立运行监听端口 |
| **生命周期** | 随 Client 启停，用完即走 | 常驻服务，持续运行 |
| **通信通道** | stdin 读请求 / stdout 写响应 | HTTP POST 发请求 / SSE 推响应 |
| **配置方式** | `"command": ["python", "server.py"]` | `"url": "https://host:port/sse"` |
| **典型场景** | 本地工具、开发调试 | 服务器部署、团队共享 |

### 交互流程对比

**stdio 模式**（你的 `server.py`）：
```
Client 启动子进程 → stdio_server() 建立读写通道 → app.run()
→ 每次请求通过 stdin/stdout 序列化 JSON-RPC
```

**HTTP 模式**（网络部署）：
```
Server 启动 uvicorn 监听 8000 端口
Client 通过 POST /sse 建立 SSE 长连接
→ 通过 POST /messages 发 JSON-RPC 请求 → Server 通过 SSE 推响应
```

### 代码差异

```python
# stdio 启动（当前版本）
async with stdio_server() as (read_stream, write_stream):
    await app.run(read_stream, write_stream, ...)

# HTTP 启动（网络版本）
import uvicorn
app.sse_app()
uvicorn.run(app, host="0.0.0.0", port=8000)
```

## MCP Server 代码架构（三层模型）

一个 MCP Server 由三层组成：

| 层 | 职责 | 代码量 | 示例 |
|------|------|------|------|
| **工具实现层** | 真正干活的纯函数 | 轻量 | `def tool_get_time(): return ...` |
| **协议注册层** | 通过装饰器向外界声明能力 | 6 个方法 | `@app.list_tools()` / `@app.call_tool()` |
| **传输启动层** | 建立通信通道 | 3 行 | `stdio_server()` 启动 |

### 6 个装饰器对应 3 类能力

| 能力 | 列出（list） | 执行/读取（call/read/get） |
|------|------|------|
| **Tools** | `@app.list_tools()` | `@app.call_tool()` |
| **Resources** | `@app.list_resources()` | `@app.read_resource()` |
| **Prompts** | `@app.list_prompts()` | `@app.get_prompt()` |

### 完整交互流程（以 get_time 为例）

```
opencode（MCP Client）              你的 server.py（MCP Server）
     │
     │ ─── {"method": "tools/list"} ───→  @app.list_tools() 返回 3 个工具定义
     │ ←── [{name: "get_time", ...}] ──
     │
     │ AI 决策："我需要当前时间"
     │
     │ ─── {"method": "tools/call",      │
     │       "name": "get_time"} ──────→  @app.call_tool("get_time", {})
     │                                   执行 tool_get_time()
     │ ←── {datetime: "2026-07-24...",   │
     │       timezone: "UTC+8"} ────────
```

## 与 Function Calling 的区别

| 维度 | MCP | 原生 Function Calling |
|------|-----|------|
| 标准化程度 | 统一协议，一次编写多处复用 | 各 LLM 厂商格式不同 |
| 连接方式 | Client-Server 架构，独立进程 | 嵌入在 LLM 调用中 |
| 生命周期 | 持久化，可跨会话复用 | 单次调用，无状态 |
| 动态发现 | Server 主动声明能力列表 | 需要在请求中预先定义 tools |
| 生态 | 开放协议，社区可自行开发 Server | 依赖厂商 SDK |

## 与其他概念的关系

- 前置概念：Function Calling / Tool Use
- 后置概念：Claude Code（MCP 的典型应用）、Agent 工具编排
- 相关概念：Harness Engineering（MCP 是 Harness 中 Tool Registry 的标准化实现）、API 网关、插件系统

## 常见误区

- **误区一："MCP 只能和 Claude 一起用"**：MCP 是开放协议，任何 LLM 都可以作为 MCP Host（通过适配 MCP Client），目前已有多家厂商和社区支持。
- **误区二："MCP 替代了 Function Calling"**：MCP 是工具连接的协议层，Function Calling 是 LLM 调用工具的接口层。两者互补——MCP 定义了"怎么连接工具"，Function Calling 定义了"怎么描述和触发工具"。

## 参考资源

- [MCP 官方文档](https://modelcontextprotocol.io) — Anthropic MCP 协议规范
- [CSDN MCP 入门教程](https://blog.csdn.net/fufan_LLM/article/details/146377471) — MCP 协议入门指南
- [MCP Server 开发指南](https://modelcontextprotocol.io/docs/concepts/architecture) — 官方架构文档

# 项目二：手写 MCP Server

---

**开始日期**：2026-07-22
**完成日期**：2026-07-22
**状态**：✅ 已完成
**所属阶段**：阶段二

---

## 项目目标

用 Python 从零手写一个 MCP Server，实现 Tools / Resources / Prompts 三类能力，并在本地验证 MCP 协议的 Client-Server 交互流程。

## 技术栈

- 协议：MCP（Model Context Protocol）
- 语言：Python 3
- 依赖：`mcp`（MCP Python SDK），`requests`

## 核心功能

1. **Tools（工具）**：`get_time`（获取当前时间）、`calculate`（数学计算）、`web_fetch`（抓取网页标题）
2. **Resources（资源）**：`server://status`（服务状态信息）、`server://tools-list`（工具清单）
3. **Prompts（提示词模板）**：`code-review`（代码审查模板）、`explain-concept`（概念解释模板）
4. 通过 stdio 与 MCP Client（如 opencode）通信

## 实现过程

### 步骤一：定义 MCP Server

使用 `mcp.server.Server` 创建服务实例，注册 Tools、Resources、Prompts 三类能力。

### 步骤二：实现 Tools

- `get_time`：返回带时区的当前时间（Python `datetime`）
- `calculate`：安全的数学表达式计算
- `web_fetch`：通过 HTTP GET 获取网页标题

### 步骤三：实现 Resources

- `server://status`：动态返回服务器运行信息
- `server://tools-list`：返回所有可用工具的列表

### 步骤四：实现 Prompts

- `code-review`：接收代码文本，返回结构化的代码审查提示词
- `explain-concept`：接收概念名称，返回概念解释的提示词模板

### 步骤五：stdio 通信

使用 `stdio_server` 通过标准输入/输出与 MCP Client 通信，这是本地进程间最常用的 MCP 传输方式。

## 项目总结

- MCP Server 的开发体验远超预期——三个装饰器搞定工具、资源、提示词的注册
- 理解了 MCP"三原语"在代码层面如何实现：
  - Tools = 可执行的函数
  - Resources = 可读取的数据
  - Prompts = 可复用的提示词模板
- MCP 的价值在于"一次编写、多处复用"——这个 Server 可以被 opencode、Claude Desktop、Cursor 等任何 MCP Client 发现和调用
- 下一步可以研究：多 Server 协作、动态 Tools 注册、权限控制

## 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

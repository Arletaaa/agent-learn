# 开发笔记

---

## MCP Python SDK 核心概念

### Server 的三个核心装饰器

```python
@server.list_tools()    # 声明有哪些工具可用
@server.call_tool()     # 处理工具调用请求
@server.list_resources()  # 声明有哪些资源
@server.read_resource()   # 处理资源读取请求
@server.list_prompts()    # 声明有哪些提示词模板
@server.get_prompt()      # 处理提示词获取请求
```

### 通信方式

MCP 支持两种传输层：
- **stdio**：本地进程通过标准输入输出通信（本项目的实现）
- **HTTP SSE**：远程 Server 通过 HTTP 通信（用于分布式场景）

### 如何被 opencode 使用

在 opencode.json 中配置：

```json
{
  "mcp": {
    "my-server": {
      "type": "local",
      "command": ["python", "path/to/server.py"]
    }
  }
}
```

opencode 会自动启动 Server 进程，通过 stdio 与之通信，并在工具列表中展示 Server 的 Tools。

## 遇到的问题

### 问题一：MCP SDK 安装
`pip install mcp` 即可安装 MCP Python SDK。

### 问题二：Tools 的参数定义
工具的参数通过 JSON Schema 定义，`inputSchema` 字段描述参数类型和约束。MCP Client 据此生成合适的参数输入界面。

### 问题三：错误处理
工具执行需要 try/except 包裹，返回 `TextContent` 时包含 `isError: True` 表示执行失败。

## 延伸方向

- 接入真实 API（天气查询、新闻、数据库操作）
- 实现 Resource 的动态生成（如按日期变化的报告）
- 探索 MCP Server 的认证和安全机制
- 部署为远程 HTTP MCP Server

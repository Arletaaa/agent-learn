"""
手写 MCP Server —— 实现 Tools / Resources / Prompts 三类能力
通过 stdio 与 MCP Client 通信
"""
import asyncio
import datetime
import json
import re

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    Prompt,
    PromptMessage,
    GetPromptResult,
)


# ============================================================
# 工具实现
# ============================================================

def tool_get_time() -> str:
    """获取当前时间（北京时间）"""
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    return json.dumps({
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "Asia/Shanghai (UTC+8)",
        "timestamp": int(now.timestamp()),
        "weekday": ["一", "二", "三", "四", "五", "六", "日"][now.weekday()],
    }, ensure_ascii=False, indent=2)


def tool_calculate(expression: str) -> str:
    """安全地计算数学表达式"""
    try:
        allowed = {
            "abs": abs, "round": round, "min": min, "max": max,
            "pow": pow, "int": int, "float": float,
            "sum": sum, "len": len,
        }
        result = eval(expression, {"__builtins__": allowed}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误：{e}"


def tool_word_count(text: str) -> str:
    """统计文本的字数、行数和字符数"""
    lines = text.strip().split("\n")
    words = text.strip().split()
    return json.dumps({
        "characters": len(text),
        "words": len(words),
        "lines": len(lines),
    }, ensure_ascii=False, indent=2)


# ============================================================
# MCP Server
# ============================================================

app = Server("demo-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_time",
            description="获取当前北京时间，返回日期、时间、时间戳和星期",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="calculate",
            description="安全地计算数学表达式",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 '2 + 3 * 4' 或 'pow(2, 10)'",
                    },
                },
                "required": ["expression"],
            },
        ),
        Tool(
            name="word_count",
            description="统计文本的字数、行数和字符数",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "需要统计的文本内容",
                    },
                },
                "required": ["text"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "get_time":
            result = tool_get_time()
        elif name == "calculate":
            result = tool_calculate(arguments["expression"])
        elif name == "word_count":
            result = tool_word_count(arguments["text"])
        else:
            result = f"未知工具：{name}"
            return [TextContent(type="text", text=result, isError=True)]

        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"执行失败：{e}", isError=True)]


# ============================================================
# Resources 实现
# ============================================================

@app.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="server://status",
            name="服务状态",
            description="MCP Server 运行状态信息",
            mimeType="application/json",
        ),
        Resource(
            uri="server://tools-list",
            name="工具清单",
            description="当前 Server 提供的所有工具列表",
            mimeType="application/json",
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))

    if uri == "server://status":
        status = {
            "server": "demo-mcp-server",
            "version": "1.0.0",
            "status": "running",
            "started_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "capabilities": ["tools", "resources", "prompts"],
            "transport": "stdio",
        }
        return json.dumps(status, ensure_ascii=False, indent=2)

    elif uri == "server://tools-list":
        tools_info = [
            {"name": "get_time", "description": "获取当前北京时间"},
            {"name": "calculate", "description": "安全地计算数学表达式"},
            {"name": "word_count", "description": "统计文本字数、行数、字符数"},
        ]
        return json.dumps(tools_info, ensure_ascii=False, indent=2)

    else:
        return json.dumps({"error": f"未知资源：{uri}"}, ensure_ascii=False)


# ============================================================
# Prompts 实现
# ============================================================

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="code-review",
            description="生成代码审查提示词",
            arguments=[
                {"name": "code", "description": "待审查的代码", "required": True},
                {"name": "language", "description": "编程语言", "required": False},
            ],
        ),
        Prompt(
            name="explain-concept",
            description="生成概念解释提示词",
            arguments=[
                {"name": "concept", "description": "要解释的概念", "required": True},
            ],
        ),
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "code-review":
        code = arguments.get("code", "")
        language = arguments.get("language", "")
        lang_hint = f"（{language}）" if language else ""

        prompt_text = f"""请对以下{lang_hint}代码进行审查，从以下几个角度分析：

1. **正确性**：代码逻辑是否正确，是否有 bug
2. **性能**：是否有性能瓶颈或优化空间
3. **可读性**：变量命名是否清晰，结构是否合理
4. **安全性**：是否存在安全漏洞
5. **改进建议**：给出具体的改进方案

代码：
```
{code}
```

请用中文回复，逐条分析。"""

        return GetPromptResult(
            description=f"代码审查提示词{lang_hint}",
            messages=[
                PromptMessage(role="user", content=TextContent(type="text", text=prompt_text)),
            ],
        )

    elif name == "explain-concept":
        concept = arguments.get("concept", "")

        prompt_text = f"""请用中文解释以下概念：

概念：{concept}

要求：
1. 一句话定义
2. 核心原理（用通俗语言）
3. 一个简单的类比帮助理解
4. 一个实际应用场景
5. 与相关概念的区别"""

        return GetPromptResult(
            description=f"概念解释提示词：{concept}",
            messages=[
                PromptMessage(role="user", content=TextContent(type="text", text=prompt_text)),
            ],
        )

    else:
        raise ValueError(f"未知提示词模板：{name}")


# ============================================================
# 启动入口
# ============================================================

async def main():
    print("MCP Server 'demo-mcp-server' 已启动（通过 stdio 通信）", file=__import__("sys").stderr)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

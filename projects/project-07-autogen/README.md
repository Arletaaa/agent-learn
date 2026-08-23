# 项目七：AutoGen 代码 Agent —— 自我验证的编程助手

---

**开始日期**：2026-08-13
**完成日期**：2026-08-13
**状态**：✅ 已完成
**所属阶段**：阶段三 - 主流框架

---

## 项目目标

用 AutoGen 构建一个**能自我验证代码的编程助手**：

1. 程序员 Agent（assistant）负责写代码
2. 用户代理（user_proxy）负责执行代码、反馈结果
3. 两者通过对话协作，直到代码运行正确

核心体验：**代码执行闭环**——assistant 写代码，user_proxy 执行，报错自动反馈修正。

## 技术栈

- 框架：AutoGen（pyautogen）
- LLM：DeepSeek Chat（OpenAI 兼容接口）
- 代码执行：本地 Python 执行器（非 Docker）

## 核心功能

1. 双 Agent 对话协作
2. 代码自动执行 + 结果反馈
3. 出错自动修正的闭环
4. 可选的 GroupChat 多角色扩展

## 运行方式

```bash
# 安装依赖
pip install pyautogen

# 设置 API Key
set DEEPSEEK_API_KEY=sk-xxx

# 运行
python code_agent.py
```

## 相关资源

- 概念文档：[11 - AutoGen 对话式多 Agent](../../concepts/11-autogen.md)
- AutoGen 官方文档：https://microsoft.github.io/autogen/

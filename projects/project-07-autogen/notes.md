# 开发笔记

## 设计思路

AutoGen 最独特的价值是"代码执行闭环"，本项目聚焦这一能力：让 assistant 写代码，user_proxy 执行，形成自动修正循环。

选择了一个简单的数学任务（斐波那契数列）来最小化其他干扰，专注体验"对话式协作"和"代码自验证"两个核心机制。

## 关键实现

### 双 Agent 配置

```python
assistant = AssistantAgent(name="assistant", system_message="...", llm_config=config)
user_proxy = UserProxyAgent(name="user_proxy", human_input_mode="NEVER",
                            code_execution_config={"use_docker": False})
```

`use_docker: False` 是关键——本地直接执行代码，避免 Docker 依赖。

### 对话发起

```python
user_proxy.initiate_chat(assistant, message="写函数算斐波那契...")
```

之后的一切（写代码→执行→反馈→修正）都是自动的。

### 终止机制

assistant 的 system_message 里要求"任务完成后回复 TERMINATE"，AutoGen 识别这个关键词来结束对话。

## 遇到问题

1. **DeepSeek 适配**：AutoGen 用 `llm_config["config_list"]` 配置，需要 `base_url` 指向 DeepSeek 的 OpenAI 兼容端点。
2. **代码执行器**：`use_docker: False` 时 AutoGen 用本地 subprocess 执行，Windows 下需要注意工作目录和编码。

## 对比感受

相比 CrewAI 的"流水线"和 LangGraph 的"状态机"，AutoGen 的"对话"最自由：

- **优点**：assistant 写错了，user_proxy 自动把报错贴回去，assistant 自动修正——这个闭环在 CrewAI/LangGraph 里都要自己手动搭
- **缺点**：对话可能跑偏，assistant 可能啰嗦地反复解释而不聚焦任务

这是"控制"和"涌现"的权衡：AutoGen 放弃了精确控制，换来了自然涌现的协作。

## 后续延伸

- 用 GroupChat 组建"程序员 + 测试员 + 评审"三人团队
- 代码执行任务换成数据分析（写 pandas 代码分析 CSV）
- 开启 human_input_mode="TERMINATE" 观察 Human-in-the-Loop

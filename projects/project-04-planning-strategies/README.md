# 项目四：Planning 策略对比实验

---

**开始日期**：2026-08-01
**完成日期**：2026-08-01
**状态**：✅ 已完成
**所属阶段**：阶段二 - 核心概念

---

## 项目目标

用纯 Python + DeepSeek API 实现 **ReAct**、**Plan-and-Execute**、**Reflexion** 三种 Planning 策略，在同一任务上运行并对比 Token 消耗、执行轨迹和输出质量。

## 技术栈

- 框架：纯 Python（openai SDK）
- 模型：DeepSeek Chat（`deepseek-chat`）
- 工具：内置模拟工具（search / calculator / weather / translate）

## 核心功能

1. ReAct 策略：Think → Act → Observe 循环
2. Plan-and-Execute 策略：先规划再执行
3. Reflexion 策略：执行 + 自我评估 + 反思重试
4. 统一输出 Token 统计和对比报告

## 运行方式

```bash
# 设置 API Key
set DEEPSEEK_API_KEY=sk-xxx

# 安装依赖
pip install openai

# 运行对比实验
python compare_planning.py
```

## 相关资源

- 概念文档：[08 - Planning 策略对比](../../concepts/08-planning-strategies.md)
- ReAct 论文：https://arxiv.org/abs/2210.03629
- Reflexion 论文：https://arxiv.org/abs/2303.11366
- Plan-and-Solve 论文：https://arxiv.org/abs/2305.04091

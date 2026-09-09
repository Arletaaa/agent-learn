# 项目十：dev-mentor —— 引导式开发 Skill（AI 辅助，不代写）

---

**开始日期**：2026-08-23
**完成日期**：待定
**状态**：🔄 进行中
**所属阶段**：阶段四 - 关键能力 / 实践

---

## 项目目标

制作第二个 Agent Skill：**dev-mentor**——当用户想通过项目练习积累开发经验时，把 AI 从"代写代码"变成"开发导师"：任务拆解 + 逐个引导 + 代码审查，**完全禁止 AI 输出完整可运行代码**，不清楚的地方先询问用户。

## 背景动机

- 用 AI 开发会直接代写代码 → 用户得不到经验积累
- 想要的模式：AI 辅助、用户亲手写（与项目 `AGENTS.md` 的"引导式学习"理念一致，只是把场景从"学概念"扩展到"做项目"）

## 核心功能

1. 澄清优先：动手前先问清目标/技术栈/水平/环境
2. 任务清单式：拆 3~8 个小任务，一次派一个，用户完成回报后推进
3. 提示递进：方向 → 线索 → 示例雏形，禁止一步到位
4. 代码审查循环：肯定 → 指出问题让用户自己改 → 确认理解
5. 收尾复盘：用户自己总结收获

## 文件结构

```
project-10-dev-mentor/
├── SKILL.md                 # ★ 技能主文件（v2：严批评风格 + 五维标准审查）
├── README.md                # 项目概述
├── notes.md                 # 开发笔记
└── references/
    └── worked-examples.md   # 完整示例（已含首测与 v2 评审）
```

## 发布状态

- ✅ 已加入独立仓库：[Arletaaa/agent-skills](https://github.com/Arletaaa/agent-skills)（MIT，Public）的 `skills/dev-mentor/`，当前 **v3**
- ✅ 已 skills.sh 收录并**已刷新到 v3**：pack 链接 `https://skills.sh/p/gNs3YHuh7lG7xP4S`（含 decision-challenge + dev-mentor），重新安装验证命中 v3 标记
- 经验记录：skills.sh 缓存提交时快照，**推 GitHub 后需在 skills.sh 刷新/重提一次**才会服务新版（v2→v3 已验证）
- 本地副本：`G:\MyProjects\agent-skills\skills\dev-mentor\`

## 相关资源

- 概念文档：[17 - Agent Skills](../../concepts/17-agent-skills.md)、[16 - Multi-Agent 协作模式](../../concepts/16-multi-agent-patterns.md)
- 本项目理念参照：`AGENTS.md`（引导式学习规范）

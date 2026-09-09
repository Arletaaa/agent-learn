# 项目九：Decision Challenge —— 反谄媚决策质询 Skill

---

**开始日期**：2026-08-23
**完成日期**：待定
**状态**：🔄 进行中
**所属阶段**：阶段四 - 关键能力

---

## 项目目标

制作第一个 Agent Skill：**decision-challenge**——当用户在做重要决策时，强制 LLM 以"最强反方 → 最强正方 → 中立裁判"三阶段质询，对抗 LLM 的谄媚倾向（sycophancy），输出不迎合用户的诚实分析。

## 技术栈

- 形态：`SKILL.md`（无框架依赖、模型无关，任何支持 Agent Skills 的环境可用）
- 学习基础：`concepts/17-agent-skills.md`（Skill 规范）、`concepts/16-multi-agent-patterns.md`（辩论模式）

## 核心功能

1. 三阶段对抗式质询（反方质询 / 正方辩护 / 中立裁判）
2. 硬性反谄媚规则（禁奉承开头、区分事实/观点/推测、标注置信度、证据不足明说）
3. 结构化输出（便于审查与前后对比）
4. 渐进式披露（完整示例放 `references/`，SKILL.md 保持精简）

## 文件结构

```
project-09-decision-challenge/
├── SKILL.md                 # ★ 技能主文件（核心交付物）
├── README.md                # 项目概述
├── notes.md                 # 开发笔记
└── references/
    └── worked-examples.md   # 完整示例（渐进式披露）
```

## 使用 / 安装方式

以 Claude Code 为例，将技能放入 skills 目录：

```bash
mkdir -p ~/.claude/skills/decision-challenge
cp SKILL.md ~/.claude/skills/decision-challenge/
cp -r references ~/.claude/skills/decision-challenge/
```

之后向 Agent 描述一个**你倾向做出的决定**，Skill 会自动触发三阶段质询。

## 发布状态

- ✅ 已发布为独立仓库：[Arletaaa/agent-skills](https://github.com/Arletaaa/agent-skills)（MIT，Public），当前为 SKILL.md v3
- 本地副本：`G:\MyProjects\agent-skills`（`skills/decision-challenge/`）
- 待办：skills.sh 注册（GitHub 验证后跟进）；在 Claude Code 环境实测触发

## 相关资源

- 概念文档：[17 - Agent Skills](../../concepts/17-agent-skills.md)、[16 - Multi-Agent 协作模式](../../concepts/16-multi-agent-patterns.md)
- 官方参考：[anthropics/skills](https://github.com/anthropics/skills)、[Claude.ai - Creating custom skills](https://claude.com/docs/skills/how-to)

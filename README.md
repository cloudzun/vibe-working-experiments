# Vibe Working Experiments 🧪

> **探索性开发实验项目** - 快速验证 AI Agent 可行性

**原则**：
1. 🚀 **快速迭代** - 2 小时验证一个想法
2. ✅ **接受不完美** - 最简版本优先
3. 📝 **记录过程** - 开发日志必填
4. 🔄 **成功再迁移** - 验证通过后合并到主项目

---

## 📦 当前实验

### Experiment 1: RFP Response Agent（计划中）

**目标**：2 小时内跑通端到端流程

**步骤**：
1. ✅ 环境准备（15 分钟）
2. ⏳ RFP 问题提取（30 分钟）
3. ⏳ 知识检索（45 分钟）
4. ⏳ 生成响应文档（30 分钟）

**素材**：
- `experiments/rfp-simple/materials/` - 7 个 RFP 相关文件

**文档**：
- `experiments/rfp-simple/RFP-EXPLORATION-PLAN.md` - 完整开发计划

---

## 📁 项目结构

```
vibe-working-experiments/
├── README.md                    # 本文件
├── .gitignore                   # Git 忽略规则
└── experiments/                 # 实验目录
    └── rfp-simple/              # RFP Response 实验
        ├── materials/           # 素材文件
        │   ├── VanArsdel_RFP.docx
        │   ├── EcoSense_360_*.docx (5 个产品文档)
        │   └── Fabrikam_Historical_RFP_Data.xlsx
        └── RFP-EXPLORATION-PLAN.md
```

---

## 🎯 与主项目的关系

**主项目**：`vibe-working` (MS-4004 OpenCode 课程)
- 成熟的课程内容
- 完整的教学设计
- 稳定的代码质量

**实验项目**：`vibe-working-experiments`
- 快速验证新想法
- 接受失败和重构
- 成功后迁移到主项目

---

## 🚀 开始实验

```bash
# 进入实验目录
cd experiments/rfp-simple

# 查看开发计划
cat RFP-EXPLORATION-PLAN.md

# 开始开发...
```

---

## 📊 实验记录模板

```markdown
# 实验日志 - [实验名称]

**日期**: YYYY-MM-DD
**开发者**: [姓名]
**耗时**: [X] 小时

## 完成情况

- [ ] Step 1: [内容]
- [ ] Step 2: [内容]
- ...

## 遇到的问题

1. [问题] → [解决方案]
2. ...

## 关键发现

- [发现 1]
- [发现 2]

## 结果

✅ 成功 / ⚠️ 部分成功 / ❌ 失败

## 下一步

- [ ] [任务 1]
- [ ] [任务 2]
```

---

## 🔗 相关链接

- **主项目**: https://github.com/cloudzun/vibe-working
- **文档**: `/home/chengzh/clawd/vibe-working/advanced-topics/`

---

**创建时间**: 2026-03-09  
**维护者**: HuaQloud AI Architect

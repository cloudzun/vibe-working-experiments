# Skill 平台对照说明

> **创建日期**: 2026-03-09  
> **用途**: 明确标注 Skill 适用平台，提供两种格式

---

## 📊 平台差异对比

| 特性 | OpenClaw | OpenCode |
|------|----------|----------|
| **Skill 格式** | YAML (`.yaml`) | Markdown (`SKILL.md`) |
| **Skill 位置** | 项目目录或 `~/.openclaw/skills/` | `~/.config/opencode/skills/` |
| **加载方式** | 自动加载或 `/skill load` | 自动加载（全局目录） |
| **触发机制** | 通过 `triggers` 字段定义 | 通过关键词和上下文 |
| **纪律要求** | `discipline` 字段 | 在文档中明确说明 |

---

## 📁 文件结构

### OpenClaw 格式

```
experiments/rfp-simple/
└── skills/
    ├── rfp-analyzer.yaml         # OpenClaw Skill 定义
    ├── knowledge-searcher.yaml
    └── response-generator.yaml
```

### OpenCode 格式

```
experiments/rfp-simple/
└── skills-opencode/
    ├── rfp-analyzer/
    │   └── SKILL.md              # OpenCode Skill 定义
    ├── knowledge-searcher/
    │   └── SKILL.md
    └── response-generator/
        └── SKILL.md
```

### 全局安装（OpenCode）

```bash
# 复制到全局技能目录
cp -r experiments/rfp-simple/skills-opencode/* ~/.config/opencode/skills/
```

---

## 🎯 使用方式

### OpenClaw 使用方式

```bash
# 1. 加载 Skill（可选，自动加载）
/skill load skills/rfp-analyzer.yaml

# 2. 触发技能
用户："分析 @materials/VanArsdel_RFP.docx"
AI: [自动调用 rfp-analyzer]

# 3. 继续工作流
用户："在产品文档中找答案"
AI: [自动调用 knowledge-searcher]

用户："生成投标文档"
AI: [自动调用 response-generator]
```

### OpenCode 使用方式

**方式 A: 全局安装（推荐）**

```bash
# 安装到全局目录
cp -r experiments/rfp-simple/skills-opencode/rfp-analyzer ~/.config/opencode/skills/
cp -r experiments/rfp-simple/skills-opencode/knowledge-searcher ~/.config/opencode/skills/
cp -r experiments/rfp-simple/skills-opencode/response-generator ~/.config/opencode/skills/

# 在 OpenCode 中使用
用户："分析 materials/VanArsdel_RFP.docx 找出所有需求"
AI: [自动调用 rfp-analyzer SKILL]
```

**方式 B: 项目目录使用**

```bash
# 在实验目录中，让 AI 按照 SKILL.md 规范执行
cd experiments/rfp-simple

# 告诉 AI 参考技能定义
用户："参考 skills-opencode/rfp-analyzer/SKILL.md，分析 RFP"
AI: [按照 SKILL.md 规范执行]
```

**方式 C: 手动执行工作流**

```bash
# Step 1: 分析 RFP
用户："请分析 materials/VanArsdel_RFP.docx，找出所有的需求"

# Step 2: 检索答案
用户："请在产品文档中检索这些需求的答案"

# Step 3: 生成文档
用户："根据上面的需求和答案，生成投标响应文档"
```

---

## 📋 Skill 文件对照表

| 技能名称 | OpenClaw 文件 | OpenCode 文件 | 功能 |
|---------|--------------|---------------|------|
| RFP 分析器 | `skills/rfp-analyzer.yaml` | `skills-opencode/rfp-analyzer/SKILL.md` | 分析 RFP，提取需求 |
| 知识检索器 | `skills/knowledge-searcher.yaml` | `skills-opencode/knowledge-searcher/SKILL.md` | 在产品文档中检索答案 |
| 文档生成器 | `skills/response-generator.yaml` | `skills-opencode/response-generator/SKILL.md` | 生成投标响应文档 |

---

## 🔄 格式转换

### YAML → SKILL.md

**OpenClaw YAML 结构**:
```yaml
---
name: rfp-analyzer
description: 分析 RFP 文档
triggers:
  keywords:
    - "分析 RFP"
    - "找出需求"
discipline:
  - ✅ 只能从提供的材料中检索答案
---
# 角色定义
role: |
  你是一位资深的投标分析专家...
```

**OpenCode SKILL.md 结构**:
```markdown
# rfp-analyzer - RFP 需求分析技能

> **适用平台**: OpenCode

## 📋 技能描述
从 RFP（招标文件）中自动提取需求并分类整理...

## 🎯 触发条件
当用户提到以下关键词时**自动调用**此技能：
- "分析 RFP"
- "找出需求"

## ⚠️ 纪律要求
- ✅ 只能从提供的材料中检索答案
...
```

---

## ✅ 最佳实践

### 1. 明确标注平台

在每个 Skill 文件开头明确标注：

```markdown
> **适用平台**: OpenCode  
> **对应 OpenClaw 版本**: `skills/rfp-analyzer.yaml`
```

或

```yaml
# 适用平台：OpenClaw
# 对应 OpenCode 版本：skills-opencode/rfp-analyzer/SKILL.md
```

### 2. 提供两种格式

为每个 Skill 提供两种格式：
- `.yaml` 用于 OpenClaw
- `SKILL.md` 用于 OpenCode

### 3. 保持同步更新

当修改一个平台的 Skill 时，同步更新另一个平台的对应文件。

### 4. 在文档中说明

在 `README-WORKFLOW.md` 中明确说明：
- 两种平台的区别
- 各自的安装和使用方式
- 文件位置对照

---

## 📚 相关文档

- `README-WORKFLOW.md` - 完整实验手册
- `OPTIMIZATION-REPORT.md` - 优化总结报告
- `OPTIMIZATION-THINKING.md` - 优化思路详解

---

## 📝 更新日志

### v1.0 (2026-03-09)
- ✅ 创建平台对照说明
- ✅ 提供 OpenClaw 和 OpenCode 两种格式
- ✅ 明确标注适用平台
- ✅ 添加安装和使用说明

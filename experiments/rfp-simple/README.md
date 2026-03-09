# RFP Response Agent

> **极简版** - 针对 OpenCode 的 RFP 自动响应工作流

---

## 📦 结构

```
experiments/rfp-simple/
├── skills/                        # Skill 定义（3 个）
│   ├── rfp-analyzer.md           # 分析 RFP
│   ├── knowledge-searcher.md     # 检索答案
│   └── response-generator.md     # 生成文档
├── materials/                     # 输入文件
│   ├── VanArsdel_RFP.docx
│   └── [产品文档...]
├── outputs/                       # 输出文件
│   └── [生成的投标文档]
└── LAB1-MANUAL.md                 # 实验手册
```

---

## 🚀 快速开始

### 1. 安装 Skills

```bash
cd experiments/rfp-simple
cp -r skills/* ~/.config/opencode/skills/
```

### 2. 运行工作流

在 OpenCode 中依次输入：

```
# Step 1: 分析 RFP
请分析 materials/VanArsdel_RFP.docx，找出所有的需求

# Step 2: 检索答案
请在产品文档中检索这些需求的答案

# Step 3: 生成文档
根据上面的需求和答案，生成 Word 格式的投标响应文档
```

### 3. 检查结果

```bash
ls outputs/
# VanArsdel_RFP_Response.docx
```

---

## 📖 详细文档

查看 `LAB1-MANUAL.md` 获取完整实验手册。

---

## 🎯 Skills

| Skill | 触发词 | 功能 |
|-------|--------|------|
| `rfp-analyzer` | "分析 RFP" | 提取并分类需求 |
| `knowledge-searcher` | "找答案" | 检索产品文档 |
| `response-generator` | "生成 Word" | 生成投标文档 |

---

## 🔧 故障排查

**Skill 未找到**:
```bash
ls ~/.config/opencode/skills/
# 确认 Skills 已复制
```

**文件不存在**:
```bash
pwd
ls materials/
# 确认在实验目录
```

**依赖缺失**:
```bash
pip install python-docx openpyxl
```

---

**版本**: v4.0 (2026-03-09)  
**平台**: OpenCode  
**状态**: ✅ 生产就绪

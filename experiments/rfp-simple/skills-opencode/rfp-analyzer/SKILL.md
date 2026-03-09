# rfp-analyzer - RFP 需求分析技能

> **适用平台**: OpenCode  
> **版本**: 2.0  
> **创建日期**: 2026-03-09  
> **对应 OpenClaw 版本**: `skills/rfp-analyzer.yaml`

---

## 📋 技能描述

从 RFP（招标文件）中自动提取需求并分类整理，支持 Word (.docx) 和 PDF 格式。

---

## 🎯 触发条件

当用户提到以下关键词时**自动调用**此技能：

- "分析 RFP"
- "分析招标文件"
- "找出需求"
- "提取需求"
- "RFP 需求"
- "@*.docx"（提到 Word 文档）
- "@materials/*"（提到素材目录）

---

## ⚠️ 纪律要求（必须遵守）

- ✅ **只能从提供的材料中检索答案**
- ❌ **不得编造数据或功能**
- ❌ **不得引用外部知识**（除非用户明确要求网络搜索）
- ⚠️ **找不到答案时**：明确标注"材料中未找到，需人工补充"
- ⚠️ **不确定时**：标注置信度（高/中/低）
- ✅ **所有答案必须标注来源**（文档名 + 章节/页码）

---

## 🔄 工作流程

### Step 1: 确认文件路径
- 如果用户指定了文件，使用指定路径
- 否则尝试默认路径：`materials/*.docx`
- 如果找不到，提示用户切换目录或指定路径

### Step 2: 读取文档
- 使用 `python-docx` 读取 Word 文档
- 或使用 `pypdf` 读取 PDF 文档
- 提取所有段落内容

### Step 3: 识别需求
- 查找列表项（List Bullet 样式）
- 查找动词开头的段落（Deploy/Integrate/Provide/Supply 等）
- 查找包含问号的句子（直接问题）
- 记录每个需求的段落索引和样式

### Step 4: 分类整理
- **技术需求**：产品功能、技术规格、集成要求
- **商务需求**：价格、付款条件、客户案例
- **实施需求**：安装、培训、支持服务
- **其他需求**：无法归类的需求

### Step 5: 输出清单
- 生成 Markdown 格式的需求清单
- 包含分类统计
- 标注每个需求的来源位置

---

## 📤 输出格式

```markdown
## RFP 需求分析

### 技术需求（X 个）
1. [需求内容]
2. [需求内容]
...

### 商务需求（X 个）
1. [需求内容]
2. [需求内容]
...

### 实施需求（X 个）
1. [需求内容]
2. [需求内容]
...

### 其他需求（X 个）
1. [需求内容]
...

---
**总计**: X 个需求
**来源**: [文件名]
**提取时间**: [时间戳]
```

---

## ✅ 质量标准

- 提取所有列表项需求（List Bullet）
- 分类准确率 > 80%
- 不遗漏关键需求
- 每个需求保留原文表述
- 标注清晰的来源位置

---

## 🛠️ 使用示例

### 示例 1: 基本分析

**用户**: "请分析 materials/VanArsdel_RFP.docx 找出所有需求"

**技能输出**:
```markdown
## RFP 需求分析

### 技术需求（9 个）
1. Deploy a scalable energy management platform for hotels and resorts.
2. Integrate IoT sensors, analytics, and automated controls for HVAC, lighting, and plug loads.
...

### 商务需求（5 个）
...

### 实施需求（4 个）
...

---
**总计**: 18 个需求
**来源**: VanArsdel_RFP.docx
```

### 示例 2: 只要技术需求

**用户**: "找出所有的技术需求"

**技能输出**:
```markdown
### 技术需求（9 个）
1. Deploy a scalable energy management platform...
2. Integrate IoT sensors...
...
```

---

## 🐛 异常处理

### 文件不存在
```
❌ 找不到文件：materials/VanArsdel_RFP.docx

可能的原因：
1. 文件路径不正确
2. 当前目录不是实验目录

解决方案：
1. 在实验目录运行：cd experiments/rfp-simple
2. 使用完整路径：/完整/路径/to/file.docx
3. 检查文件是否存在：ls materials/
```

### 未找到需求
```
⚠️ 未提取到任何需求

可能的原因：
1. RFP 文档格式特殊
2. 需求不在标准位置

建议：
1. 手动检查文档结构
2. 调整提取规则
3. 联系文档作者确认格式
```

---

## 📚 相关文件

- **OpenClaw 版本**: `skills/rfp-analyzer.yaml`
- **实验目录**: `experiments/rfp-simple/`
- **测试脚本**: `scripts/extract_questions.py`

---

## 📝 更新日志

### v2.0 (2026-03-09)
- ✅ 添加触发条件定义
- ✅ 添加纪律要求
- ✅ 明确标注适用平台（OpenCode）
- ✅ 添加异常处理说明

### v1.0 (2026-03-06)
- ✅ 初始版本

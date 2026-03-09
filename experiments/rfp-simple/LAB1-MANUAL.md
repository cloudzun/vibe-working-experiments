# Lab 1: RFP Response Agent

> **目标**: 用自然语言让 AI 分析 RFP 并生成投标文档  
> **时间**: 15 分钟  
> **平台**: OpenCode  
> **前提**: 无需写代码

---

## 🎯 场景

你是销售工程师，收到 VanArsdel 公司的 RFP（招标文件）。

**任务**:
1. 理解 20+ 个需求
2. 从产品文档中找到答案
3. 生成投标响应文档

**传统方式**: 2-3 天  
**AI 方式**: 15 分钟

---

## 📦 Skills

已准备好 3 个 Skill（位于 `skills/` 目录）：

| Skill | 功能 | 触发词 |
|-------|------|--------|
| `rfp-analyzer` | 分析 RFP，提取需求 | "分析 RFP" |
| `knowledge-searcher` | 检索产品答案 | "找答案" |
| `response-generator` | 生成投标文档 | "生成 Word" |

---

## 🚀 步骤

### Step 1: 安装 Skills（2 分钟）

```bash
# 1. 进入实验目录
cd experiments/rfp-simple

# 2. 复制 Skills 到 OpenCode 全局目录
cp -r skills/* ~/.config/opencode/skills/

# 3. 验证安装
ls ~/.config/opencode/skills/
# 应该看到：rfp-analyzer, knowledge-searcher, response-generator
```

---

### Step 2: 分析 RFP（3-5 分钟）

**在 OpenCode 中输入**:

```
请分析 materials/VanArsdel_RFP.docx，找出所有的需求并分类整理
```

**预期输出**:

```
## RFP 需求分析

### 技术需求（9 个）
1. Deploy a scalable energy management platform...
2. Integrate IoT sensors...
...

### 商务需求（5 个）
...

### 实施需求（4 个）
...

---
**总计**: 18 个需求
```

**微调**:
- "只要技术需求" → AI 重新输出
- "用表格展示" → AI 转换格式

---

### Step 3: 检索答案（5-7 分钟）

**在 OpenCode 中输入**:

```
现在请在 materials 目录的产品文档中检索答案，
为每个需求找到对应的产品特性或案例支持
```

**预期输出**:

```
## 需求 - 答案对照表

| 需求 | 答案来源 | 置信度 |
|------|---------|--------|
| Deploy scalable platform | Technical_Specifications.docx | 高 |
| Integrate IoT sensors | Technical_Specifications.docx | 高 |
...

✅ 找到 18 个答案
⚠️ 0 个需求需人工补充
```

---

### Step 4: 生成文档（5-7 分钟）

**在 OpenCode 中输入**:

```
根据上面的需求和答案，生成一份专业的 Word 格式投标响应文档
```

**预期输出**:

```
✅ 文档生成完成！

**文件**: VanArsdel_RFP_Response.docx
**位置**: outputs/
**大小**: 42 KB

文档包含：
1. 封面页
2. 执行摘要
3. 技术响应（逐项）
4. 商务响应（含定价）
5. 实施计划
6. 客户案例
```

---

## ✅ 验收

完成后检查：

- [ ] `outputs/VanArsdel_RFP_Response.docx` 存在（40-50 KB）
- [ ] 文档包含 7 个主要章节
- [ ] 所有需求都有响应
- [ ] 每个响应都标注了来源

---

## 🔧 故障排查

### 问题 1: Skill 未找到

**错误**: `Skill "rfp-analyzer" not found`

**解决**:
```bash
# 确认 Skills 已复制
ls ~/.config/opencode/skills/

# 如果不存在，重新复制
cp -r skills/* ~/.config/opencode/skills/

# 重启 OpenCode
```

### 问题 2: 找不到文件

**错误**: `Cannot read binary file: materials/VanArsdel_RFP.docx`

**解决**:
```bash
# 确认在实验目录
pwd
# 应该显示：.../experiments/rfp-simple

# 检查文件存在
ls materials/
```

### 问题 3: python-docx 未安装

**错误**: `ModuleNotFoundError: No module named 'docx'`

**解决**:
```bash
pip install python-docx openpyxl
```

---

## 💡 提示

### 提高准确率

1. **明确文件路径**
   - ✅ "分析 materials/VanArsdel_RFP.docx"
   - ❌ "分析 RFP"

2. **分步骤引导**
   - ✅ "先分析 RFP，然后检索答案，最后生成文档"
   - ❌ "生成投标文档"

3. **提供上下文**
   - ✅ "基于刚才提取的需求，在产品文档中找答案"
   - ❌ "找答案"

### 微调输出

```
"让执行摘要更专业一些"
"精简到 200 字以内"
"用表格形式展示"
"添加项目符号列表"
```

---

## 📚 扩展

完成 Lab 1 后：

1. **尝试其他 RFP**
   - 替换 `materials/VanArsdel_RFP.docx`
   - 准备对应的产品文档

2. **自定义 Skills**
   - 修改 `skills/*.md`
   - 添加行业特定规则

3. **部署到生产**
   - 全局安装 Skills
   - 培训团队成员

---

**版本**: v4.0 (2026-03-09)  
**平台**: OpenCode  
**状态**: ✅ 生产就绪  
**GitHub**: https://github.com/cloudzun/vibe-working-experiments

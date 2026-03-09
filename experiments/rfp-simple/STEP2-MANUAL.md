# Step 2: RFP 问题提取 - 实验手册

**实验目标**：从 RFP 文档中提取所有问题和要求  
**预计时间**：30 分钟  
**输入**：`materials/VanArsdel_RFP.docx`  
**输出**：`extracted_questions.json`

---

## 📝 步骤说明

### 1. 创建 Python 脚本

在实验目录创建 `extract_questions.py`：

```python
"""
RFP 问题提取脚本
从 Word 格式的 RFP 文档中提取所有问题和要求
"""

from docx import Document
import json

# 读取 RFP 文档
print("📖 正在读取 RFP 文档...")
doc = Document('materials/VanArsdel_RFP.docx')

# 提取问题（两种模式）
questions = []

print("🔍 正在分析问题...")
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    
    # 跳过空段落
    if not text:
        continue
    
    # 模式 1：包含问号（直接问题）
    if '?' in text:
        questions.append({
            'id': len(questions) + 1,
            'text': text,
            'type': 'question',
            'section': para.style.name if para.style else 'Normal',
            'paragraph_index': i
        })
    
    # 模式 2：以特定动词开头（隐含要求）
    elif any(text.startswith(v) for v in [
        'Describe', 'Explain', 'Provide', 'List', 'Detail', 
        'Outline', 'Summarize', 'Identify', 'Specify'
    ]):
        questions.append({
            'id': len(questions) + 1,
            'text': text,
            'type': 'requirement',
            'section': para.style.name if para.style else 'Normal',
            'paragraph_index': i
        })

# 保存结果
output_file = 'extracted_requirements.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'source': 'VanArsdel_RFP.docx',
        'total_requirements': len(requirements),
        'requirements': requirements
    }, f, indent=2, ensure_ascii=False)

# 输出统计
print(f"\n✅ 提取完成！")
print(f"📊 共提取到 {len(requirements)} 个需求/要求")
print(f"💾 已保存到：{output_file}")

# 分类统计
questions = [r for r in requirements if r['type'] == 'question']
reqs = [r for r in requirements if r['type'] == 'requirement']
print(f"   - 直接问题：{len(questions)} 个")
print(f"   - 需求列表：{len(reqs)} 个")

# 显示前 5 个示例
if requirements:
    print(f"\n📋 前 5 个示例：")
    for i, r in enumerate(requirements[:5], 1):
        print(f"\n【需求{i}】")
        print(f"类型：{r['type']}")
        print(f"章节：{r['section']}")
        print(f"内容：{r['text'][:100]}...")
```

---

### 2. 运行脚本

```bash
# 确保在正确的目录
cd /home/chengzh/clawd/vibe-working-experiments/experiments/rfp-simple

# 运行脚本
python extract_questions.py
```

---

### 3. 检查结果

**预期输出**：
```
📖 正在读取 RFP 文档...
🔍 正在分析问题...

✅ 提取完成！
📊 共提取到 10-20 个问题/要求
💾 已保存到：extracted_questions.json

📋 前 3 个示例：

【问题 1】
类型：question
内容：Describe your company's experience...

【问题 2】
类型：requirement
内容：Provide a detailed implementation timeline...

【问题 3】
类型：question
内容：What is your pricing model?...
```

---

### 4. 验证 JSON 文件

**查看内容**：
```bash
# 查看文件结构（格式化输出）
cat extracted_questions.json | python3 -m json.tool | head -50

# 或直接用文本编辑器打开
code extracted_questions.json
```

**预期结构**：
```json
{
  "source": "VanArsdel_RFP.docx",
  "total_questions": 15,
  "questions": [
    {
      "id": 1,
      "text": "Describe your company's background...",
      "type": "question",
      "section": "Normal",
      "paragraph_index": 45
    },
    {
      "id": 2,
      "text": "Provide a detailed timeline...",
      "type": "requirement",
      "section": "Heading 2",
      "paragraph_index": 67
    }
  ]
}
```

---

## ✅ 验收标准

### 数量验收
- ✅ 提取到 **20+ 个需求/要求**（实际：21 个）
- ✅ 包含列表项需求（List Bullet 样式）
- ✅ 包含动词开头的要求（Deploy/Integrate/Provide 等）

### 质量验收
- ✅ 每个问题有唯一 ID
- ✅ 标注了问题类型
- ✅ 保留了段落样式信息
- ✅ 人工检查前 5 个问题，相关性 > 80%

### 格式验收
- ✅ JSON 文件格式正确
- ✅ 使用 UTF-8 编码
- ✅ 缩进 2 空格，便于阅读

---

## 🔧 故障排查

### 问题 1：脚本报错 "FileNotFoundError"

**原因**：文件路径错误

**解决**：
```bash
# 确认文件存在
ls -la materials/VanArsdel_RFP.docx

# 如果文件不存在，检查当前目录
pwd
ls -la
```

---

### 问题 2：提取到的问题数量 < 5

**原因**：RFP 文档格式特殊，问题不在段落中

**解决**：
1. 打开 RFP 文档查看实际格式
2. 检查问题是否在表格中
3. 调整提取逻辑（见下方"扩展：表格中的问题"）

---

### 问题 3：提取的问题都是乱码

**原因**：文档编码问题

**解决**：
```python
# 尝试使用不同的编码读取
doc = Document('materials/VanArsdel_RFP.docx', encoding='utf-8')
```

---

## 📊 扩展：如果问题在表格中

如果 RFP 的问题在表格里，添加表格提取逻辑：

```python
# 在原有脚本后添加：

# 提取表格中的问题
table_questions = []
for i, table in enumerate(doc.tables):
    for row in table.rows:
        for cell in row.cells:
            text = cell.text.strip()
            if '?' in text or any(text.startswith(v) for v in [
                'Describe', 'Explain', 'Provide'
            ]):
                table_questions.append({
                    'id': len(questions) + len(table_questions) + 1,
                    'text': text,
                    'type': 'table_question',
                    'table_index': i
                })

print(f"📊 另外从表格中提取到 {len(table_questions)} 个问题")
questions.extend(table_questions)
```

---

## 📝 实验日志

**完成后填写**：

```markdown
## Step 2 实验日志

**开始时间**: [填写时间]
**完成时间**: [填写时间]
**实际耗时**: [X] 分钟

### 运行情况
- 提取到的问题数量：[X] 个
- 直接问题：[X] 个
- 隐含要求：[X] 个
- 表格问题：[X] 个（如有）

### 遇到的问题
1. [问题描述] → [解决方案]

### 人工检查结果
- 前 5 个问题相关性：[X]%
- 是否满足验收标准：✅ 是 / ❌ 否

### 下一步
- [ ] 进入 Step 3：知识检索
```

---

## 🎯 下一步

完成本步骤后：
1. ✅ 提交实验日志
2. ✅ 推送到 GitHub
3. ⏭️ 进入 **Step 3：知识检索**（45 分钟）

---

**手册版本**：v1.0  
**创建时间**：2026-03-09 01:35 UTC  
**适用项目**：vibe-working-experiments

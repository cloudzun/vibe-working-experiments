# 探索性开发计划 - RFP Response Agent（最简版本）

**开发时间**：2026-03-09 01:45 UTC  
**目标**：快速验证可行性，2 小时内跑通端到端流程  
**原则**：使用现有数据、OpenCode 优先、后续复现 OpenClaw  
**项目**：vibe-working-experiments（独立实验项目）

---

## 🎯 为什么选择 RFP Response 场景？

### 素材充足度：100% ✅

| 文件 | 用途 | 状态 |
|------|------|------|
| `VanArsdel_RFP.docx` | RFP 招标文件（输入） | ✅ 已有 |
| `EcoSense_360_Technical_Specifications.docx` | 产品技术规格 | ✅ 已有 |
| `EcoSense_360_Customer_Case_Study.docx` | 客户案例 | ✅ 已有 |
| `EcoSense_360_Sample_Pricing_Sheet.docx` | 定价表 | ✅ 已有 |
| `EcoSense_360_Integration_Compatibility_Guide.docx` | 集成指南 | ✅ 已有 |
| `EcoSense_360_Compliance_Certification_Summary.docx` | 合规认证 | ✅ 已有 |
| `Fabrikam_Historical_RFP_Data.xlsx` | 历史数据（参考） | ✅ 已有 |

**总计**：7 个文件，全部就绪！无需生成 Mock 数据！

---

### 商业价值：10/10 ⭐⭐⭐⭐⭐

- 直接支持销售投标，创造收入
- 节省大量人工时间（通常投标需数天）
- 可复用于多个行业和场景

---

### 技术可行性：80% ✅

- ✅ Word 文档读取（python-docx）
- ✅ 问题提取（AI 理解）
- ✅ 关键词检索（简单算法）
- ✅ 文档生成（python-docx）
- ⚠️ 检索准确性（需验证）

---

## 📋 开发目标（2 小时）

### 最简版本功能

```
输入：VanArsdel_RFP.docx
处理：
  1. 提取 RFP 中的问题列表
  2. 在 5 个产品文档中检索答案
  3. 生成简单的响应文档
输出：rfp_response_simple.docx
```

### 不做的事情（后续迭代）

- ❌ 复杂的合规矩阵
- ❌ 多轮对话优化
- ❌ OpenClaw 集成
- ❌ 精美的格式排版

---

## 🛠️ 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **文档读取** | python-docx | 读取 Word 文档 |
| **问题提取** | AI 理解（bailian） | 识别 RFP 中的问题 |
| **知识检索** | 关键词匹配 | 简单检索算法 |
| **文档生成** | python-docx | 生成 Word 响应 |
| **运行环境** | OpenCode Desktop | 本地 Python 环境 |

---

## 📝 开发步骤（2 小时）

### Step 1：环境准备（15 分钟）

```bash
# 1. 确认 OpenCode Desktop 已安装
which opencode

# 2. 确认 Python 库已安装
pip list | grep -E "docx|pandas"

# 3. 进入实验目录
cd /home/chengzh/clawd/vibe-working-experiments/experiments/rfp-simple

# 4. 复制素材文件（已完成）
# materials/ 目录已包含所有需要的文件
```

---

### Step 2：RFP 问题提取（30 分钟）

**目标**：从 RFP 文档中提取问题列表

**脚本**：`extract_questions.py`

```python
from docx import Document
import json

# 读取 RFP 文档
doc = Document('materials/VanArsdel_RFP.docx')

# 提取问题（简单版本：查找包含问号的段落）
questions = []
for para in doc.paragraphs:
    text = para.text.strip()
    if '?' in text or text.startswith('Describe') or text.startswith('Explain'):
        questions.append({
            'text': text,
            'section': para.style.name if para.style else 'Normal'
        })

# 保存问题列表
with open('extracted_questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

print(f"提取到 {len(questions)} 个问题/要求")
print(f"示例：{questions[0]['text'][:100]}...")
```

**验收标准**：
- ✅ 提取到 10+ 个问题/要求
- ✅ 保存到 JSON 文件
- ✅ 人工检查提取质量

---

### Step 3：知识检索（45 分钟）

**目标**：对每个问题，在 5 个产品文档中检索相关信息

**脚本**：`knowledge_search.py`

```python
from docx import Document
import json

# 加载问题列表
with open('extracted_questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# 读取产品文档（构建简单索引）
product_docs = {
    'technical': Document('materials/EcoSense_360_Technical_Specifications.docx'),
    'case_study': Document('materials/EcoSense_360_Customer_Case_Study.docx'),
    'pricing': Document('materials/EcoSense_360_Sample_Pricing_Sheet.docx'),
    'integration': Document('materials/EcoSense_360_Integration_Compatibility_Guide.docx'),
    'compliance': Document('materials/EcoSense_360_Compliance_Certification_Summary.docx')
}

# 简单关键词检索
def search_keywords(question, docs):
    # 提取问题中的关键词（去掉停用词）
    keywords = [w.lower() for w in question.split() if len(w) > 3]
    
    results = []
    for doc_name, doc in docs.items():
        for para in doc.paragraphs:
            text = para.text.lower()
            # 计算关键词匹配数
            match_count = sum(1 for kw in keywords if kw in text)
            if match_count >= 2:  # 至少匹配 2 个关键词
                results.append({
                    'source': doc_name,
                    'content': para.text.strip()[:200],  # 截取前 200 字
                    'relevance': match_count
                })
    
    # 按相关性排序
    results.sort(key=lambda x: x['relevance'], reverse=True)
    return results[:5]  # 返回 Top 5 结果

# 对每个问题检索答案
answers = []
for q in questions:
    search_results = search_keywords(q['text'], product_docs)
    answers.append({
        'question': q['text'],
        'answers': search_results
    })

# 保存检索结果
with open('search_results.json', 'w', encoding='utf-8') as f:
    json.dump(answers, f, indent=2, ensure_ascii=False)

print(f"完成 {len(answers)} 个问题的检索")
```

**验收标准**：
- ✅ 每个问题返回 3-5 个相关段落
- ✅ 标注来源文档
- ✅ 按相关性排序

---

### Step 4：生成响应文档（30 分钟）

**目标**：将检索结果组织成 Word 响应文档

**脚本**：`generate_response.py`

```python
from docx import Document
import json

# 加载检索结果
with open('search_results.json', 'r', encoding='utf-8') as f:
    answers = json.load(f)

# 创建响应文档
response = Document()
response.add_heading('RFP 响应文档', 0)
response.add_paragraph('基于 VanArsdel RFP 的自动响应')

# 逐个回答问题
for i, item in enumerate(answers, 1):
    response.add_heading(f'问题 {i}', level=1)
    response.add_paragraph(item['question'], style='Intense Quote')
    
    response.add_heading('参考答案:', level=2)
    for j, ans in enumerate(item['answers'], 1):
        p = response.add_paragraph()
        p.add_run(f'[{ans["source"]}] ').bold = True
        p.add_run(ans['content'])
    
    response.add_page_break()

# 保存文档
response.save('rfp_response_simple.docx')
print("✅ 响应文档已生成：rfp_response_simple.docx")
```

**验收标准**：
- ✅ 生成 Word 文档
- ✅ 包含所有问题和答案
- ✅ 标注答案来源
- ✅ 格式清晰可读

---

## ✅ 验收标准

### 功能验收

| 步骤 | 输入 | 输出 | 验收标准 |
|------|------|------|---------|
| 问题提取 | VanArsdel_RFP.docx | extracted_questions.json | 10+ 个问题 |
| 知识检索 | questions + 5 产品文档 | search_results.json | 每问题 3-5 答案 |
| 文档生成 | search_results.json | rfp_response_simple.docx | 格式清晰、来源标注 |

### 质量验收

- ✅ **准确性**：人工抽查 5 个问题，答案相关性 > 60%
- ✅ **完整性**：所有 RFP 问题都有回答
- ✅ **可用性**：生成的文档可直接作为投标草稿基础

### 时间验收

- ⏱️ **总耗时**：< 2 小时
- ⏱️ **单问题处理**：< 1 分钟

---

## 📊 预期结果

### 生成的响应文档结构

```
RFP 响应文档
├── 问题 1: [RFP 中的第一个问题]
│   ├── 参考答案:
│   │   ├── [technical] 技术规格文档中的相关内容...
│   │   ├── [case_study] 客户案例中的相关内容...
│   │   └── [pricing] 定价表中的相关内容...
├── 问题 2: [RFP 中的第二个问题]
│   └── ...
└── ...（共 10-20 个问题）
```

### 示例输出

```markdown
# 问题 1

> Describe your product's energy savings compared to traditional HVAC systems.

## 参考答案:

**[technical]** Our EcoSense 360 system achieves 30-40% energy savings through advanced AI-driven optimization...

**[case_study]** Trey Research reported 35% reduction in energy costs after 6 months of deployment...

**[pricing]** ROI typically achieved within 18-24 months based on average energy savings...
```

---

## 🚀 后续迭代（如果最简版本成功）

### Iteration 1：提升检索准确性（+2 小时）

- 使用 AI 理解替代关键词匹配
- 添加语义相似度计算
- 支持多轮对话澄清

### Iteration 2：OpenClaw 集成（+4 小时）

- 编写 SOUL.md 和 SKILL.md
- 配置 sessions_spawn
- 测试 Discord 交互

### Iteration 3：完整功能（+8 小时）

- 合规矩阵生成（Excel）
- 定价响应自动生成
- 精美的 Word 格式

---

## 🎯 成功标准

### ✅ 最低成功

- 跑通端到端流程
- 生成可阅读的响应文档
- 验证技术可行性

### ✅ 理想成功

- 答案相关性 > 70%
- 处理时间 < 5 分钟
- 文档可直接使用（需人工审核）

### ⚠️ 失败条件

- 问题提取失败（< 5 个问题）
- 检索结果完全不相关
- 文档生成报错

---

## 📝 记录与复盘

### 开发日志模板

```markdown
# RFP Response 探索性开发日志

**日期**: 2026-03-09
**开发者**: [姓名]
**耗时**: [X] 小时

## 遇到的问题

1. [问题描述] → [解决方案]
2. ...

## 关键发现

- [发现 1]
- [发现 2]

## 下一步计划

- [ ] [任务 1]
- [ ] [任务 2]
```

---

## 🔗 相关文件

- **素材目录**: `materials/`（本目录下）
- **实验目录**: `experiments/rfp-simple/`
- **主项目**: `/home/chengzh/clawd/vibe-working/`

---

**开发计划完成时间**: 2026-03-09 01:45 UTC  
**预计开始时间**: 立即  
**预计完成时间**: 2 小时后

🚀 准备好开始了吗？

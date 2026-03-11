# Skill 自动化实验手册

> **版本**：v2.0  
> **适用项目**：vibe-working-experiments  
> **最后更新**：2026-03-09  
> **目标读者**：希望通过动手实验理解 AI Skill 自动化原理的学习者

---

## 目录

1. [实验概述与学习目标](#1-实验概述与学习目标)
2. [两条实验路径说明](#2-两条实验路径说明)
3. [环境准备](#3-环境准备)
4. [路径 A：分步执行模式（推荐初学者）](#4-路径-a分步执行模式推荐初学者)
   - 4.1 [Step 1：RFP 问题提取](#41-step-1rfp-问题提取)
   - 4.2 [Step 2：知识库检索](#42-step-2知识库检索)
   - 4.3 [Step 3：投标响应书生成](#43-step-3投标响应书生成)
   - 4.4 [独立技能：客服案例分析](#44-独立技能客服案例分析)
5. [路径 B：一键执行模式（适合生产使用）](#5-路径-b一键执行模式适合生产使用)
6. [输出文件详解](#6-输出文件详解)
7. [质量验证检查表](#7-质量验证检查表)
8. [脚本解决了哪些问题](#8-脚本解决了哪些问题)
9. [故障排查](#9-故障排查)
10. [进阶用法](#10-进阶用法)

---

## 1. 实验概述与学习目标

本实验使用一个真实的商业场景（**投标响应自动化**）演示 AI Skill 的完整生命周期：

```
RFP 招标书 + 产品知识库
        ↓
  [Skill 流水线]
        ↓
  结构化投标响应书
```

### 使用的材料

| 文件 | 类型 | 说明 |
|------|------|------|
| `materials/VanArsdel_RFP.txt` | 招标书 | VanArsdel, Ltd. 发出的能源管理采购需求 |
| `materials/EcoSense_360_Technical_Specifications.txt` | 知识库 | EcoSense 360 技术规格书 |
| `materials/EcoSense_360_Customer_Case_Study.txt` | 知识库 | EcoSense 360 客户案例 |
| `materials/EcoSense_360_Sample_Pricing_Sheet.txt` | 知识库 | EcoSense 360 定价说明 |

### 完成实验后，你将能够

- [ ] 理解 SKILL.md 的作用及其局限性
- [ ] 使用脚本复现完整的投标响应流水线
- [ ] 读懂 JSON 中间数据，验证每步结果
- [ ] 解释为什么脚本比纯 AI 执行更可靠
- [ ] 根据 `SKILL_TUTORIAL.md` 自己创建一个新的 Skill

---

## 2. 两条实验路径说明

本实验提供两种执行方式，学习目的不同：

| | 路径 A：分步执行 | 路径 B：一键执行 |
|--|----------------|----------------|
| **适合** | 初次学习、理解原理 | 熟悉后、实际使用 |
| **命令数** | 3 条独立命令 | 1 条命令 |
| **可见度** | 每步暂停，可逐步检查 | 全程自动，最后查看汇总 |
| **推荐顺序** | 先做路径 A，再做路径 B | 在路径 A 之后 |
| **断点续跑** | 手动跳过已完成步骤 | `--skip-extract` / `--skip-search` |

**建议**：第一次实验从路径 A 开始，完整跑一遍并检查每步输出；理解后再用路径 B 一键复现，感受脚本编排的价值。

---

## 3. 环境准备

### 3.1 Python 版本

```
Python >= 3.9
```

```powershell
python --version
```

### 3.2 安装可选依赖

核心功能**仅需 Python 标准库**。以下依赖为可选增强：

```powershell
cd d:\vibedrone\vibe-working-experiments
pip install -r requirements.txt
```

| 包 | 作用 | 不安装时 |
|----|------|---------|
| `python-docx>=1.1.0` | 读取 `.docx` 格式 RFP 和知识库；导出 Word 格式投标书 | 只处理 `.txt`/`.md`；不生成 `.docx` 输出 |
| `openpyxl>=3.1.0` | 读取 `.xlsx` 客服工单数据 | `analyze.py` 报错并提示安装 |

### 3.3 确认工作目录

**所有命令从项目根目录执行**：

```powershell
cd d:\vibedrone\vibe-working-experiments
# 确认位置
dir materials
```

预期看到 4 个 `EcoSense_360` 文件和 `VanArsdel_RFP.*`。

---

## 4. 路径 A：分步执行模式（推荐初学者）

### 4.1 Step 1：RFP 问题提取

**技能脚本**：`skills/rfp-question-extractor/scripts/extract.py`  
**对应 SKILL.md**：`skills/rfp-question-extractor/SKILL.md`

#### 技术说明

脚本严格按 SKILL.md 定义的 6 步执行，每步打印带编号的日志：

```
[1/6] 读取文档       → 支持 .txt / .md / .docx，纯文本直读，.docx 需 python-docx
[2/6] 章节识别       → 正则检测"1. Section"、"## Heading"、全大写行三类标题
[3/6] 问题提取       → 双层识别：显式触发词 + 章节上下文默认类型
[4/6] 分配编号       → Q-001, Q-002 … 全局连续
[5/6] 依赖关系分析   → 8 个主题关键词组，同主题 Q 间生成依赖提示
[6/6] 写入输出       → JSON（机器用）+ Markdown（人工阅读）
```

**问题识别逻辑（理解这个是关键）**：

脚本使用两层识别，任意一层命中即提取该行：

```
第一层：显式触发词
  🔴 直接问题   → 行末有"?" 或含 please describe/provide/list 等
  🟡 硬性要求   → 含 must/shall/required 或行首是动作动词(Deploy/Supply/Ensure…)
  🟢 期望描述   → 含 should/preferred/recommended 等
  🔵 资质门槛   → 含 at least/minimum/demonstrated/references/certified 等

第二层：章节上下文默认类型（v1.1 新增）
  "Project Objectives" / "Scope of Work" → 默认 🟡 硬性要求
  "Technical Requirements"               → 默认 🟡 硬性要求
  "Vendor Qualifications"                → 默认 🔵 资质门槛
  "Evaluation Criteria"                  → 默认 🟢 期望描述
  "Proposal Submission"                  → 默认 🟡 硬性要求
```

> **为什么需要第二层**？RFP 中很多真实需求不含触发词，例如：
> `Cloud-based management portal with mobile access`（没有"must"，但显然是需求）。
> 第二层保证这类短语在已知需求章节内不被遗漏。

**VanArsdel RFP 识别结果**：

| 章节 | 识别问题数 | 默认类型 |
|------|----------|---------|
| Project Objectives | 4 | 🟡 |
| Scope of Work | 4 | 🟡 |
| Technical Requirements | 5 | 🟡 |
| Vendor Qualifications | 3 | 🔵 |
| Proposal Submission | 2 | 🟡 |
| Evaluation Criteria | 5 | 🟢 |
| **合计** | **23** | |

#### 运行命令

```powershell
python skills/rfp-question-extractor/scripts/extract.py materials/VanArsdel_RFP.txt
```

自定义输出目录：

```powershell
python skills/rfp-question-extractor/scripts/extract.py `
    materials/VanArsdel_RFP.txt `
    --output-dir outputs
```

#### 预期输出日志

```
📄 RFP Question Extractor
   Input: materials\VanArsdel_RFP.txt

[1/6] 读取文档...
      ✓ 2589 字符
[2/6] 识别章节结构...
      ✓ 10 个章节
         · 2. Project Objectives  (4 行内容)
         · 3. Scope of Work  (4 行内容)
         · ...
[3/6] 提取并分类问题...
      ✓ 硬性要求: 17 个
      ✓ 资质门槛: 4 个
      ✓ 期望描述: 2 个
[4/6] 分配编号...
      ✓ Q-001 ~ Q-023
[5/6] 分析依赖关系...
      ✓ 6 组依赖
[6/6] 写入输出文件...
      ✓ outputs\01_rfp_questions.json
      ✓ outputs\01_RFP_Questions.md

🎉 完成！共提取 23 个问题
```

#### 检查输出：读懂 JSON 中间件

```powershell
# 快速查看所有提取的问题
python -c "
import json
data = json.load(open('outputs/01_rfp_questions.json', encoding='utf-8'))
print(f'共 {data[\"total\"]} 个问题:')
for q in data['questions']:
    print(f'  {q[\"id\"]} {q[\"type_icon\"]} [{q[\"section\"][:25]}] {q[\"original\"][:55]}')
"
```

JSON 单条结构解析：

```json
{
  "id":         "Q-009",              ← 唯一编号
  "type":       "hard_req",           ← 内部类型键
  "type_icon":  "🟡",                 ← 显示用图标
  "type_label": "硬性要求",            ← 显示用标签
  "section":    "4. Technical Requirements",  ← 所属章节
  "original":   "Support for wireless IoT sensors ...",  ← 原文
  "summary":    "Support for wireless IoT sensors ...",  ← 摘要（≤100字）
  "hint":       "需确认传感器类型、通讯协议及覆盖范围",    ← 响应要点提示
  "priority":   "高"                  ← 优先级
}
```

#### Step 1 验证清单

完成后打开 `outputs/01_RFP_Questions.md`，逐项勾选：

- [ ] 问题总数为 **23** 个
- [ ] "原文摘要"列内容是 RFP 原文，未被改写，加了引号
- [ ] 所有 6 个已知章节（Project Objectives、Scope of Work 等）都有对应问题，无章节遗漏
- [ ] 编号 Q-001 ~ Q-023 连续，无跳跃
- [ ] "问题依赖关系"章节有 6 条内容
- [ ] "建议响应顺序"章节有 4 条内容

---

### 4.2 Step 2：知识库检索

**技能脚本**：`skills/knowledge-searcher/scripts/search_kb.py`  
**对应 SKILL.md**：`skills/knowledge-searcher/SKILL.md`  
**前提**：Step 1 已完成（`outputs/01_rfp_questions.json` 存在）

#### 技术说明

```
[1/5] 扫描知识库   → 遍历目录，按段落切块，记录 {section, text}
[2/5] 加载问题     → 从 JSON 读取全部问题
[3/5] 逐题检索     → 每个问题抽取关键词 → 对所有块评分 → 取 Top-3 命中
[4/5] 匹配评级     → 按分数阈值分级，打印汇总统计
[5/5] 写入输出     → JSON + Markdown 报告
```

**关键词提取规则**：

```python
# 多词技术术语（保留原形）
_MULTI_TERM: sso, tls/ssl, iso 27001, open api, iot, hvac, leed, energy star,
             demand response, predictive maintenance, real-time, ...

# 单词规则
长度 >= 4 个字符 + 不在停用词表（the/for/must/shall/provide/...）中
```

**评分机制（score_chunk）**：

```
score = 命中关键词数 / 总关键词数

阈值：
  score >= 0.55  →  ✅ 完全匹配   （关键词覆盖超过一半以上）
  score >= 0.15  →  ⚠️ 部分匹配
  score <  0.15  →  ❌ 未找到
```

**原文摘录机制（best_verbatim_quote）**：

```
1. 将块文本按句号/感叹号/问号切成句子列表
2. 对每个句子计算关键词命中密度
3. 返回密度最高句的原文切片（不改写、不概括）
4. 最大长度 350 字符
```

**防自引用（`--exclude`）**：

```
问题：知识库目录和 RFP 文件在同一目录时，搜索会匹配到 RFP 原文，
      导致"从招标书自己回答自己"，答案不来自产品文档。

解决：--exclude <file> 排除指定文件。支持多个值：
      --exclude materials/VanArsdel_RFP.txt materials/VanArsdel_RFP_Questions.md
      
      文件的任何同名不同扩展名变体（如 .docx）也会被自动排除。
```

#### 运行命令

```powershell
python skills/knowledge-searcher/scripts/search_kb.py `
    materials/ `
    --questions outputs/01_rfp_questions.json `
    --exclude materials/VanArsdel_RFP.txt
```

> 如果知识库和 RFP 在**不同目录**，可以省略 `--exclude`：
> ```powershell
> python skills/knowledge-searcher/scripts/search_kb.py `
>     C:\MyCompany\ProductDocs\ `
>     --questions outputs/01_rfp_questions.json
> ```

#### 预期输出日志

```
🔍 Knowledge Base Searcher

[1/5] 扫描知识库，建立索引...
      扫描: EcoSense_360_Customer_Case_Study.txt    ✓ 33 段
      扫描: EcoSense_360_Technical_Specifications.txt  ✓ 37 段
      扫描: EcoSense_360_Sample_Pricing_Sheet.txt   ✓ 8 段
      跳过 (已排除): VanArsdel_RFP.txt
      跳过 (已排除): VanArsdel_RFP.docx
      ...
      ✓ 共 7 份文档
[2/5] 加载问题清单...
      ✓ 23 个问题
[3/5] 逐题检索...
      Q-001 ✅ (完全匹配) — EcoSense_360_Technical_Specifications.txt
      Q-002 ✅ (完全匹配) — EcoSense_360_Technical_Specifications.txt
      ...
[4/5] 匹配评级汇总...
      ✅ 完全匹配 17 (74%)
      ⚠️  部分匹配 5 (22%)
      ❌ 未找到   1 (4%)
```

#### 检查输出：读懂检索 JSON

```powershell
# 查看哪些问题未完全命中
python -c "
import json
data = json.load(open('outputs/02_search_results.json', encoding='utf-8'))
for r in data['results']:
    if r['status'] != 'full_match':
        print(r['question_id'], r['status_icon'], r['source_doc'] or '无来源', r['question_text'][:50])
"
```

单条检索结果结构：

```json
{
  "question_id":    "Q-011",
  "question_text":  "Secure communications (TLS/SSL), data encryption...",
  "status":         "full_match",
  "status_icon":    "✅",
  "source_doc":     "EcoSense_360_Technical_Specifications.txt",
  "source_section": "5. Security & Compliance",
  "best_quote":     "EcoSense 360 uses TLS 1.2+ for all data in transit...",
  "keywords":       ["tls", "ssl", "encryption", "iso 27001", "secure"],
  "answer_draft":   "我司郑重承诺，完全满足本项技术要求..."
}
```

#### Step 2 验证清单

打开 `outputs/02_Knowledge_Search_Report.md`，逐项勾选：

- [ ] 扫描文档列表中**没有** `VanArsdel_RFP.txt`（已正确排除）
- [ ] 每个 ✅ 条目都有 `来源文档` 字段（格式：`` `文件名` ＞ 章节名 ``）
- [ ] "相关原文摘录"是引用块格式（以 `>` 开头），是文档原文，**不是** AI 编写的答案
- [ ] ✅+⚠️ 合计占比 > 50%（否则知识库可能不匹配）
- [ ] 所有 ❌ 和 ⚠️ 问题列入了"需人工补充"表格

---

### 4.3 Step 3：投标响应书生成

**技能脚本**：`skills/proposal-generator/scripts/generate.py`  
**对应 SKILL.md**：`skills/proposal-generator/SKILL.md`  
**前提**：Step 1、Step 2 均已完成

#### 技术说明

```
[1/5] 加载数据     → 合并两个 JSON（问题 + 检索结果），建立 question_id 映射
[2/5] 内容梳理     → 按 section 字段重排（确保与 RFP 章节顺序一致）
[3/5] 回答润色     → polish_answer()：移除草稿前缀 → 加正式开场白 → 按类型选风格
[4/5] 质量自检     → 统计占位符数、章节覆盖数、打印摘要
[5/5] 文件生成     → .md（始终生成）+ .docx（需 python-docx，文件被锁时输出警告不崩溃）
```

**回答润色规则（按问题类型）**：

| 问题类型 | 正式开场白 |
|---------|-----------|
| 🟡 硬性要求 | 我司郑重承诺，**完全满足**本项技术要求，具体实现方式如下 |
| 🔵 资质门槛 | 我司在相关领域拥有丰富的实战经验及完整的资质体系，具体情况如下 |
| 🔴 直接问题 | 针对贵司的提问，我司作出如下详细说明 |
| 🟢 期望描述 | 我司在此方面的能力不仅满足基本要求，更具有以下差异化优势 |

**占位符规范**：

```
当某问题的检索结果为 not_found 时，响应书中自动插入：
[待补充：需相关团队在终稿提交前补充说明]

提交前：全局搜索"待补充"定位所有占位符，人工补全。
```

#### 运行命令

```powershell
python skills/proposal-generator/scripts/generate.py `
    --client "VanArsdel, Ltd." `
    --project "Smart Energy Management Solution"
```

指定所有参数：

```powershell
python skills/proposal-generator/scripts/generate.py `
    --questions     outputs/01_rfp_questions.json `
    --search-results outputs/02_search_results.json `
    --client  "VanArsdel, Ltd." `
    --project "Smart Energy Management Solution" `
    --output-dir outputs
```

#### 预期输出日志

```
📝 Proposal Generator

[1/5] 加载数据...
      ✓ 23 个问题，23 条检索结果
[2/5] 内容梳理（按 RFP 章节顺序排列）...
      · 2. Project Objectives (4 个)
      · 3. Scope of Work (4 个)
      · 4. Technical Requirements (5 个)
      · 5. Vendor Qualifications (3 个)
      · 6. Proposal Submission Instructions (2 个)
      · 7. Evaluation Criteria (5 个)
[3/5] 回答润色（口语化 → 正式商务语体）...
      ✓ 润色 23 个回答
[4/5] 质量自检...
      ✓ 完全匹配 17  部分匹配 5  未找到 1
      ✓ 待补充占位符：1 个
      ✓ 章节覆盖：6 章
[5/5] 生成文件...
      ✓ Markdown: outputs\03_Proposal_Response.md
      ✓ Word 文档: outputs\03_Proposal_Response.docx

🎉 投标响应书生成完成！
   ⚠️  1 个问题需人工补充（搜索文档中的「待补充」）
```

#### Step 3 验证清单

打开 `outputs/03_Proposal_Response.md`，逐项勾选：

- [ ] 文档以正式致辞开头
- [ ] 共 6 个章节，与 RFP 章节顺序一致
- [ ] 每个响应条目有"**甲方要求**"（原文引用）和"**我方响应**"两部分
- [ ] 关键技术参数已加粗（如 `**TLS 1.2+**`、`**ISO 27001**`）
- [ ] 搜索"待补充"——确认已知晓所有需人工补充的条目
- [ ] 文档末尾有"质量自检"表格

---

### 4.4 独立技能：客服案例分析

**技能脚本**：`skills/support-case-analyzer/scripts/analyze.py`  
**对应 SKILL.md**：`skills/support-case-analyzer/SKILL.md`

此技能**独立于**投标流水线，用于分析客服工单数据（Excel/CSV）。

#### 技术说明

```
[1/7] 读取数据    → 验证 8 个必要字段，读取每一行
[2/7] 总量统计    → 案例数、时间跨度（最早 ~ 最晚 Date Opened）
[3/7] 高频问题    → 按 Issue Type 分组计数，排序取 Top-3
[4/7] 严重程度    → Critical/High/Medium/Low 各自计数和占比
[5/7] 解决效率    → 全局平均 + 按 Issue Type 分组平均 Resolution Time
[6/7] 升级率      → Escalated=Yes 占比，识别升级率最高类型
[7/7] 改进建议    → 基于数据点生成 3-5 条具体建议
```

**必要字段（8个，缺任一报错）**：

| 字段名 | 示例值 |
|--------|--------|
| `Customer` | Fabrikam, Inc. |
| `Case ID` | CASE-20240315-001 |
| `Date Opened` | 2024-03-15 |
| `Issue Type` | Bug Report |
| `Module` | Energy Dashboard |
| `Severity` | High |
| `Resolution Time (hrs)` | 4.5 |
| `Escalated` | Yes |

**运行命令**：

```powershell
# 使用自己准备的 Excel 文件
python skills/support-case-analyzer/scripts/analyze.py data/cases.xlsx

# 支持 CSV 格式（无需 openpyxl）
python skills/support-case-analyzer/scripts/analyze.py data/cases.csv
```

> **注意**：`materials/Fabrikam_Historical_RFP_Data.xlsx` 是历史 RFP 数据（字段为 `RFP ID, Date, Industry`），
> 不是客服工单格式，无法直接用于此技能。需要准备符合上述 8 字段的 Excel 文件。

---

## 5. 路径 B：一键执行模式（适合生产使用）

**脚本**：`skills/bid-response-agent/scripts/run_pipeline.py`  
**对应 SKILL.md**：`skills/bid-response-agent/SKILL.md`

路径 B 在一条命令内依次调用路径 A 的三个脚本，额外提供：
- **自动防自引用**：RFP 文件自动加入 `--exclude` 列表
- **执行摘要**：自动生成含匹配统计的 `04_Executive_Summary.md`
- **断点续跑**：通过 `--skip-*` 跳过已完成步骤，节省迭代时间

### 5.1 基础运行

```powershell
python skills/bid-response-agent/scripts/run_pipeline.py `
    materials/VanArsdel_RFP.txt `
    materials/ `
    --client "VanArsdel, Ltd." `
    --project "Smart Energy Management Solution"
```

### 5.2 完整参数说明

| 参数 | 是否必填 | 默认值 | 说明 |
|------|---------|--------|------|
| `rfp_file` | ✅ | — | RFP 文档路径（`.txt`/`.md`/`.docx`）|
| `kb_dir` | ✅ | — | 知识库目录路径 |
| `--client` | ❌ | `客户` | 甲方公司名（出现在投标书抬头）|
| `--project` | ❌ | `项目` | 项目名称 |
| `--output-dir` | ❌ | `outputs` | 输出目录（每个项目建议使用独立目录）|
| `--skip-extract` | ❌ | `False` | 跳过 Step 1，使用已有 `01_rfp_questions.json` |
| `--skip-search` | ❌ | `False` | 跳过 Step 2，使用已有 `02_search_results.json` |

### 5.3 典型使用场景

**场景 1：全新项目，完整跑**

```powershell
python skills/bid-response-agent/scripts/run_pipeline.py `
    C:\Projects\ClientA_RFP.docx `
    C:\Knowledge\ProductDocs\ `
    --client "Client A" --project "Project X" `
    --output-dir outputs/client_a
```

**场景 2：已有问题列表，只需重新检索 + 生成**

```powershell
python skills/bid-response-agent/scripts/run_pipeline.py `
    materials/VanArsdel_RFP.txt materials/ `
    --skip-extract
```

**场景 3：已有检索结果，只需重新生成（调整客户名称等）**

```powershell
python skills/bid-response-agent/scripts/run_pipeline.py `
    materials/VanArsdel_RFP.txt materials/ `
    --client "VanArsdel, Ltd." --project "Smart Energy Management Solution" `
    --skip-extract --skip-search
```

### 5.4 预期最终输出

```
📁 输出目录: D:\vibedrone\vibe-working-experiments\outputs
     01_RFP_Questions.md            RFP 问题清单
     01_rfp_questions.json          流水线中间数据
     02_Knowledge_Search_Report.md  知识库检索报告
     02_search_results.json         流水线中间数据
     03_Proposal_Response.md        投标响应书（主文档）
     03_Proposal_Response.docx      Word 格式（需 python-docx）
     04_Executive_Summary.md        执行摘要 + 下一步清单
```

打开 `outputs/04_Executive_Summary.md` 查看执行统计和下一步行动清单。

---

## 6. 输出文件详解

### 6.1 文件对应关系

| 文件 | 产生脚本 | 格式 | 用途 |
|------|---------|------|------|
| `01_RFP_Questions.md` | extract.py | Markdown | 问题清单，人工阅读 |
| `01_rfp_questions.json` | extract.py | JSON | 流水线中间数据，机器消费 |
| `02_Knowledge_Search_Report.md` | search_kb.py | Markdown | 检索报告，含原文证据 |
| `02_search_results.json` | search_kb.py | JSON | 流水线中间数据 |
| `03_Proposal_Response.md` | generate.py | Markdown | 投标响应书初稿 |
| `03_Proposal_Response.docx` | generate.py | Word | 可排版提交的版本 |
| `04_Executive_Summary.md` | run_pipeline.py | Markdown | 执行摘要 + 行动清单 |

### 6.2 JSON 中间数据详细结构

**`01_rfp_questions.json`**

```json
{
  "source_file": "materials/VanArsdel_RFP.txt",
  "extracted_at": "2026-03-09T10:00:00",
  "total": 23,
  "questions": [
    {
      "id": "Q-009",
      "type": "hard_req",
      "type_icon": "🟡",
      "type_label": "硬性要求",
      "section": "4. Technical Requirements",
      "original": "Support for wireless IoT sensors (temperature, occupancy, humidity, light, CO2).",
      "summary": "Support for wireless IoT sensors (temperature, occupancy...",
      "hint": "需确认传感器类型、通讯协议及覆盖范围",
      "priority": "高"
    }
  ],
  "dependencies": [
    "Q-006 依赖 Q-012（均涉及「API 集成」，答案应保持一致）"
  ]
}
```

**`02_search_results.json`**

```json
{
  "kb_path": "materials",
  "searched_at": "2026-03-09T10:01:00",
  "results": [
    {
      "question_id": "Q-009",
      "question_text": "Support for wireless IoT sensors...",
      "question_type": "hard_req",
      "keywords": ["wireless", "iot", "sensors", "temperature", "occupancy", "humidity"],
      "status": "full_match",
      "status_icon": "✅",
      "status_label": "完全匹配",
      "source_doc": "EcoSense_360_Technical_Specifications.txt",
      "source_section": "3. Key Features & Capabilities",
      "best_quote": "Wireless IoT Sensors: Supports temperature, occupancy, humidity, light, and CO2 sensors via Zigbee, Wi-Fi, and Bluetooth LE protocols.",
      "top_hits": [
        {"doc": "EcoSense_360_Technical_Specifications.txt", "section": "...", "score": 0.714, "matched": ["wireless", "iot", ...]}
      ],
      "answer_draft": "我司郑重承诺，完全满足本项技术要求..."
    }
  ]
}
```

---

## 7. 质量验证检查表

### 7.1 Step 1 质量

- [ ] `01_rfp_questions.json` 已生成，问题总数为 23
- [ ] 覆盖所有 6 个已知需求章节，无章节完全遗漏
- [ ] "原文摘要"保持 RFP 原文语言（英文 RFP 摘要仍为英文）
- [ ] 有依赖关系输出（至少 1 条）

### 7.2 Step 2 质量

- [ ] `02_search_results.json` 已生成
- [ ] 扫描文档列表中没有 `VanArsdel_RFP.txt`（已排除）
- [ ] 每个 ✅ 结果的 `best_quote` 是原文切片（以原文语言书写）
- [ ] `source_section` 字段有具体章节名（不只是 `Document`）
- [ ] 命中率（✅+⚠️）> 50%

### 7.3 Step 3 质量

- [ ] `03_Proposal_Response.md` 已生成
- [ ] 章节数量 = 6（与 RFP 章节数一致）
- [ ] 每条响应有"**甲方要求**"和"**我方响应**"两部分
- [ ] 搜索"待补充"——数量应与 Step 2 中 ❌ 数量一致
- [ ] 文档末尾有质量自检表格

---

## 8. 脚本解决了哪些问题

### 8.1 AI 直接执行 SKILL.md 时的常见偏差

```
SKILL.md 是"菜谱"，AI 是"厨师"。
厨师可以决定某些步骤"可以省略"——脚本拥有菜谱的执行权。
```

| AI 手动执行的偏差 | 发生原因 | 脚本的解决方式 |
|----------------|---------|--------------|
| 跳过依赖关系分析 | AI 认为"可选" | 步骤 5 是固定函数调用，无法跳过 |
| 原文引用被改写/概括 | AI 倾向流畅表达 | `best_verbatim_quote()` 直接切片原文 |
| 出处只标文档名，不标章节 | AI 模糊索引 | 每个 chunk 记录 `{section, text}`，命中即带出章节 |
| 遗漏无触发词的条目 | 靠关键词配对 | `section_default_type()` 对已知需求章节整体兜底 |
| 输出 `.md` 而非 `.docx` | 走最简路径 | `save_docx()` 明确调用 python-docx |
| 每次结果不同 | 语言模型有随机性 | Python 脚本 = 确定性函数，相同输入→相同输出 |

### 8.2 "脚本+AI"最佳分工

```
脚本负责：流程执行、数据提取、结构保证（不可变部分）
AI 负责：语言润色、不确定内容的补充（灵活部分）
```

**推荐工作流**：

```
1. python run_pipeline.py → 得到 03_Proposal_Response.md（结构完整）
2. 将 03_Proposal_Response.md 粘贴给 AI
3. 告诉 AI："请只做语言润色，不要修改技术参数，帮我补充所有[待补充]条目"
4. AI 输出最终版本
```

---

## 9. 故障排查

### 9.1 常见错误

#### `❌ Error: File not found`

```
原因：工作目录不正确
解决：cd d:\vibedrone\vibe-working-experiments
```

#### `ModuleNotFoundError: No module named 'docx'`

```
解决：pip install python-docx
注意：.txt / .md 文件不需要此依赖
```

#### `ModuleNotFoundError: No module named 'openpyxl'`

```
解决：pip install openpyxl  （仅 analyze.py 需要）
```

#### `❌ Excel 文件缺少以下必要字段`

```
原因：Excel 表头不符合规范（区分大小写）
解决：确认第一行包含：Customer, Case ID, Date Opened, Issue Type, 
      Module, Severity, Resolution Time (hrs), Escalated
```

#### 提取问题数为 0

```
排查步骤：
  1. 确认文件有内容：python -c "print(open('materials/VanArsdel_RFP.txt').read()[:300])"
  2. 确认文件编码为 UTF-8
  3. 如果 RFP 格式特殊（纯表格），可手工整理为按行的要求列表
```

#### 知识库命中率很低（< 30%）

```
排查步骤：
  1. 核查脚本日志中"扫描知识库"列出的文档列表是否正确
  2. python -c "
     import json
     r = json.load(open('outputs/02_search_results.json', encoding='utf-8'))
     print(r['results'][0]['keywords'])  # 查看第一个问题的关键词
     "
  3. 在知识库文档中手动搜索这些关键词，验证文档内容是否相关
  4. 确认 .docx 文件正确被读取（检查是否安装了 python-docx）
```

#### `.docx` 输出报权限错误

```
原因：03_Proposal_Response.docx 已在 Word 中打开
解决：关闭 Word，然后用 --skip-extract --skip-search 重新生成
```

#### Step 2 报 `Questions file not found`

```
原因：Step 1 未成功完成
解决：先成功运行 Step 1，确认 outputs/01_rfp_questions.json 存在
```

### 9.2 调试命令速查

```powershell
# 查看提取的所有问题（带章节）
python -c "
import json; data = json.load(open('outputs/01_rfp_questions.json', encoding='utf-8'))
for q in data['questions']: print(q['id'], q['type_icon'], q['section'][:20], q['original'][:50])
"

# 查看未完全命中的问题
python -c "
import json; data = json.load(open('outputs/02_search_results.json', encoding='utf-8'))
for r in data['results']:
    if r['status'] != 'full_match': print(r['question_id'], r['status_icon'], r['source_doc'] or '无', r['question_text'][:50])
"

# 统计占位符数量
python -c "print(open('outputs/03_Proposal_Response.md', encoding='utf-8').read().count('[待补充'))"
```

---

## 10. 进阶用法

### 10.1 为其他 RFP 项目运行

```powershell
python skills/bid-response-agent/scripts/run_pipeline.py `
    C:\Projects\Contoso_RFP.docx `
    C:\Knowledge\ProductDocs\ `
    --client "Contoso, Ltd." --project "Cloud Migration" `
    --output-dir outputs/contoso-2026
```

每个项目使用独立的 `--output-dir`，避免覆盖历史结果。

### 10.2 批量处理多份 RFP

```powershell
$rfps = @(
    @{file="materials/RFP_A.txt"; client="Client A"; project="Project X"},
    @{file="materials/RFP_B.txt"; client="Client B"; project="Project Y"}
)
foreach ($rfp in $rfps) {
    $outDir = "outputs/$($rfp.client.Replace(' ', '_'))"
    python skills/bid-response-agent/scripts/run_pipeline.py `
        $rfp.file materials/ --client $rfp.client --project $rfp.project `
        --output-dir $outDir
    Write-Host "✅ $($rfp.client) 完成"
}
```

### 10.3 仅重新生成投标书（复用已有检索结果）

```powershell
python skills/bid-response-agent/scripts/run_pipeline.py `
    materials/VanArsdel_RFP.txt materials/ `
    --client "VanArsdel, Ltd." --project "Smart Energy Management Solution" `
    --skip-extract --skip-search
```

### 10.4 学完实验的下一步

完成实验后，推荐阅读 [SKILL_TUTORIAL.md](SKILL_TUTORIAL.md) 学习如何从零创建自己的 Skill：

- 理解 SKILL.md 的 7 个组成部分
- 按通用模板编写自己的 SKILL.md
- 用配套 Python 脚本模板实现自动化
- 完整示例：从零创建一个"合同审查"Skill

---

## 附录：脚本参数速查

### `extract.py`

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `rfp_file` | ✅ | — | RFP 文档路径 |
| `--output-dir` | ❌ | `outputs` | 输出目录 |

### `search_kb.py`

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `kb_dir` | ✅ | — | 知识库目录 |
| `--questions` | ❌ | `outputs/01_rfp_questions.json` | 问题 JSON |
| `--output-dir` | ❌ | `outputs` | 输出目录 |
| `--exclude` | ❌ | — | 排除文件（支持多个，空格分隔）|

### `generate.py`

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `--questions` | ❌ | `outputs/01_rfp_questions.json` | 问题 JSON |
| `--search-results` | ❌ | `outputs/02_search_results.json` | 检索 JSON |
| `--client` | ❌ | `客户` | 甲方公司名 |
| `--project` | ❌ | `项目` | 项目名称 |
| `--output-dir` | ❌ | `outputs` | 输出目录 |

### `run_pipeline.py`

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `rfp_file` | ✅ | — | RFP 文档 |
| `kb_dir` | ✅ | — | 知识库目录 |
| `--client` | ❌ | `客户` | 甲方公司名 |
| `--project` | ❌ | `项目` | 项目名称 |
| `--output-dir` | ❌ | `outputs` | 输出目录 |
| `--skip-extract` | ❌ | False | 跳过 Step 1 |
| `--skip-search` | ❌ | False | 跳过 Step 2 |

### `analyze.py`

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `cases_file` | ✅ | — | Excel/CSV 客服数据文件 |
| `--output-dir` | ❌ | `outputs` | 输出目录 |


---

## 目录

1. [背景与核心问题](#1-背景与核心问题)
2. [目录结构说明](#2-目录结构说明)
3. [环境准备](#3-环境准备)
4. [快速开始 — 一键运行投标响应流水线](#4-快速开始--一键运行投标响应流水线)
5. [分步执行指南](#5-分步执行指南)
   - 5.1 [Step 1：RFP 问题提取](#51-step-1rfp-问题提取)
   - 5.2 [Step 2：知识库检索](#52-step-2知识库检索)
   - 5.3 [Step 3：投标响应书生成](#53-step-3投标响应书生成)
   - 5.4 [客服案例分析（独立技能）](#54-客服案例分析独立技能)
6. [输出文件说明](#6-输出文件说明)
7. [质量验证检查表](#7-质量验证检查表)
8. [为什么 AI 会"跳步"以及脚本如何解决](#8-为什么-ai-会跳步以及脚本如何解决)
9. [故障排查](#9-故障排查)
10. [进阶用法](#10-进阶用法)

---

## 1. 背景与核心问题

### 1.1 症状

使用 OpenCode（或任何 AI 编码助手）调用 `SKILL.md` 技能时，容易出现以下偏差：

| 现象 | 根本原因 |
|------|---------|
| 跳过依赖关系分析步骤 | SKILL.md 是"说明书"，AI 自行判断哪些步骤"必要" |
| 原文摘录改为概括性描述 | AI 倾向于用更流畅的语言改写，而非逐字引用 |
| 输出 `.md` 而非 `.docx` | 无工具链约束，AI 走最简路径 |
| 每次运行结果不一致 | 纯语言判断存在随机性，无法保证幂等性 |
| 出处只标文档名，不标章节 | AI 不做精确索引，靠记忆模糊匹配 |

### 1.2 解决方案

```
SKILL.md（指令文档）
      +
scripts/*.py（执行脚本）
      =
可复现、可验证、严格按流程执行的自动化技能
```

每个脚本：
- **强制执行** SKILL.md 中定义的所有步骤，步步打印日志
- **JSON 中间件** 在步骤间传递结构化数据，可随时审查
- **原文逐字摘录**，不改写，只标注出处（文档名 + 章节）
- **幂等性**：相同输入 → 相同输出，可重复运行

---

## 2. 目录结构说明

```
vibe-working-experiments/
│
├── materials/                         # 原始输入材料（知识库）
│   ├── VanArsdel_RFP.txt              # 招标书（RFP）
│   ├── EcoSense_360_Technical_Specifications.txt
│   ├── EcoSense_360_Customer_Case_Study.txt
│   └── EcoSense_360_Sample_Pricing_Sheet.txt
│
├── skills/
│   ├── rfp-question-extractor/
│   │   ├── SKILL.md                   # AI 指令文档（面向 AI）
│   │   └── scripts/
│   │       └── extract.py             # ★ 自动化脚本（面向脚本执行）
│   │
│   ├── knowledge-searcher/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── search_kb.py           # ★
│   │
│   ├── proposal-generator/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── generate.py            # ★
│   │
│   ├── bid-response-agent/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── run_pipeline.py        # ★ 一键运行全流水线
│   │
│   └── support-case-analyzer/
│       ├── SKILL.md
│       └── scripts/
│           └── analyze.py             # ★ 独立技能
│
├── outputs/                           # 所有输出文件（自动创建）
│   ├── 01_RFP_Questions.md
│   ├── 01_rfp_questions.json          # 流水线中间件
│   ├── 02_Knowledge_Search_Report.md
│   ├── 02_search_results.json         # 流水线中间件
│   ├── 03_Proposal_Response.md
│   ├── 03_Proposal_Response.docx      # 需要 python-docx
│   └── 04_Executive_Summary.md
│
├── requirements.txt                   # 可选依赖
└── EXPERIMENT_MANUAL.md               # 本文档
```

---

## 3. 环境准备

### 3.1 Python 版本要求

```
Python >= 3.9
```

验证：

```powershell
python --version
```

### 3.2 安装可选依赖

脚本核心功能**仅使用 Python 标准库**，无需额外安装。  
以下依赖为可选功能增强：

```powershell
# 进入项目根目录
cd d:\vibedrone\vibe-working-experiments

# 安装可选依赖
pip install -r requirements.txt
```

| 包 | 功能 | 不安装时的行为 |
|----|------|--------------|
| `python-docx` | 读取 `.docx` 格式的 RFP 和知识库；导出 `.docx` 格式投标书 | 自动降级为纯文本读取；不生成 `.docx` 输出 |
| `openpyxl` | 读取 `.xlsx` 格式的客服案例数据 | 分析脚本报错并提示安装 |

### 3.3 确认工作目录

所有命令均从**项目根目录**执行：

```powershell
cd d:\vibedrone\vibe-working-experiments
```

---

## 4. 快速开始 — 一键运行投标响应流水线

这是最简单的方式，一条命令完成从 RFP 到投标书的全部工作：

```powershell
python skills/bid-response-agent/scripts/run_pipeline.py `
    materials/VanArsdel_RFP.txt `
    materials/ `
    --client "VanArsdel, Ltd." `
    --project "Smart Energy Management Solution"
```

**预期输出：**

```
🚀 Bid Response Agent — Full Pipeline
   RFP 文档:  materials/VanArsdel_RFP.txt
   知识库:    materials/
   客户:      VanArsdel, Ltd.
   项目:      Smart Energy Management Solution
   输出目录:  outputs/

══════════════════════════════════════════════════════════════
  Step 1 / 3 — RFP 问题提取
══════════════════════════════════════════════════════════════
  $ python extract.py materials/VanArsdel_RFP.txt --output-dir outputs
...
[1/6] 读取文档: materials/VanArsdel_RFP.txt
      ✓ 2135 字符
[2/6] 识别章节结构...
      ✓ 8 个章节
...
🎉 完成！共提取 N 个问题

══════════════════════════════════════════════════════════════
  Step 2 / 3 — 知识库检索
══════════════════════════════════════════════════════════════
...
      ✅ 完全匹配 X (Y%)
      ⚠️  部分匹配 ...
      ❌ 未找到 ...

══════════════════════════════════════════════════════════════
  Step 3 / 3 — 投标响应书生成
══════════════════════════════════════════════════════════════
...
🎉 投标响应书生成完成！

══════════════════════════════════════════════════════════════
  ✅  Pipeline 全部完成！
══════════════════════════════════════════════════════════════

  📁 输出目录: D:\vibedrone\vibe-working-experiments\outputs
     01_RFP_Questions.md            RFP 问题清单
     02_Knowledge_Search_Report.md  知识库检索报告
     03_Proposal_Response.md        投标响应书
     04_Executive_Summary.md        执行摘要
```

完成后打开 `outputs/04_Executive_Summary.md` 查看执行摘要和下一步行动清单。

---

## 5. 分步执行指南

分步执行适用于：调试中间结果 / 复用已有输出 / 只跑部分流程。

### 5.1 Step 1：RFP 问题提取

**脚本**：`skills/rfp-question-extractor/scripts/extract.py`

**对应 SKILL.md 步骤**（严格执行，不跳过）：

| 步骤 | 脚本日志前缀 | 说明 |
|------|------------|------|
| 1. 读取文档 | `[1/6]` | 支持 `.txt` / `.md` / `.docx` |
| 2. 章节识别 | `[2/6]` | 按标题层级/编号识别结构 |
| 3. 问题提取 | `[3/6]` | 识别 4 种类型（见下表） |
| 4. 分类编号 | `[4/6]` | Q-001, Q-002 … 全局唯一 |
| 5. 依赖关系 | `[5/6]` | 基于共享主题关键词 |
| 6. 汇总统计 | `[6/6]` | 写入 JSON + Markdown |

**问题类型识别规则**：

| 类型 | 图标 | 触发条件 |
|------|------|---------|
| 直接问题 | 🔴 | 以 `?` 结尾，或含 `please describe/provide` 等祈使表达 |
| 硬性要求 | 🟡 | 含 `must/shall/required`，或以动作动词开头（Deploy/Provide/Ensure…）|
| 期望描述 | 🟢 | 含 `should/preferred/recommended` 等柔性表达 |
| 资质门槛 | 🔵 | 含 `at least/minimum/demonstrated/references/certified` 等 |

> **章节感知提取（v1.1 新增）**：对于「技术要求」「项目目标」「工作范围」「评分标准」
> 「供应商资质」等已知需求章节，脚本会为章节内所有有意义的条目自动赋予章节默认类型，
> 即使该条目不含任何显式触发词（例如 "Cloud-based management portal" 或 "Sustainability impact"）。
> 这与 OpenCode AI 手工提取结果更好对齐，减少遗漏。

**运行命令**：

```powershell
python skills/rfp-question-extractor/scripts/extract.py materials/VanArsdel_RFP.txt
```

**带参数**：

```powershell
python skills/rfp-question-extractor/scripts/extract.py `
    materials/VanArsdel_RFP.txt `
    --output-dir outputs
```

**输出**：

```
outputs/
├── 01_RFP_Questions.md      ← 阅读此文件检查提取质量
└── 01_rfp_questions.json    ← 下一步脚本的输入
```

**验证方法**：

打开 `01_RFP_Questions.md`，检查：
- [ ] 每个 RFP 章节都有对应的问题
- [ ] 问题编号连续无空缺
- [ ] "原文摘要"是 RFP 原文（未改写），加了引号
- [ ] "依赖关系"章节有输出（哪怕是"各问题相对独立"）

---

### 5.2 Step 2：知识库检索

**脚本**：`skills/knowledge-searcher/scripts/search_kb.py`

**前提**：Step 1 已完成（`outputs/01_rfp_questions.json` 存在）

**对应 SKILL.md 步骤**（严格执行）：

| 步骤 | 脚本日志前缀 | 说明 |
|------|------------|------|
| 1. 扫描知识库 | `[1/5]` | 遍历目录，逐文档读取，记录段落数 |
| 2. 加载问题 | `[2/5]` | 从 JSON 加载所有问题 |
| 3. 逐题检索 | `[3/5]` | 每题打印命中状态和来源文档 |
| 4. 匹配评级 | `[4/5]` | 打印完全/部分/未找到统计 |
| 5. 写入输出 | `[5/5]` | JSON + Markdown 报告 |

**匹配评级标准**：

| 评级 | 图标 | 条件 |
|------|------|------|
| 完全匹配 | ✅ | 关键词覆盖率 ≥ 55% |
| 部分匹配 | ⚠️ | 关键词覆盖率 ≥ 15% 且 < 55% |
| 未找到 | ❌ | 覆盖率 < 15% |

**运行命令**：

```powershell
python skills/knowledge-searcher/scripts/search_kb.py materials/
```

**带参数**：

```powershell
python skills/knowledge-searcher/scripts/search_kb.py `
    materials/ `
    --questions outputs/01_rfp_questions.json `
    --output-dir outputs
```

**使用自定义知识库**：

```powershell
# 指定不同的知识库目录
python skills/knowledge-searcher/scripts/search_kb.py `
    C:\MyCompany\ProductDocs\ `
    --questions outputs/01_rfp_questions.json
```

**重要：知识库目录不应包含 RFP 文件本身**

如果 RFP 文件和产品文档在同一目录，使用 `--exclude` 参数排除 RFP 及其衍生文件，
否则搜索会自我匹配（从 RFP 原文中找到"答案"，而非从产品文档）：

```powershell
python skills/knowledge-searcher/scripts/search_kb.py `
    materials/ `
    --questions outputs/01_rfp_questions.json `
    --exclude materials/VanArsdel_RFP.txt materials/VanArsdel_RFP_Questions.md
```

> ✅ **最佳实践**：将产品文档放在独立目录（如 `knowledge_base/`），与 RFP 文件分开存放，
> 无需使用 `--exclude`。使用 `run_pipeline.py` 时，RFP 文件会被自动排除。

**输出**：

```
outputs/
├── 02_Knowledge_Search_Report.md   ← 阅读此文件检查检索质量
└── 02_search_results.json          ← 下一步脚本的输入
```

**验证方法**：

打开 `02_Knowledge_Search_Report.md`，检查：
- [ ] 每个问题都有"来源文档"字段（格式：`文件名.txt > 章节名`）
- [ ] "相关原文摘录"是引用块格式（以 `>` 开头），是原文而非概括
- [ ] "检索命中总览"表格中完全匹配 + 部分匹配的占比 > 50%
- [ ] "需人工补充"表格列出了所有 ❌ 和 ⚠️ 问题

---

### 5.3 Step 3：投标响应书生成

**脚本**：`skills/proposal-generator/scripts/generate.py`

**前提**：Step 1、Step 2 已完成

**对应 SKILL.md 步骤**（严格执行）：

| 步骤 | 脚本日志前缀 | 说明 |
|------|------------|------|
| 1. 加载数据 | `[1/5]` | 加载问题 + 检索结果两个 JSON |
| 2. 内容梳理 | `[2/5]` | 按 RFP 章节顺序重排，打印章节分布 |
| 3. 回答润色 | `[3/5]` | 口语化 → 正式商务语体，补充开场白 |
| 4. 质量自检 | `[4/5]` | 统计占位符数量，检查覆盖率 |
| 5. 文件生成 | `[5/5]` | Markdown（必输）+ Word（可选）|

**占位符规范**：  
对于 ❌ 未找到的问题，响应书中会自动插入：
```
[待补充：需相关团队在终稿提交前补充说明]
```

在提交投标书前，**全局搜索「待补充」**确认所有占位符已被填写。

**运行命令**：

```powershell
python skills/proposal-generator/scripts/generate.py `
    --client "VanArsdel, Ltd." `
    --project "Smart Energy Management Solution"
```

**带全部参数**：

```powershell
python skills/proposal-generator/scripts/generate.py `
    --questions outputs/01_rfp_questions.json `
    --search-results outputs/02_search_results.json `
    --client "VanArsdel, Ltd." `
    --project "Smart Energy Management Solution" `
    --output-dir outputs
```

**输出**：

```
outputs/
├── 03_Proposal_Response.md     ← 主要投标响应书（Markdown）
└── 03_Proposal_Response.docx   ← Word 格式（需 python-docx 已安装）
```

**验证方法**：

打开 `03_Proposal_Response.md`，检查：
- [ ] 文档以正式致辞开头
- [ ] 每章节与 RFP 原始章节对应
- [ ] 每个问题有"甲方要求"（原文引用）和"我方响应"两部分
- [ ] 关键参数用 `**加粗**` 标注
- [ ] 搜索"待补充" — 确认已知晓需人工补充的条目

---

### 5.4 客服案例分析（独立技能）

**脚本**：`skills/support-case-analyzer/scripts/analyze.py`

此技能**独立于**投标响应流水线，用于分析客服工单 Excel 数据。

**对应 SKILL.md 步骤**（严格执行）：

| 步骤 | 脚本日志前缀 | 分析内容 |
|------|------------|---------|
| 1. 读取数据 | `[1/7]` | 验证 8 个必要字段，统计行数 |
| 2. 总量统计 | `[2/7]` | 案例总数、时间跨度 |
| 3. 高频问题 | `[3/7]` | Top 3 Issue Type（按数量排序）|
| 4. 严重程度 | `[4/7]` | Critical/High/Medium/Low 占比 |
| 5. 解决效率 | `[5/7]` | 全局 + 分类平均解决时间 |
| 6. 升级率 | `[6/7]` | 总体升级率 + 最高升级类型 |
| 7. 改进建议 | `[7/7]` | 3-5 条数据驱动的改进建议 |

**前提**：需安装 `openpyxl`（处理 `.xlsx`）

```powershell
pip install openpyxl
```

**运行命令**：

```powershell
python skills/support-case-analyzer/scripts/analyze.py data/cases.xlsx
```

**支持格式**：
- `.xlsx` — Excel（推荐）
- `.csv` — 逗号分隔值（标准库支持，无需额外安装）

**必要的数据字段**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| Customer | 文本 | 客户名称 |
| Case ID | 文本 | 案例编号 |
| Date Opened | 日期/文本 | 开案日期 |
| Issue Type | 文本 | 问题分类 |
| Module | 文本 | 涉及模块 |
| Severity | 文本 | Critical/High/Medium/Low |
| Resolution Time (hrs) | 数值 | 解决耗时（小时）|
| Escalated | 布尔/文本 | Yes/No 或 True/False |

---

## 6. 输出文件说明

### 6.1 投标响应流水线输出

| 文件 | 格式 | 用途 | 目标读者 |
|------|------|------|---------|
| `01_RFP_Questions.md` | Markdown | 问题清单，供团队分工 | 售前/技术团队 |
| `01_rfp_questions.json` | JSON | 流水线中间数据 | 脚本（自动使用）|
| `02_Knowledge_Search_Report.md` | Markdown | 检索报告，含原文证据 | 产品/技术团队 |
| `02_search_results.json` | JSON | 流水线中间数据 | 脚本（自动使用）|
| `03_Proposal_Response.md` | Markdown | 投标响应书初稿 | 售前/技术团队 |
| `03_Proposal_Response.docx` | Word | 可直接提交的版本 | 客户/评审 |
| `04_Executive_Summary.md` | Markdown | 执行摘要 + 下一步清单 | 项目负责人 |

### 6.2 JSON 中间件结构（便于调试）

`01_rfp_questions.json` 核心字段：
```json
{
  "questions": [
    {
      "id":         "Q-001",
      "type":       "hard_req",
      "type_icon":  "🟡",
      "section":    "4. Technical Requirements",
      "original":   "Support for wireless IoT sensors ...",
      "hint":       "需确认传感器类型和规格",
      "priority":   "高"
    }
  ]
}
```

`02_search_results.json` 核心字段：
```json
{
  "results": [
    {
      "question_id":    "Q-001",
      "status":         "full_match",
      "status_icon":    "✅",
      "source_doc":     "EcoSense_360_Technical_Specifications.txt",
      "source_section": "3. Key Features & Capabilities",
      "best_quote":     "Wireless IoT Sensors (temperature, occupancy, humidity, light)",
      "answer_draft":   "..."
    }
  ]
}
```

---

## 7. 质量验证检查表

运行流水线后，用此清单验证输出质量：

### 7.1 RFP 问题提取质量

- [ ] `outputs/01_rfp_questions.json` 文件已生成
- [ ] 问题总数合理（通常 10-30 个，根据 RFP 长度而定）
- [ ] 问题分布覆盖所有 4 种类型
- [ ] 各章节都有对应问题（无章节被完全遗漏）
- [ ] 问题编号连续无跳跃
- [ ] 依赖关系章节有内容
- [ ] "原文摘要"保持了原文语言（英文 RFP 摘要仍为英文）

### 7.2 知识库检索质量

- [ ] `outputs/02_search_results.json` 文件已生成
- [ ] 扫描了所有期望的知识库文档（检查日志中的文档列表）
- [ ] 完全匹配 + 部分匹配总占比 > 50%
- [ ] 每个 ✅ 结果都有来源文档和原文摘录
- [ ] 原文摘录是引用格式（`>` 开头），不是自己编写的答案
- [ ] 所有 ❌ 问题都列入了"需人工补充"表格

### 7.3 投标响应书质量

- [ ] `outputs/03_Proposal_Response.md` 文件已生成
- [ ] 文档结构完整（致辞 → 各章节 → 附录 → 质量自检）
- [ ] 章节数量与 RFP 章节数量一致
- [ ] `[待补充]` 占位符的数量与 `02` 报告中 ❌+⚠️ 数量一致
- [ ] 关键参数已加粗（如产品名称、技术指标）
- [ ] 未出现凭空编造的数字或认证（所有回答必须有来源）

---

## 8. 为什么 AI 会"跳步"以及脚本如何解决

### 8.1 根本原因分析

```
SKILL.md 是"菜谱"，AI 是"厨师"。
  厨师可以决定某几步"可以省略"——脚本拥有菜谱的执行权。
```

| AI 手动执行的问题 | 脚本的解决方式 |
|----------------|---------------|
| 可能跳过依赖关系分析 | 步骤 5 是固定的、无法跳过的函数调用 |
| 原文引用可能被改写 | `best_verbatim_quote()` 函数强制返回原文切片，不做语义加工 |
| 章节出处不精确 | 建立 `{doc_name: {chunks: [{section, text}]}}` 索引，每次命中都记录章节 |
| 输出格式不一致 | `render_markdown()` 函数定义了固定模板 |
| 运行结果不可复现 | Python 脚本 = 确定性函数，相同输入 → 相同输出 |
| 无法验证 | JSON 中间件在每步后保存，可随时 `cat` 检查 |
| 遗漏不含触发词的条目<br>（如 "Sustainability impact"） | `section_default_type()` 对已知需求章节内所有有意义行赋予章节默认类型 |

### 8.2 脚本 vs. AI 执行对比

```
┌─────────────────────────────────────────────────────────┐
│ AI 手动执行（之前）                                       │
│ 读 SKILL.md → 理解意图 → 手动完成 → 可能简化/跳步        │
│ 问题：不可复现、容易偷工、格式随意                        │
└─────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 脚本自动执行（现在）                                      │
│ 脚本固化所有步骤 → 强制按序执行 → JSON 中间件 → 可验证   │
│ 优势：强一致性、可复现、步步有日志、输出可审查            │
└─────────────────────────────────────────────────────────┘
```

---

## 9. 故障排查

### 9.1 常见错误及解决方法

#### 错误：`❌ Error: File not found: materials/VanArsdel_RFP.txt`

```
原因：工作目录不是项目根目录
解决：先执行 cd d:\vibedrone\vibe-working-experiments，再运行脚本
```

#### 错误：`ModuleNotFoundError: No module named 'docx'`

```
原因：python-docx 未安装（读取 .docx 文件时）
解决：pip install python-docx
注意：.txt 文件不需要此依赖，脚本会自动降级处理
```

#### 错误：`ModuleNotFoundError: No module named 'openpyxl'`

```
原因：openpyxl 未安装（读取 .xlsx 文件时）
解决：pip install openpyxl
```

#### 错误：`❌ Excel 文件缺少以下必要字段：...`

```
原因：Excel 表头不符合规范
解决：检查第一行表头是否与规范字段完全一致（区分大小写）
     必要字段：Customer, Case ID, Date Opened, Issue Type, Module,
               Severity, Resolution Time (hrs), Escalated
```

#### 问题：提取的问题数为 0

```
原因：RFP 文件为空，或没有匹配到任何问题类型
解决：
  1. 确认文件有内容：python -c "print(open('materials/VanArsdel_RFP.txt').read()[:200])"
  2. 检查文件编码是否为 UTF-8
  3. 如果 RFP 格式特殊（纯表格、无标准行文），可以手动整理为按行的要求列表
```

#### 问题：知识库检索命中率很低（< 30%）

```
可能原因：
  1. 知识库文档与 RFP 主题不匹配（如用了错误的知识库目录）
  2. 知识库文档使用了不同的专业术语或缩写
  3. .docx 文件未被读取（需要 python-docx）

排查步骤：
  1. 检查脚本日志中"扫描知识库"阶段列出的文档清单
  2. 打开 02_search_results.json，查看具体问题的 keywords 字段
  3. 手动在知识库文档中搜索这些关键词验证
```

#### 问题：Step 2 报错 `Questions file not found`

```
原因：Step 1 未成功运行，或 outputs 目录不存在
解决：先成功运行 Step 1，确认 outputs/01_rfp_questions.json 存在
```

### 9.2 调试模式

如需查看中间数据，直接读取 JSON 中间件：

```powershell
# 检查提取了哪些问题
python -c "
import json
data = json.load(open('outputs/01_rfp_questions.json', encoding='utf-8'))
for q in data['questions']:
    print(q['id'], q['type_icon'], q['original'][:60])
"
```

```powershell
# 检查哪些问题没有命中
python -c "
import json
data = json.load(open('outputs/02_search_results.json', encoding='utf-8'))
for r in data['results']:
    if r['status'] != 'full_match':
        print(r['question_id'], r['status_icon'], r['question_text'][:50])
"
```

---

## 10. 进阶用法

### 10.1 复用已有结果（加速重跑）

如果只修改了 Step 3 的参数，可以跳过前两步：

```powershell
python skills/bid-response-agent/scripts/run_pipeline.py `
    materials/VanArsdel_RFP.txt `
    materials/ `
    --client "VanArsdel, Ltd." `
    --project "Smart Energy Management Solution" `
    --skip-extract `
    --skip-search
```

### 10.2 用于其他 RFP 项目

替换 RFP 文件和知识库路径：

```powershell
# 为新客户 Contoso 生成投标书
python skills/bid-response-agent/scripts/run_pipeline.py `
    C:\Projects\Contoso_RFP.docx `
    C:\Knowledge\ProductDocs\ `
    --client "Contoso, Ltd." `
    --project "Cloud Migration" `
    --output-dir outputs/contoso
```

每个项目使用独立的 `--output-dir`，避免覆盖之前的结果。

### 10.3 指定自定义输出目录

```powershell
python skills/bid-response-agent/scripts/run_pipeline.py `
    materials/VanArsdel_RFP.txt `
    materials/ `
    --output-dir outputs/vanarsdelltd-2026Q1
```

### 10.4 与 AI 助手结合使用（推荐工作流）

```
1. 运行脚本 → 得到结构化 JSON 和 Markdown 输出
2. 将 03_Proposal_Response.md 提供给 AI，
   要求 AI 只做"语言润色"和"补充待补充条目"
3. AI 不再需要"手动执行技能流程"——流程已由脚本完成
4. AI 的角色变为：编辑 / 补充 / 润色，而非执行技能
```

这样既保证了**流程完整性**（由脚本保证），也保留了**AI 语言能力**（润色和补充），两者取长补短。

### 10.5 批量处理多份 RFP

```powershell
# 批量处理脚本示例（PowerShell）
$rfps = @(
    @{file="materials/RFP_A.txt"; client="Client A"; project="Project X"},
    @{file="materials/RFP_B.txt"; client="Client B"; project="Project Y"}
)

foreach ($rfp in $rfps) {
    $outDir = "outputs/$($rfp.client.Replace(' ', '_'))"
    python skills/bid-response-agent/scripts/run_pipeline.py `
        $rfp.file materials/ `
        --client $rfp.client `
        --project $rfp.project `
        --output-dir $outDir
    Write-Host "✅ $($rfp.client) 完成，输出: $outDir"
}
```

---

## 附录：脚本参数总览

### `extract.py`

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `rfp_file` | ✅ | — | RFP 文件路径 |
| `--output-dir` | ❌ | `outputs` | 输出目录 |

### `search_kb.py`

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `kb_dir` | ✅ | — | 知识库目录路径 |
| `--questions` | ❌ | `outputs/01_rfp_questions.json` | 问题 JSON 文件路径 |
| `--output-dir` | ❌ | `outputs` | 输出目录 |
| `--exclude` | ❌ | — | 排除指定文件（支持多个），其同名不同扩展名文件也会被排除 |

### `generate.py`

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--questions` | ❌ | `outputs/01_rfp_questions.json` | 问题 JSON |
| `--search-results` | ❌ | `outputs/02_search_results.json` | 检索结果 JSON |
| `--client` | ❌ | `客户` | 甲方公司名 |
| `--project` | ❌ | `项目` | 项目名称 |
| `--output-dir` | ❌ | `outputs` | 输出目录 |

### `run_pipeline.py`

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `rfp_file` | ✅ | — | RFP 文件 |
| `kb_dir` | ✅ | — | 知识库目录 |
| `--client` | ❌ | `客户` | 甲方公司名 |
| `--project` | ❌ | `项目` | 项目名称 |
| `--output-dir` | ❌ | `outputs` | 输出目录 |
| `--skip-extract` | ❌ | `False` | 跳过 Step 1（复用已有 JSON）|
| `--skip-search` | ❌ | `False` | 跳过 Step 2（复用已有 JSON）|

### `analyze.py`

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `cases_file` | ✅ | — | Excel/CSV 案例文件 |
| `--output-dir` | ❌ | `outputs` | 输出目录 |

---

*实验手册 v1.0 — 与脚本同步维护，修改脚本后请同步更新本文档*

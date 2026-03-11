# Vibe Working Experiments

> **AI Skill 自动化实验项目** — 将 SKILL.md 指令文档升级为可执行、可复现的自动化技能

---

## 目录

1. [核心概念：Skill 的两层结构](#1-核心概念skill-的两层结构)
2. [适用场景](#2-适用场景)
3. [本项目的 Skill 地图](#3-本项目的-skill-地图)
4. [最佳实践](#4-最佳实践)
5. [学习路径](#5-学习路径)

---

## 1. 核心概念：Skill 的两层结构

**AI Skill（技能）** 是一个封装了固定工作流程的可复用模块。本项目中，每个 Skill 由两层组成：

```
Skill
  ├── SKILL.md         （描述层）  定义角色、流程、输出、质量标准
  └── scripts/*.py     （执行层）  将描述层的流程固化为强制执行的代码
```

**描述层（SKILL.md）** 解决的问题：明确 Skill 的边界，让 AI 知道何时调用它、如何执行它。

**执行层（scripts）** 解决的问题：AI 单独读 SKILL.md 时，容易跳过步骤或改写原文——脚本强制按序执行所有步骤，保证输出的一致性。

| 执行方式 | 优势 | 劣势 |
|---------|------|------|
| 只用 AI（无脚本） | 灵活、可对话 | 跳步、改写原文、结果随机 |
| AI + 脚本 | 可复现、可审查 | 需要一次性编写脚本 |

**什么时候必须有脚本**：需要读写本地文件、输出格式有严格要求、流程步骤间有数据依赖、原文引用不允许改写。

---

## 2. 适用场景

### 场景一：投标响应（本项目重点演示）

**业务背景**：收到客户发来的 RFP（招标书）后，需要从几十页文档里识别所有问题、从产品文档里检索对应答案、最后组织成格式规范的响应书。这是一个典型的"信息处理 → 知识检索 → 文档生成"三步流水线。

**痛点**：人工处理耗时 2-4 天；让 AI 直接处理容易漏提问题、从错误来源引用知识（如把 RFP 里的系统描述当成产品能力来引用）、输出格式不统一。

**本项目的解法**：三个 Skill 串联成流水线，问题提取、知识检索、响应书生成各司其职，每步结果保存为 JSON 中间件，全程可审查。

### 场景二：客服案例分析（独立演示）

**业务背景**：从 Excel 客服工单数据中识别高频问题、归因分析、输出改进建议。

**痛点**：人工分析靠感觉，规则不统一；让 AI 读 Excel 数据可靠性低。

**本项目的解法**：`analyze.py` 严格按 SKILL.md 的 7 步流程处理，输出包含统计数据的结构化简报。

### 这种模式适用的通用场景

| 场景类型 | 典型任务 | 关键需求 |
|---------|---------|---------|
| 文档分析 | 合同审查、需求梳理、标准对比 | 原文引用不改写 |
| 知识检索 | 产品问答、政策查询、FAQs 生成 | 来源可追溯 |
| 报告生成 | 投标书、分析简报、会议纪要 | 格式固定、可批量 |
| 数据分析 | 工单统计、日志归因、销售分析 | 字段验证、结构化输出 |

---

## 3. 本项目的 Skill 地图

```
materials/
  VanArsdel_RFP.txt          ← 招标书（输入）
  EcoSense_*.txt / .docx     ← 产品知识库（检索来源）
  Fabrikam_*.xlsx            ← 客服工单数据

skills/
  rfp-question-extractor/    ← Step 1: 从 RFP 提取结构化问题
  knowledge-searcher/        ← Step 2: 用问题检索知识库，逐字引用原文
  proposal-generator/        ← Step 3: 把答案组织成投标响应书
  bid-response-agent/        ← 编排器: 将上面 3 个 Skill 串联一键执行
  support-case-analyzer/     ← 独立 Skill: 分析客服工单数据

outputs/                     ← 所有结果（运行后自动生成）
```

**Skill 间的数据流**：

```
VanArsdel_RFP.txt
      │
      ▼ extract.py
01_rfp_questions.json         ← 结构化问题清单
      │
      ▼ search_kb.py（检索 materials/ 目录）
02_search_results.json        ← 问题 + 知识库匹配结果 + 原文摘录
      │
      ▼ generate.py
03_Proposal_Response.md/.docx ← 最终投标响应书
```

JSON 中间文件是 Skill 之间的"契约"：格式严格定义，任何步骤都可以单独重跑，也可以人工审查或注入补充数据。

---

## 4. 最佳实践

### 实践一：脚本处理结构，AI 做语言润色

不要让 AI 执行整个 Skill 流程——让脚本做确定性的部分（提取、检索、格式化），让 AI 做主观判断的部分（语言润色、填补脚本无法回答的条目）。

```
❌ 让 AI 一次性完成提取 + 检索 + 生成   → 跳步、改写、不可控
✅ 脚本执行 → AI 润色 outputs/*.md 中的"[待补充]"条目
```

### 实践二：把知识库与 RFP 物理分离

`search_kb.py` 扫描整个目录，如果 RFP 文件与知识库混在一起，会把"客户提出的需求"当成"我们的产品能力"引用。

```
materials/              ← 只放知识库（产品文档）
rfp_input/              ← 只放待响应的 RFP
```

或者保持在同一目录，在运行时用 `--exclude` 参数排除 RFP 文件（流水线自动处理）。

### 实践三：用 JSON 中间文件做质量审查

每个步骤生成的 JSON 文件包含结构化的中间结果，发现问题可以精准定位到哪一步出问题：

- `01_rfp_questions.json` — 检查是否提取到正确数量的问题
- `02_search_results.json` — 检查哪些问题没有命中知识库（`status != "full_match"`）
- 知识库命中率低 → 说明知识库文档不够完整，需要补充材料

### 实践四：提交前全局搜索占位符

脚本对没有命中知识库的问题插入占位符 `[待补充：...]`，提交投标书前必须处理所有占位符：

```powershell
Select-String -Path outputs/03_Proposal_Response.md -Pattern "待补充"
```

### 实践五：用独立输出目录隔离不同项目

```powershell
# 每个客户/项目用独立目录，避免互相覆盖
python skills/bid-response-agent/scripts/run_pipeline.py `
    rfp_input/ClientA_RFP.docx materials/ `
    --client "Client A" --output-dir outputs/clientA-2026Q2
```

### 实践六：理解"脚本能做的"和"AI 该做的"分工

| 交给脚本 | 交给 AI |
|---------|---------|
| 问题提取（规则确定） | 语言风格润色 |
| 原文逐字引用（不允许改写）| 填补"待补充"条目 |
| 格式渲染（JSON / Markdown / docx）| 审阅逻辑连贯性 |
| 统计数据汇总（如命中率） | 判断答案是否有说服力 |
| 批量处理多份文件 | 针对特定客户定制语气 |

---

## 5. 学习路径

本项目提供两份详细文档，配合本 README 使用：

**[EXPERIMENT_MANUAL.md](EXPERIMENT_MANUAL.md)** — 实验操作手册

- 适合：第一次使用本项目的人
- 内容：环境配置、两条实验路径（分步 vs 一键）、每步技术原理、输出格式详解、故障排查
- 先读这个，动手跑一遍实验

**[SKILL_TUTORIAL.md](SKILL_TUTORIAL.md)** — Skill 创建教程

- 适合：想创建自己的 Skill 的人
- 内容：SKILL.md 7 个部分的解析、配套脚本模板、从零创建新 Skill 的完整示例
- 读完 EXPERIMENT_MANUAL.md 后读这个，自己动手创建一个新 Skill

### 建议学习顺序

```
1. 读 README.md（本文件）          → 理解概念和架构
2. 读 EXPERIMENT_MANUAL.md        → 动手跑实验，掌握使用方法
3. 读各 skills/*/SKILL.md          → 观察真实 Skill 是怎么写的
4. 读 SKILL_TUTORIAL.md           → 学习创建新 Skill 的方法
5. 自己创建一个新 Skill             → 完成学习闭环
```

---

**维护者**：HuaQloud AI Architect

# Skill 创建教程

> 本教程教你**从零创建一个可复现的 AI Skill**，理解 SKILL.md 的结构，
> 并为其编写配套的 Python 自动化脚本。
>
> **阅读前提**：已完成 `EXPERIMENT_MANUAL.md` 中的实验，理解现有 Skill 的使用方式。

---

## 目录

1. [什么是 Skill？](#1-什么是-skill)
2. [SKILL.md 解剖：7 个组成部分](#2-skillmd-解剖7-个组成部分)
3. [为什么需要配套脚本](#3-为什么需要配套脚本)
4. [创建 Skill 的通用流程](#4-创建-skill-的通用流程)
5. [通用 SKILL.md 模板](#5-通用-skillmd-模板)
6. [通用 Python 脚本模板](#6-通用-python-脚本模板)
7. [完整示例：从零创建 contract-reviewer Skill](#7-完整示例从零创建-contract-reviewer-skill)
8. [Skill 设计检查表](#8-skill-设计检查表)

---

## 1. 什么是 Skill？

**Skill（技能）** 是一个封装了特定工作流程的可复用模块。它由两部分构成：

```
Skill
  ├── SKILL.md         （描述层：说明 Skill 做什么、怎么做）
  └── scripts/xxx.py   （执行层：按描述层的流程自动执行）
```

**SKILL.md** 是一份给 AI 和人类都能读懂的说明文档，描述：
- 谁来执行（角色）
- 输入什么
- 分几步执行
- 输出什么
- 质量标准是什么

**配套脚本** 是将 SKILL.md 流程固化为代码，确保每次执行步骤完整、结果一致。

### Skill 与普通脚本的区别

| | 普通脚本 | Skill |
|--|---------|-------|
| 可读性 | 只有代码 | SKILL.md + 代码 |
| 调用方式 | 命令行 | 可供 AI 调用 + 命令行 |
| 边界定义 | 隐含 | 明确（输入/输出/质量标准）|
| 复用性 | 难以理解意图 | 意图显式，易于迁移 |
| 触发方式 | 手动运行 | AI 识别用户意图后自动调用 |

---

## 2. SKILL.md 解剖：7 个组成部分

以 `rfp-question-extractor/SKILL.md` 为例，逐部分解析：

### 2.1 前置元数据（Frontmatter）

```yaml
---
name: rfp-question-extractor
description: |
  从客户发来的 RFP 文档中，自动识别并提取所有需要响应的问题、
  技术要求和资质条件，输出结构化的问题清单。

  当用户提供一份 RFP/招标书/询价函，并要求提取问题、梳理需求、
  列出响应要点时触发本技能。
---
```

**关键字段**：

| 字段 | 作用 | 注意事项 |
|------|------|---------|
| `name` | Skill 唯一标识符 | 用连字符，全小写 |
| `description` | AI 判断何时调用此 Skill 的依据 | 第一段说功能，第二段说触发条件 |

> **触发条件非常重要**：description 的后半段决定 AI 在什么情境下会调用这个 Skill。
> 应用自然语言描述用户意图，如"当用户提供... 并要求... 时触发"。

---

### 2.2 角色定义（Role Definition）

```markdown
## 角色定义
你是一位经验丰富的售前需求分析师（Pre-sales Requirements Analyst）。
你擅长从冗长的招标文档中精准定位甲方关注点，确保不遗漏任何需要响应的问题。
```

**作用**：为 AI 建立执行角色的认知框架，影响 AI 的判断风格和关注重点。

**写法**：
- 给一个具体的职位名（中英文均标注）
- 描述该角色的核心能力和工作风格
- 避免过于宽泛（"你是 AI 助手"毫无意义）

---

### 2.3 输入规范（Input Specification）

```markdown
## 输入规范
用户会提供一份 RFP 文档的文件路径，支持格式：`.txt`、`.md`、`.docx`。

> 如果文件不是支持的格式或无法打开，请告知用户并建议转换格式。
```

**作用**：明确 Skill 接受什么输入、不接受什么输入。

**必须包含**：
- 输入格式（文件类型、数据结构）
- 可选参数及其含义
- 当输入不符合要求时如何处理

---

### 2.4 处理流程（Processing Steps）

```markdown
## 处理流程

按以下步骤执行：

1. **读取文档**：打开用户指定路径的文件，逐段落读取全文内容。
2. **章节识别**：根据标题层级和编号模式识别文档结构。
3. **问题提取**：扫描每个段落，识别以下类型的"需响应内容"：...
4. **分类编号**：为每个问题分配唯一编号（Q-001, Q-002...）。
5. **依赖关系标注**：标注问题之间的关联。
6. **汇总统计**：统计各类型问题数量。
```

**这是 SKILL.md 最核心的部分**。写好它的关键：

- **步骤数量**：通常 4-8 步，太少则过于模糊，太多则难以执行
- **步骤命名**：动词开头（读取/识别/提取/生成）
- **步骤内容**：每步说清楚"做什么"和"怎么判断"
- **步骤顺序**：严格的先后依赖关系，每步的输出是下一步的输入

> **关键原则**：如果你希望脚本强制执行某步骤，就把它单独列为一步。
> 合并在同一步的内容，AI（或脚本开发者）容易"合并处理"从而简化。

---

### 2.5 输出格式（Output Format）

```markdown
## 输出格式

输出一份 Markdown 格式的结构化问题清单：

​```markdown
# RFP 问题提取清单

## 📋 文档信息
- 文件名：[filename]
- 提取问题总数：X 个

## 📊 问题分布统计
| 类型 | 数量 | 占比 |
|------|------|------|
...
​```
```

**作用**：固定输出结构，确保每次输出格式一致，可被下游工具消费。

**写法**：
- 给出完整的输出示例（用代码块内嵌 Markdown）
- 用 `[placeholder]` 标注动态填充的部分
- 如果输出是 JSON 或 machine-readable 格式，给出字段说明

---

### 2.6 质量标准（Quality Standards）

```markdown
## 质量标准
- 每个问题的"原文摘要"必须引用文档原文，不可改写失真
- "响应要点提示"用一句话点明回答方向
- 优先级判定规则：含"必须/否决"→高，含"应当/要求"→中，含"希望/加分"→低
- 问题编号全局唯一且连续
```

**作用**：定义"什么是好的输出"，让 AI 知道如何自我检查，让脚本开发者知道什么该验证。

**写法**：
- 列出 3-6 条可验证的规则（能用"是/否"判断的）
- 避免模糊表述（"质量要高"没有意义）
- 重点关注容易出错的地方（如引用不改写、编号连续等）

---

### 2.7 异常处理（Error Handling）

```markdown
## 异常处理
- 如果文档结构极不规范（无标题层级）→ 改用段落顺序编号，在报告开头说明
- 如果文件格式不支持 → 报错并建议转换
```

**作用**：定义边界情况的处理方式，防止 Skill 在异常输入时静默失败或编造结果。

**必须覆盖**：
- 输入文件不存在或格式错误
- 输入内容为空或不符合预期
- 处理结果为空（如提取到 0 个问题）
- 依赖服务/工具不可用

---

## 3. 为什么需要配套脚本

SKILL.md 只是**说明书**，AI 阅读后会自行判断哪些步骤"重要"、哪些"可跳过"。

```
只有 SKILL.md 时：
  用户请求 → AI 读 SKILL.md → AI 自由解释 → 执行（可能跳步、改写）
                                                    ↑ 不可控

有配套脚本时：
  用户请求 → AI 调用脚本 → 脚本强制按流程执行 → 确定性输出
                                                    ↑ 可控、可复现
```

### 何时必须有配套脚本

| 场景 | 是否需要脚本 | 原因 |
|------|------------|------|
| 处理本地文件 | ✅ 必须 | AI 无法直接操作文件系统 |
| 输出需要精确格式（JSON/docx）| ✅ 必须 | AI 输出格式随机 |
| 多步流程且步骤间有数据依赖 | ✅ 强烈建议 | AI 容易跳步或混并 |
| 原文引用（不允许改写）| ✅ 强烈建议 | AI 倾向于"改写得更流畅" |
| 简单的单步文本生成 | ❌ 可选 | AI 执行足够好 |

---

## 4. 创建 Skill 的通用流程

```
Step 1: 定义边界   ← 整个 Skill 做一件事是什么？
Step 2: 写 SKILL.md ← 7 个部分，从角色到异常处理
Step 3: 验证 SKILL.md ← 用 AI 手动执行一次，发现哪些步骤被跳过
Step 4: 写配套脚本  ← 将每个步骤固化为函数
Step 5: 测试验证   ← 用真实数据运行，对比 AI 执行和脚本执行的结果
```

### Step 1：定义边界

回答三个问题：

```
Q1: 这个 Skill 单次执行完成一件什么事？（一句话）
    示例："从 PDF 合同中提取所有付款条款并标注风险等级"
    
Q2: 输入是什么？
    示例："一个 PDF 文件路径"
    
Q3: 输出是什么？
    示例："一份 Markdown 报告 + 一个 JSON 数据文件"
```

> **警告**：避免"大而全"的 Skill。一个 Skill 只做一件事效果最好。
> 如果需要多件事，考虑创建多个 Skill 并用编排器连接（类似 bid-response-agent）。

### Step 2：按模板写 SKILL.md

使用下一节的通用模板，逐部分填写。

### Step 3：用 AI 验证 SKILL.md

写好 SKILL.md 后，先**用纯 AI 执行一次**（不用脚本），观察：
- AI 是否跳过了某步骤？
- AI 是否按你期望的格式输出？
- AI 是否引用了原文还是自己改写了？

这些偏差就是你需要在脚本中"修复"的地方。

### Step 4：为每个步骤写一个函数

```python
# SKILL.md 中每个步骤 → 脚本中一个函数
步骤 1: 读取文档    →  def read_input(file_path):
步骤 2: 提取关键信息 →  def extract_items(text):
步骤 3: 分类        →  def classify_items(items):
步骤 4: 生成输出    →  def render_output(items):
main() 函数: 按顺序调用，每步打印 [N/M] 进度
```

### Step 5：测试验证

```
运行脚本 → 比较与 AI 手动执行的结果 → 确认关键质量标准都满足
```

---

## 5. 通用 SKILL.md 模板

将以下模板保存为 `skills/your-skill-name/SKILL.md`，补充 `[...]` 部分：

```markdown
---
name: your-skill-name
description: |
  [一句话描述 Skill 的功能，说明它处理什么、产出什么]

  当用户[描述用户的典型请求场景，如"提供...并要求..."]时触发本技能。
---

# [Skill 中文名称]

## 角色定义
你是一位[具体职位名（中英）]。
你擅长[核心能力描述]，[工作风格特点]。

## 输入规范
用户会提供：
- **[输入1]**：[格式说明]，支持 [文件格式列表]
- **[输入2]**（可选）：[说明及默认值]

> 如果 [异常输入情况]，请立即告知用户并 [处理方式]。

## 处理流程

按以下步骤依次执行，每步完成后简要汇报进度：

1. **[动词短语]**：[具体操作说明，包括判断标准]
2. **[动词短语]**：[具体操作说明]
3. **[动词短语]**：[具体操作说明]
4. **[动词短语]**：[具体操作说明]
5. **[动词短语]**：[具体操作说明，含输出动作]

## 输出格式

输出一份 [格式] 的 [文档类型]，结构如下：

​```[格式]
# [输出文档标题]

## [章节1]
[内容描述或示例]

## [章节2]
[内容描述或示例]
​```

同时生成机器可读的 JSON 文件，供下游 Skill 使用：
- `outputs/[N]_[name].json`

## 质量标准
- [可验证的规则1，例如"原文引用不得改写"]
- [可验证的规则2，例如"编号全局唯一"]
- [可验证的规则3]

## 异常处理
- [异常情况1] → [处理方式]
- [异常情况2] → [处理方式]
- [结果为空时] → [处理方式]
```

---

## 6. 通用 Python 脚本模板

将以下模板保存为 `skills/your-skill-name/scripts/run.py`：

```python
#!/usr/bin/env python3
"""
[Skill 名称]
[一句话描述]

Usage:
  python run.py <input_file> [options]

Example:
  python run.py data/input.txt --output-dir outputs
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime

# 可选依赖
try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


# ─────────────────────────────────────────────────────────────────────────────
# Step 1: 读取输入
# ─────────────────────────────────────────────────────────────────────────────

def read_input(file_path: Path) -> str:
    """对应 SKILL.md 步骤 1：读取文档。"""
    suffix = file_path.suffix.lower()
    if suffix in ('.txt', '.md'):
        return file_path.read_text(encoding='utf-8', errors='ignore')
    if suffix == '.docx':
        if not HAS_DOCX:
            print("  ⚠️  python-docx 未安装，降级为纯文本读取。pip install python-docx")
        else:
            doc = docx.Document(str(file_path))
            return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
    return file_path.read_text(encoding='utf-8', errors='ignore')


# ─────────────────────────────────────────────────────────────────────────────
# Step 2: 处理/提取
# ─────────────────────────────────────────────────────────────────────────────

def extract_items(text: str) -> list:
    """对应 SKILL.md 步骤 2：提取核心信息。"""
    items = []
    # TODO: 实现你的提取逻辑
    # 示例：按行提取，跳过空行和注释
    for i, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        items.append({
            'id':      f'ITEM-{i:03d}',
            'content': line,
            'raw':     line,
        })
    return items


# ─────────────────────────────────────────────────────────────────────────────
# Step 3: 分类/分析
# ─────────────────────────────────────────────────────────────────────────────

def classify_items(items: list) -> list:
    """对应 SKILL.md 步骤 3：分类。"""
    for item in items:
        # TODO: 实现分类逻辑
        item['category'] = 'general'
        item['priority'] = '中'
    return items


# ─────────────────────────────────────────────────────────────────────────────
# Step 4: 分析/汇总（可选步骤，复杂 Skill 才需要）
# ─────────────────────────────────────────────────────────────────────────────

def analyze(items: list) -> dict:
    """对应 SKILL.md 步骤 4：分析汇总。"""
    stats = {}
    for item in items:
        cat = item['category']
        stats[cat] = stats.get(cat, 0) + 1
    return stats


# ─────────────────────────────────────────────────────────────────────────────
# Step 5: 输出
# ─────────────────────────────────────────────────────────────────────────────

def render_markdown(filename: str, items: list, stats: dict) -> str:
    """对应 SKILL.md 步骤 5：生成 Markdown 报告。"""
    lines = [
        f"# [Skill 名称] 结果报告",
        "",
        "## 📋 基本信息",
        f"- **来源文件**：{filename}",
        f"- **处理时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- **提取数量**：{len(items)} 条",
        "",
        "## 📊 分类统计",
        "| 类别 | 数量 |",
        "|------|------|",
    ]
    for cat, count in stats.items():
        lines.append(f"| {cat} | {count} |")
    lines += ["", "---", "", "## 🔍 详细结果", ""]
    for item in items:
        lines += [
            f"### {item['id']}",
            f"- **内容**：{item['content']}",
            f"- **类别**：{item['category']}",
            "",
        ]
    return '\n'.join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main：按 SKILL.md 步骤顺序调用，每步打印 [N/M] 日志
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description='[Skill 名称]')
    parser.add_argument('input_file', help='输入文件路径')
    parser.add_argument('--output-dir', default='outputs', help='输出目录')
    args = parser.parse_args()

    input_path = Path(args.input_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"❌ 文件不存在：{input_path}")
        sys.exit(1)

    print(f"🚀 [Skill 名称]")
    print(f"   输入: {input_path}")
    print()

    # ── SKILL.md 步骤 1 ───────────────────────────────────────────────────────
    print("[1/5] 读取输入文件...")
    text = read_input(input_path)
    print(f"      ✓ {len(text)} 字符")

    # ── SKILL.md 步骤 2 ───────────────────────────────────────────────────────
    print("[2/5] 提取核心信息...")
    items = extract_items(text)
    print(f"      ✓ {len(items)} 条")

    # ── SKILL.md 步骤 3 ───────────────────────────────────────────────────────
    print("[3/5] 分类...")
    items = classify_items(items)

    # ── SKILL.md 步骤 4 ───────────────────────────────────────────────────────
    print("[4/5] 汇总分析...")
    stats = analyze(items)
    for cat, count in stats.items():
        print(f"      ✓ {cat}: {count} 条")

    # ── SKILL.md 步骤 5 ───────────────────────────────────────────────────────
    print("[5/5] 写入输出文件...")

    # JSON（机器可读，供下游 Skill 使用）
    json_path = output_dir / 'result.json'
    json_path.write_text(
        json.dumps({
            'source': str(input_path),
            'created_at': datetime.now().isoformat(),
            'total': len(items),
            'items': items,
            'stats': stats,
        }, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f"      ✓ {json_path}")

    # Markdown（人工阅读）
    md_path = output_dir / 'result.md'
    md_path.write_text(
        render_markdown(input_path.name, items, stats),
        encoding='utf-8',
    )
    print(f"      ✓ {md_path}")

    print()
    print(f"🎉 完成！共处理 {len(items)} 条数据")
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

**使用此模板的步骤**：

1. 复制模板到 `skills/your-skill-name/scripts/run.py`
2. 修改 `extract_items()` → 实现你的提取逻辑
3. 修改 `classify_items()` → 实现你的分类逻辑
4. 修改 `render_markdown()` → 调整输出格式
5. 按需增减步骤数（`[1/5]` 改为 `[1/N]`）

---

## 7. 完整示例：从零创建 contract-reviewer Skill

本节用一个完整例子演示整个创建过程。

**目标**：创建一个 Skill，能从合同文本中提取所有付款条款并标注风险等级。

### 7.1 Step 1：定义边界

```
做一件什么事：从合同文本提取付款条款，分析风险
输入：一个合同文件（.txt 或 .docx）
输出：Markdown 报告 + JSON 数据
```

### 7.2 Step 2：写 SKILL.md

创建 `skills/contract-reviewer/SKILL.md`：

```markdown
---
name: contract-reviewer
description: |
  从合同文档中自动提取所有付款条款（付款金额、时间节点、违约条款），
  评估每条款的风险等级，输出结构化的合同审查报告。

  当用户提供一份合同文件，并要求提取付款条款、审查风险、
  生成合同摘要时触发本技能。
---

# 合同审查技能

## 角色定义
你是一位资深合同审查律师（Contract Review Lawyer）。
你擅长从长篇合同中定位关键条款，识别潜在的财务和法律风险。
你的风格：严谨、精准，所有结论必须有原文依据，不做无依据的推断。

## 输入规范
用户会提供一份合同文件的路径，支持格式：`.txt`、`.docx`。

- 合同文件通常包含章节：总则、付款条款、违约与赔偿、争议解决等
- 如果文件格式不支持或无法读取，报错并建议转换

## 处理流程

按以下步骤执行：

1. **读取文档**：打开合同文件，读取全文。
2. **识别章节**：根据标题/编号识别合同结构，列出章节目录。
3. **提取付款条款**：识别所有涉及"付款""金额""到期""逾期""罚款"
   等关键词的句子或段落，记录原文。
4. **风险评级**：对每条款评定风险等级：
   - 🔴 高风险：含无上限罚款、单方终止权、连带责任等
   - 🟡 中风险：含逾期利息、违约金（有上限）等
   - 🟢 低风险：标准付款时间节点，无特殊条件
5. **汇总报告**：统计各风险等级数量，生成建议。

## 输出格式

​```markdown
# 合同付款条款审查报告

## 📋 文档信息
- 文件名：[filename]
- 审查时间：[datetime]
- 提取条款总数：N 条

## 🚨 风险概览
| 风险等级 | 条款数 | 占比 |
|---------|--------|------|
| 🔴 高风险 | ... | ...% |
| 🟡 中风险 | ... | ...% |
| 🟢 低风险 | ... | ...% |

## 🔍 条款明细

### 条款 C-001
- **原文**："[原文摘录]"
- **所在章节**：[章节名]
- **风险等级**：🔴 高风险
- **风险说明**：[具体说明]
​```

## 质量标准
- 每条款"原文"必须引用合同原文，不得改写
- 风险等级必须有明确依据（说明哪个词/哪个条件触发了该等级）
- 不得对合同整体法律效力作出判断（超出本 Skill 范围）

## 异常处理
- 文件不存在 → 报错，检查路径
- 文件无付款相关内容 → 输出"未发现付款条款"，不虚构
- 文件格式不支持 → 报错，建议转 .txt
```

### 7.3 Step 3：用 AI 验证 SKILL.md

让 AI 手动执行一次（无需写脚本）：

```
用户：请使用 contract-reviewer 技能分析这份合同。
AI 执行后，观察：
  ✅ AI 是否按 5 步执行？
  ❌ AI 是否跳过了章节识别步骤？
  ❌ AI 是否把原文改写成了自己的描述？
  ❌ AI 是否给出了格式规范的报告？
```

假设发现问题：AI 跳过了"章节识别"，直接提取，且原文引用被改写。
这意味着需要在脚本里强制执行这两件事。

### 7.4 Step 4：写配套脚本

创建 `skills/contract-reviewer/scripts/review.py`（基于通用模板改写）：

```python
#!/usr/bin/env python3
"""合同付款条款审查 Skill"""

import re, json, sys
from pathlib import Path
from datetime import datetime

# ─── SKILL.md 步骤 2：章节识别 ─────────────────────────────────────────────

def identify_sections(text):
    sections, current = [], {'title': 'Document', 'content': []}
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        if re.match(r'^\d+[\.、]\s+\S', line) or re.match(r'^第[一二三四五六七八九十]+[条章]', line):
            if current['content']: sections.append(dict(current))
            current = {'title': line, 'content': []}
        else:
            current['content'].append(line)
    if current['content']: sections.append(current)
    return sections

# ─── SKILL.md 步骤 3：提取付款条款 ─────────────────────────────────────────

PAY_PATTERNS = [
    r'付款|支付|金额|到期|逾期|罚款|违约金|赔偿|利息|保证金',
]

def extract_clauses(sections):
    clauses, counter = [], 1
    for sec in sections:
        for line in sec['content']:
            if any(re.search(p, line) for p in PAY_PATTERNS) and len(line) > 20:
                clauses.append({
                    'id': f'C-{counter:03d}',
                    'section': sec['title'],
                    'original': line,          # 原文切片，不改写
                })
                counter += 1
    return clauses

# ─── SKILL.md 步骤 4：风险评级 ──────────────────────────────────────────────

HIGH_RISK = r'无上限|连带责任|单方终止|不可抗力.*不免责|全额赔偿'
MID_RISK  = r'逾期利息|违约金|罚款|解除合同|提前还款'

def classify_risk(clauses):
    for c in clauses:
        t = c['original']
        if re.search(HIGH_RISK, t):
            c['risk'] = 'high';    c['risk_icon'] = '🔴'; c['risk_label'] = '高风险'
        elif re.search(MID_RISK, t):
            c['risk'] = 'medium';  c['risk_icon'] = '🟡'; c['risk_label'] = '中风险'
        else:
            c['risk'] = 'low';     c['risk_icon'] = '🟢'; c['risk_label'] = '低风险'
    return clauses

# ─── SKILL.md 步骤 5：生成报告 ──────────────────────────────────────────────

def render_markdown(filename, clauses):
    total = len(clauses)
    high = sum(1 for c in clauses if c['risk'] == 'high')
    mid  = sum(1 for c in clauses if c['risk'] == 'medium')
    low  = sum(1 for c in clauses if c['risk'] == 'low')
    lines = [
        "# 合同付款条款审查报告", "",
        "## 📋 文档信息",
        f"- **文件名**：{filename}",
        f"- **审查时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- **提取条款总数**：{total} 条", "",
        "## 🚨 风险概览",
        "| 风险等级 | 条款数 | 占比 |",
        "|---------|--------|------|",
        f"| 🔴 高风险 | {high} | {high/total*100:.0f}% |" if total else "| 🔴 高风险 | 0 | 0% |",
        f"| 🟡 中风险 | {mid}  | {mid/total*100:.0f}% |" if total else "| 🟡 中风险 | 0 | 0% |",
        f"| 🟢 低风险 | {low}  | {low/total*100:.0f}% |" if total else "| 🟢 低风险 | 0 | 0% |",
        "", "---", "", "## 🔍 条款明细", "",
    ]
    for c in clauses:
        lines += [
            f"### {c['id']}",
            f"- **原文**："{c['original']}"",
            f"- **所在章节**：{c['section']}",
            f"- **风险等级**：{c['risk_icon']} {c['risk_label']}", "",
        ]
    return '\n'.join(lines)

# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description='合同付款条款审查')
    parser.add_argument('contract_file')
    parser.add_argument('--output-dir', default='outputs')
    args = parser.parse_args()

    path = Path(args.contract_file)
    out  = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        print(f"❌ 文件不存在：{path}"); sys.exit(1)

    print("📋 合同付款条款审查 Skill"); print()

    print("[1/5] 读取文档...")
    text = path.read_text(encoding='utf-8', errors='ignore')
    print(f"      ✓ {len(text)} 字符")

    print("[2/5] 识别章节结构...")
    sections = identify_sections(text)
    print(f"      ✓ {len(sections)} 个章节")

    print("[3/5] 提取付款条款...")
    clauses = extract_clauses(sections)
    print(f"      ✓ {len(clauses)} 条")

    print("[4/5] 风险评级...")
    clauses = classify_risk(clauses)
    high = sum(1 for c in clauses if c['risk'] == 'high')
    print(f"      🔴 高风险: {high}  🟡 中风险: {sum(1 for c in clauses if c['risk']=='medium')}  🟢 低风险: {sum(1 for c in clauses if c['risk']=='low')}")

    print("[5/5] 写入输出文件...")
    (out / 'contract_review.json').write_text(
        json.dumps({'total': len(clauses), 'clauses': clauses}, ensure_ascii=False, indent=2),
        encoding='utf-8')
    (out / 'contract_review.md').write_text(
        render_markdown(path.name, clauses), encoding='utf-8')
    print(f"      ✓ outputs/contract_review.md")
    print(); print(f"🎉 审查完成！发现 {high} 条高风险条款")

if __name__ == '__main__':
    sys.exit(main())
```

**目录结构**：

```
skills/contract-reviewer/
├── SKILL.md            ← 描述层（7 个部分）
└── scripts/
    └── review.py       ← 执行层（5 步流程）
```

**运行**：

```powershell
python skills/contract-reviewer/scripts/review.py data/contract.txt
```

---

## 8. Skill 设计检查表

在发布 Skill 前，检查以下所有条目：

### SKILL.md 质量

- [ ] `name` 字段：连字符连接，全小写，描述功能
- [ ] `description`：第一句说功能，明确说明触发条件
- [ ] **角色定义**：有具体职位名（中英文），有能力特点
- [ ] **输入规范**：列出所有支持格式，说明可选参数默认值
- [ ] **处理流程**：每步以动词开头，步骤间有数据流动，4-8 步
- [ ] **输出格式**：有完整示例（含占位符），有 JSON 结构说明
- [ ] **质量标准**：3-6 条可用"是/否"验证的规则
- [ ] **异常处理**：覆盖文件不存在、内容为空、依赖未安装三种情况

### 配套脚本质量

- [ ] 每个 SKILL.md 步骤对应一个函数
- [ ] `main()` 按顺序调用所有函数，每步打印 `[N/M]` 日志
- [ ] 关键数据用原文切片，不用 AI 改写
- [ ] 生成 JSON 中间文件（供下游 Skill 或调试使用）
- [ ] 生成 Markdown 人工可读报告
- [ ] 异常情况打印清晰错误信息，不静默崩溃
- [ ] 有 `argparse` 命令行参数，支持 `--output-dir`

### 功能验证

- [ ] 用真实样本数据运行，无报错
- [ ] 对比 AI 手动执行和脚本执行的结果，关键质量标准一致
- [ ] 空输入/异常输入时输出有意义的错误信息
- [ ] `--output-dir` 参数正确创建目录并写入文件

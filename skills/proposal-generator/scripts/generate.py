#!/usr/bin/env python3
"""
Proposal Generator
Combines RFP questions + search results into a professional bid response document.

Inputs:
  outputs/01_rfp_questions.json    - from extract.py
  outputs/02_search_results.json   - from search_kb.py

Outputs:
  outputs/03_Proposal_Response.md
  outputs/03_Proposal_Response.docx  (only if python-docx is installed)
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    from docx import Document as DocxDocument
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


# ---------------------------------------------------------------------------
# Answer polishing
# ---------------------------------------------------------------------------

_DRAFT_PREFIXES = [
    '我司产品完全满足此项要求，具体如下：',
    '我司具备所需资质和经验，详情如下：',
    '针对此问题，我司的具体说明如下：',
    '我司在此方面的能力超出基本期望：',
    '我司对此项的响应如下：',
]

_OPENERS = {
    'hard_req':      (
        '我司郑重承诺，**完全满足**本项技术要求，具体实现方式如下：'
    ),
    'qualification': (
        '我司在相关领域拥有丰富的实战经验及完整的资质体系，具体情况如下：'
    ),
    'direct':        (
        '针对贵司的提问，我司作出如下详细说明：'
    ),
    'expectation':   (
        '我司在此方面的能力不仅满足基本要求，更具有以下差异化优势：'
    ),
}


def polish_answer(answer_draft: str, question: dict, status: str) -> str:
    """Transform raw draft into formal business-register prose."""
    if not answer_draft or '[待补充' in answer_draft:
        return '[待补充：需相关团队在终稿提交前补充说明]'

    # Strip internal draft markers
    cleaned = answer_draft
    for pfx in _DRAFT_PREFIXES:
        cleaned = cleaned.replace(pfx, '')
    cleaned = cleaned.replace('详见：', '').strip()
    # Remove incomplete trailing fragment markers
    cleaned = re.sub(r'\(⚠️.*?\)', '', cleaned).strip()
    cleaned = re.sub(r'…+$', '', cleaned).strip()

    qtype  = question.get('type', 'hard_req')
    opener = _OPENERS.get(qtype, '我司对此项要求的响应如下：')

    body = cleaned[:600] if cleaned else ''
    result = f"{opener}\n\n{body}" if body else opener

    if status == 'partial_match':
        result += (
            "\n\n> ⚠️ **说明**：以上基于现有产品文档，"
            "部分技术细节需技术团队进一步确认并在正式版中补全。"
        )

    return result


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def render_markdown(
    client: str,
    project: str,
    questions: list,
    results: list,
) -> str:
    r_map = {r['question_id']: r for r in results}

    # Group questions by section (preserve insertion order)
    by_section = {}
    for q in questions:
        by_section.setdefault(q.get('section', '通用要求'), []).append(q)

    full    = sum(1 for r in results if r['status'] == 'full_match')
    partial = sum(1 for r in results if r['status'] == 'partial_match')
    nf      = sum(1 for r in results if r['status'] == 'not_found')
    total   = len(results)

    lines = [
        f"# {client}《{project}》投标响应书",
        "",
        "## 文档信息",
        "| 项目 | 内容 |",
        "|------|------|",
        "| 响应方 | Fabrikam, Inc. |",
        f"| 响应日期 | {datetime.now().strftime('%Y-%m-%d')} |",
        "| 文档版本 | V1.0（初稿，待内部审阅） |",
        "| 保密级别 | 商业机密，未经授权不得外传 |",
        "",
        "---",
        "",
        "## 致辞",
        "",
        f"尊敬的 {client} 评审委员会：",
        "",
        (
            f"衷心感谢贵司就 **{project}** 项目所发出的招标邀请。"
            "我司（Fabrikam, Inc.）在认真研读并充分理解贵司招标文件后，"
            "现以 **EcoSense 360** 智能能源管理解决方案为核心，"
            "按招标书结构逐章响应如下。"
            "我们有充分信心，EcoSense 360 能够全面满足贵司所提出的技术、"
            "商务及可持续发展要求，并在投资回报、运维便利性和长期合作响应力方面"
            "展现出领先优势。"
        ),
        "",
        "---",
        "",
    ]

    # Chapters
    for chap_num, (section_title, qs) in enumerate(by_section.items(), 1):
        lines += [f"## 第 {chap_num} 章：{section_title}", ""]

        for item_num, q in enumerate(qs, 1):
            r = r_map.get(q['id'])

            brief_title = q['summary'][:55]
            lines += [
                f"### {chap_num}.{item_num}  {q['id']} — {brief_title}",
                "",
                "**甲方要求**",
                "",
                f"> {q['original']}",
                "",
                "**我方响应**",
                "",
            ]

            if r:
                polished = polish_answer(
                    r.get('answer_draft', ''),
                    q,
                    r.get('status', ''),
                )
                lines.append(polished)

                if r.get('best_quote') and r['status'] != 'not_found':
                    lines += [
                        "",
                        "*参考依据*",
                        f"> 来源：`{r.get('source_doc', '（文档）')}`"
                        f" ＞ {r.get('source_section', '（章节）')}",
                        f"> \"{r['best_quote'][:250]}\"",
                    ]
            else:
                lines.append('[待补充：需相关团队在终稿提交前补充说明]')

            lines += ["", "---", ""]

    # Appendix – pending items
    need_followup = [r for r in results if r['status'] != 'full_match']
    if need_followup:
        lines += [
            "## 附录 A：待补充事项清单",
            "",
            "以下问题在现有知识库中未能完全覆盖，**请相关团队在提交终稿前补充**：",
            "",
            "| 编号 | 问题摘要 | 状态 | 建议负责人 |",
            "|------|---------|------|-----------|",
        ]
        for r in need_followup:
            summary = r['question_text'][:50].replace('|', '\\|')
            team = (
                '安全/合规团队'
                if re.search(r'secur|encrypt|iso|certif', r['question_text'], re.I)
                else '产品/技术团队'
            )
            lines.append(
                f"| {r['question_id']} | {summary}… | {r['status_icon']} | {team} |"
            )
        lines.append("")

    # Quality self-check
    lines += [
        "---",
        "",
        "## 质量自检报告（由生成脚本自动生成）",
        "",
        f"- **响应问题总数**：{total}",
        f"- ✅ 完全匹配（有原文依据）：{full} 个（{full/total*100:.0f}%）",
        f"- ⚠️ 部分匹配（需补充细节）：{partial} 个",
        f"- ❌ 未找到（需人工填写）：{nf} 个",
        f"- **待补充占位符数量**：{nf + partial} 个",
        "",
        "_提示：提交前请通过全局搜索「待补充」确认所有占位符已填写完毕。_",
        "",
        "---",
        f"*本文档由 bid-response-agent 自动生成 @ {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ]

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# DOCX export
# ---------------------------------------------------------------------------

def _add_bold_para(doc, text: str):
    """Add paragraph with **bold** markdown rendered as actual bold."""
    para = doc.add_paragraph()
    parts = re.split(r'\*\*(.*?)\*\*', text)
    for i, part in enumerate(parts):
        run = para.add_run(part)
        run.bold = (i % 2 == 1)


def save_docx(output_path: Path, md_content: str) -> bool:
    if not HAS_DOCX:
        print(
            "  ℹ️  python-docx 未安装，跳过 .docx 导出。"
            "  安装命令: pip install python-docx"
        )
        return False

    doc = DocxDocument()

    for line in md_content.splitlines():
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            doc.add_heading(stripped[2:], level=1)
        elif stripped.startswith('## '):
            doc.add_heading(stripped[3:], level=2)
        elif stripped.startswith('### '):
            doc.add_heading(stripped[4:], level=3)
        elif stripped.startswith('> '):
            p = doc.add_paragraph(stripped[2:])
            p.style = 'Quote'
        elif stripped == '---':
            doc.add_paragraph('─' * 50)
        elif stripped:
            _add_bold_para(doc, stripped)

    try:
        doc.save(str(output_path))
    except PermissionError:
        print(f"      ⚠️  无法写入 {output_path.name}（文件可能已在 Word 中打开）。"
              f"  请关闭文件后重新运行，或使用 --skip-extract --skip-search 跳过前两步。")
        return False
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Proposal Generator — Step 3 of Bid Response Pipeline',
        epilog=(
            'Example: python generate.py '
            '--client "VanArsdel, Ltd." '
            '--project "Smart Energy Management Solution"'
        ),
    )
    parser.add_argument('--questions',       default='outputs/01_rfp_questions.json')
    parser.add_argument('--search-results',  default='outputs/02_search_results.json')
    parser.add_argument('--client',          default='客户')
    parser.add_argument('--project',         default='项目')
    parser.add_argument('--output-dir',      default='outputs')
    args = parser.parse_args()

    q_path      = Path(args.questions)
    s_path      = Path(args.search_results)
    output_dir  = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for p in (q_path, s_path):
        if not p.exists():
            print(f"❌ Error: File not found: {p}")
            print("   Please run the previous pipeline steps first.")
            sys.exit(1)

    print("📝 Proposal Generator")
    print(f"   Client:  {args.client}")
    print(f"   Project: {args.project}")
    print()

    print("[1/5] 加载数据...")
    with open(q_path, encoding='utf-8') as f:
        q_data = json.load(f)
    with open(s_path, encoding='utf-8') as f:
        s_data = json.load(f)
    questions = q_data['questions']
    results   = s_data['results']
    print(f"      ✓ {len(questions)} 个问题，{len(results)} 条检索结果")

    print("[2/5] 内容梳理（按 RFP 章节顺序排列）...")
    by_section = {}
    for q in questions:
        by_section.setdefault(q.get('section', '通用要求'), []).append(q['id'])
    for sec, qids in by_section.items():
        print(f"      · {sec} ({len(qids)} 个)")

    print("[3/5] 回答润色（口语化 → 正式商务语体）...")
    r_map  = {r['question_id']: r for r in results}
    polished = sum(
        1 for q in questions
        if r_map.get(q['id']) and r_map[q['id']]['status'] != 'not_found'
    )
    print(f"      ✓ 润色 {polished} 个回答")

    print("[4/5] 质量自检...")
    full    = sum(1 for r in results if r['status'] == 'full_match')
    partial = sum(1 for r in results if r['status'] == 'partial_match')
    nf      = sum(1 for r in results if r['status'] == 'not_found')
    total   = len(results)
    print(f"      ✓ 完全匹配 {full}  部分匹配 {partial}  未找到 {nf}")
    print(f"      ✓ 待补充占位符：{nf + partial} 个")
    print(f"      ✓ 章节覆盖：{len(by_section)} 章")

    print("[5/5] 生成文件...")
    md_content = render_markdown(args.client, args.project, questions, results)

    md_path = output_dir / '03_Proposal_Response.md'
    md_path.write_text(md_content, encoding='utf-8')
    print(f"      ✓ Markdown: {md_path}")

    docx_path = output_dir / '03_Proposal_Response.docx'
    if save_docx(docx_path, md_content):
        print(f"      ✓ Word 文档: {docx_path}")

    print()
    print("🎉 投标响应书生成完成！")
    if nf + partial:
        print(f"   ⚠️  {nf + partial} 个问题需人工补充（搜索文档中的「待补充」）")
    return 0


if __name__ == '__main__':
    sys.exit(main())

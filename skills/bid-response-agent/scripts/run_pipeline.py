#!/usr/bin/env python3
"""
Bid Response Agent — Full Pipeline Orchestrator
Runs all three steps end-to-end and generates an executive summary.

Usage:
  python run_pipeline.py <rfp_file> <kb_dir> [options]

Examples:
  python skills/bid-response-agent/scripts/run_pipeline.py \\
      materials/VanArsdel_RFP.txt materials/ \\
      --client "VanArsdel, Ltd." \\
      --project "Smart Energy Management Solution"
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _scripts_root() -> Path:
    """Return the skills/ root directory (two levels up from this script)."""
    return Path(__file__).resolve().parent.parent.parent


def run_step(script: Path, argv: list, label: str) -> bool:
    """Execute a Python script as a subprocess. Returns True on success."""
    cmd = [sys.executable, str(script)] + argv
    print()
    print(f"{'═' * 62}")
    print(f"  {label}")
    print(f"{'═' * 62}")
    print(f"  $ python {script.name} {' '.join(argv)}")
    print()

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n  ❌ {label} 失败 (exit code {result.returncode})")
        return False
    return True


# ---------------------------------------------------------------------------
# Executive summary
# ---------------------------------------------------------------------------

def write_executive_summary(
    output_dir: Path,
    rfp_file: str,
    kb_dir: str,
    client: str,
    project: str,
) -> Path:
    q_path = output_dir / '01_rfp_questions.json'
    s_path = output_dir / '02_search_results.json'

    q_count = full = partial = nf = 0

    if q_path.exists():
        with open(q_path, encoding='utf-8') as f:
            q_count = len(json.load(f).get('questions', []))

    if s_path.exists():
        with open(s_path, encoding='utf-8') as f:
            results = json.load(f).get('results', [])
        full    = sum(1 for r in results if r['status'] == 'full_match')
        partial = sum(1 for r in results if r['status'] == 'partial_match')
        nf      = sum(1 for r in results if r['status'] == 'not_found')

    total      = q_count or 1  # avoid div/0
    match_rate = (full + partial) / total * 100

    lines = [
        "# 投标响应流程执行摘要",
        "",
        "## 📋 执行信息",
        f"- **执行时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- **RFP 文档**：{rfp_file}",
        f"- **知识库路径**：{kb_dir}",
        f"- **甲方**：{client}",
        f"- **项目**：{project}",
        "",
        "## 📊 执行结果",
        "| 阶段 | 状态 | 关键输出 |",
        "|------|------|---------|",
        f"| 1️⃣ RFP 问题提取 | ✅ 完成 | {q_count} 个问题 → `01_RFP_Questions.md` |",
        f"| 2️⃣ 知识库检索   | ✅ 完成 | 命中率 {match_rate:.0f}% → `02_Knowledge_Search_Report.md` |",
        f"| 3️⃣ 投标书生成   | ✅ 完成 | → `03_Proposal_Response.md` |",
        "",
        "## 🎯 知识匹配统计",
        "| 状态 | 数量 | 占比 |",
        "|------|------|------|",
        f"| ✅ 完全匹配 | {full}    | {full/total*100:.0f}% |",
        f"| ⚠️ 部分匹配 | {partial} | {partial/total*100:.0f}% |",
        f"| ❌ 未找到   | {nf}      | {nf/total*100:.0f}% |",
        "",
    ]

    if match_rate < 50:
        lines += [
            "> ⚠️ **警告**：知识库命中率低于 50%，建议检查文档完整性。",
            "",
        ]

    lines += [
        "## 📁 输出文件一览",
        "",
        "| 文件 | 格式 | 说明 |",
        "|------|------|------|",
        "| `01_RFP_Questions.md`           | Markdown | RFP 问题清单（含优先级、依赖） |",
        "| `01_rfp_questions.json`          | JSON     | 问题数据（流水线中间件） |",
        "| `02_Knowledge_Search_Report.md` | Markdown | 知识库检索报告（含原文摘录）|",
        "| `02_search_results.json`         | JSON     | 检索结果（流水线中间件） |",
        "| `03_Proposal_Response.md`        | Markdown | 投标响应书初稿 |",
        "| `03_Proposal_Response.docx`      | Word     | （需 python-docx）|",
        "| `04_Executive_Summary.md`        | Markdown | 本执行摘要 |",
        "",
        "## ⚡ 下一步行动",
        "",
    ]

    step = 1
    if nf:
        lines.append(
            f"{step}. **【必须】** 填写 {nf} 个 `[待补充]` 占位符"
            f"（全局搜索「待补充」定位）"
        )
        step += 1
    if partial:
        lines.append(
            f"{step}. **【建议】** 审阅 {partial} 个部分匹配回答，"
            f"确认技术信息是否准确完整"
        )
        step += 1
    lines += [
        f"{step}. 将初稿发送给售前/产品/技术团队内部审阅",
        f"{step+1}. 根据甲方格式要求调整排版（字体、页眉页脚等）",
        f"{step+2}. 终稿签字并按时提交",
        "",
        "---",
        f"*由 bid-response-agent 自动生成 @ {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ]

    path = output_dir / '04_Executive_Summary.md'
    path.write_text('\n'.join(lines), encoding='utf-8')
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Bid Response Agent — End-to-End Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('rfp_file',    help='RFP document path (.txt or .docx)')
    parser.add_argument('kb_dir',      help='Knowledge base directory path')
    parser.add_argument('--client',    default='客户',
                        help='Client company name (used in proposal header)')
    parser.add_argument('--project',   default='项目',
                        help='Project name (used in proposal header)')
    parser.add_argument('--output-dir', default='outputs',
                        help='Output directory (default: outputs)')
    parser.add_argument('--skip-extract', action='store_true',
                        help='Skip step 1 if 01_rfp_questions.json already exists')
    parser.add_argument('--skip-search',  action='store_true',
                        help='Skip step 2 if 02_search_results.json already exists')
    args = parser.parse_args()

    skills_root = _scripts_root()
    extract_py  = skills_root / 'rfp-question-extractor' / 'scripts' / 'extract.py'
    search_py   = skills_root / 'knowledge-searcher'     / 'scripts' / 'search_kb.py'
    generate_py = skills_root / 'proposal-generator'     / 'scripts' / 'generate.py'

    for script in (extract_py, search_py, generate_py):
        if not script.exists():
            print(f"❌ Script not found: {script}")
            sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print()
    print("🚀 Bid Response Agent — Full Pipeline")
    print(f"   RFP 文档:  {args.rfp_file}")
    print(f"   知识库:    {args.kb_dir}")
    print(f"   客户:      {args.client}")
    print(f"   项目:      {args.project}")
    print(f"   输出目录:  {output_dir.resolve()}")

    # ── Step 1: Extract ──────────────────────────────────────────────────────
    q_json = output_dir / '01_rfp_questions.json'
    if args.skip_extract and q_json.exists():
        print("\n[Step 1/3] RFP 问题提取 ── 使用已有结果（--skip-extract）")
    else:
        ok = run_step(
            extract_py,
            [args.rfp_file, '--output-dir', str(output_dir)],
            'Step 1 / 3 — RFP 问题提取',
        )
        if not ok:
            sys.exit(1)

    # ── Step 2: Search ───────────────────────────────────────────────────────
    s_json = output_dir / '02_search_results.json'
    if args.skip_search and s_json.exists():
        print("\n[Step 2/3] 知识库检索 ── 使用已有结果（--skip-search）")
    else:
        # Automatically exclude the source RFP to avoid self-matching
        ok = run_step(
            search_py,
            [
                args.kb_dir,
                '--questions',   str(q_json),
                '--output-dir',  str(output_dir),
                '--exclude',     args.rfp_file,
            ],
            'Step 2 / 3 — 知识库检索',
        )
        if not ok:
            sys.exit(1)

    # ── Step 3: Generate ─────────────────────────────────────────────────────
    ok = run_step(
        generate_py,
        [
            '--questions',      str(q_json),
            '--search-results', str(s_json),
            '--client',         args.client,
            '--project',        args.project,
            '--output-dir',     str(output_dir),
        ],
        'Step 3 / 3 — 投标响应书生成',
    )
    if not ok:
        sys.exit(1)

    # ── Executive summary ────────────────────────────────────────────────────
    print()
    print(f"{'═' * 62}")
    print("  执行摘要")
    print(f"{'═' * 62}")
    summary = write_executive_summary(
        output_dir, args.rfp_file, args.kb_dir, args.client, args.project
    )
    print(f"  ✓ {summary}")

    # ── Final report ─────────────────────────────────────────────────────────
    print()
    print(f"{'═' * 62}")
    print("  ✅  Pipeline 全部完成！")
    print(f"{'═' * 62}")
    print(f"\n  📁 输出目录: {output_dir.resolve()}")
    print("     01_RFP_Questions.md            RFP 问题清单")
    print("     02_Knowledge_Search_Report.md  知识库检索报告")
    print("     03_Proposal_Response.md        投标响应书")
    print("     04_Executive_Summary.md        执行摘要")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Support Case Analyzer
Reads a customer support case Excel file and generates a structured analysis report.

Input:  <cases.xlsx>  — Excel with columns:
        Customer, Case ID, Date Opened, Issue Type, Module,
        Severity, Resolution Time (hrs), Escalated

Outputs:
  outputs/support_case_analysis.md
  outputs/support_case_analysis.json
"""

import sys
import json
from pathlib import Path
from datetime import datetime

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    # csv is std-lib, useful as fallback for .csv files
    import csv
    HAS_CSV = True
except ImportError:
    HAS_CSV = False


# ---------------------------------------------------------------------------
# File reading
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {
    'Customer',
    'Case ID',
    'Date Opened',
    'Issue Type',
    'Module',
    'Severity',
    'Resolution Time (hrs)',
    'Escalated',
}


def read_excel(file_path: Path) -> tuple:
    """Return (headers, rows) where rows are dicts."""
    if not HAS_OPENPYXL:
        print("❌ openpyxl 未安装，无法读取 Excel 文件。")
        print("   安装命令: pip install openpyxl")
        sys.exit(1)

    wb = openpyxl.load_workbook(str(file_path), read_only=True, data_only=True)
    ws = wb.active

    rows_iter = ws.iter_rows(values_only=True)
    raw_headers = next(rows_iter, None)
    if raw_headers is None:
        print("❌ Excel 文件为空或无法读取表头。")
        sys.exit(1)

    headers = [str(h).strip() if h is not None else '' for h in raw_headers]

    missing = REQUIRED_FIELDS - set(headers)
    if missing:
        print(f"❌ Excel 文件缺少以下必要字段：{', '.join(sorted(missing))}")
        print("   请确认表头行与规范一致后重试。")
        sys.exit(1)

    rows = []
    for raw in rows_iter:
        row = {headers[i]: raw[i] for i in range(len(headers))}
        rows.append(row)

    wb.close()
    return headers, rows


def read_csv(file_path: Path) -> tuple:
    with open(file_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        missing = REQUIRED_FIELDS - set(headers)
        if missing:
            print(f"❌ CSV 文件缺少字段：{', '.join(sorted(missing))}")
            sys.exit(1)
        rows = list(reader)
    return headers, rows


def load_cases(file_path: Path) -> list:
    suffix = file_path.suffix.lower()
    if suffix in ('.xlsx', '.xls'):
        _, rows = read_excel(file_path)
    elif suffix == '.csv':
        _, rows = read_csv(file_path)
    else:
        print(f"❌ 不支持的文件格式: {suffix}。请使用 .xlsx 或 .csv。")
        sys.exit(1)

    # Filter out completely empty rows
    cases = [
        r for r in rows
        if any(v for v in r.values() if v is not None and str(v).strip())
    ]
    return cases


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def _str(val) -> str:
    return str(val).strip() if val is not None else ''


def _float(val) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def analyze(cases: list) -> dict:
    if not cases:
        return {}

    total = len(cases)

    # Time range
    dates = []
    for c in cases:
        d = _str(c.get('Date Opened'))
        if d:
            dates.append(d)
    date_min = min(dates) if dates else 'N/A'
    date_max = max(dates) if dates else 'N/A'

    # Issue type counts
    issue_counts = {}
    for c in cases:
        it = _str(c.get('Issue Type')) or '(未分类)'
        issue_counts[it] = issue_counts.get(it, 0) + 1
    top3 = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    # Severity distribution
    sev_counts = {}
    for c in cases:
        sev = _str(c.get('Severity')) or '(未知)'
        sev_counts[sev] = sev_counts.get(sev, 0) + 1

    # Resolution time
    res_times = [_float(c.get('Resolution Time (hrs)')) for c in cases]
    valid_times = [t for t in res_times if t > 0]
    avg_res_time = sum(valid_times) / len(valid_times) if valid_times else 0.0

    # Resolution by issue type
    res_by_type = {}
    for c in cases:
        it = _str(c.get('Issue Type')) or '(未分类)'
        t  = _float(c.get('Resolution Time (hrs)'))
        if t > 0:
            res_by_type.setdefault(it, []).append(t)
    avg_by_type = {
        k: round(sum(v) / len(v), 1)
        for k, v in res_by_type.items()
    }

    # Escalation
    escalated = sum(
        1 for c in cases
        if _str(c.get('Escalated')).lower() in ('yes', 'true', '1', 'y')
    )
    escalation_rate = escalated / total * 100

    # Escalation by issue type
    esc_by_type = {}
    total_by_type = {}
    for c in cases:
        it  = _str(c.get('Issue Type')) or '(未分类)'
        esc = _str(c.get('Escalated')).lower() in ('yes', 'true', '1', 'y')
        total_by_type[it] = total_by_type.get(it, 0) + 1
        if esc:
            esc_by_type[it] = esc_by_type.get(it, 0) + 1
    esc_rates = {
        k: round(esc_by_type.get(k, 0) / total_by_type[k] * 100, 1)
        for k in total_by_type
    }
    highest_esc_type = max(esc_rates, key=esc_rates.get) if esc_rates else 'N/A'

    return {
        'total':            total,
        'date_min':         date_min,
        'date_max':         date_max,
        'issue_counts':     issue_counts,
        'top3':             top3,
        'sev_counts':       sev_counts,
        'avg_res_time':     round(avg_res_time, 1),
        'avg_by_type':      avg_by_type,
        'escalated':        escalated,
        'escalation_rate':  round(escalation_rate, 1),
        'esc_rates':        esc_rates,
        'highest_esc_type': highest_esc_type,
    }


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

def generate_recommendations(stats: dict) -> list:
    recs = []

    # Escalation
    if stats['escalation_rate'] > 20:
        recs.append(
            f"**降低升级率**：总体升级率 {stats['escalation_rate']}% 偏高，"
            f"「{stats['highest_esc_type']}」类型升级率最高（"
            f"{stats['esc_rates'].get(stats['highest_esc_type'], 0)}%）。"
            "建议为该类型建立专属快速响应通道并强化一线技术培训。"
        )

    # Top issue type
    if stats['top3']:
        top_type, top_count = stats['top3'][0]
        top_pct = top_count / stats['total'] * 100
        recs.append(
            f"**高频问题专项治理**：「{top_type}」占全部案例 {top_pct:.1f}%，"
            "是最主要问题类型。建议建立专项知识库和自助解决流程，"
            "减少同类工单重复进入队列。"
        )

    # Resolution time
    slowest = max(stats['avg_by_type'].items(), key=lambda x: x[1], default=('', 0))
    if slowest[1] > stats['avg_res_time'] * 1.5:
        recs.append(
            f"**缩短高耗时类型解决时长**：「{slowest[0]}」平均解决时间 "
            f"{slowest[1]} 小时，远高于全局均值 {stats['avg_res_time']} 小时。"
            "建议分析根因，考虑引入专家支撑团队或自动化诊断工具。"
        )

    # Critical severity
    critical_count = stats['sev_counts'].get('Critical', 0)
    if critical_count > stats['total'] * 0.15:
        recs.append(
            f"**Critical 案例占比偏高**（{critical_count} 个，"
            f"{critical_count / stats['total'] * 100:.1f}%）。"
            "建议建立 Critical 专项看板，并设置自动升级触发规则，"
            "确保 P0 问题在 2 小时内获得响应。"
        )

    if len(recs) < 3:
        recs.append(
            "**定期知识沉淀**：将高频问题标准化为 FAQ 和操作手册，"
            "赋能客户自助解决，降低工单总量。"
        )

    return recs


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render_markdown(filename: str, stats: dict) -> str:
    if not stats:
        return "# 客服案例分析简报\n\n⚠️ 无有效数据。\n"

    lines = [
        "# 客服案例分析简报",
        "",
        f"**分析文件**：{filename}  ",
        f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 📊 数据概览",
        f"- **分析周期**：{stats['date_min']} ～ {stats['date_max']}",
        f"- **案例总数**：{stats['total']} 条",
        "",
        "---",
        "",
        "## 🔍 Top 3 高频问题类型",
        "| 排名 | 问题类型 | 案例数 | 占比 |",
        "|------|---------|--------|------|",
    ]
    for i, (itype, cnt) in enumerate(stats['top3'], 1):
        pct = cnt / stats['total'] * 100
        lines.append(f"| {i} | {itype} | {cnt} | {pct:.1f}% |")

    lines += [
        "",
        "## 📈 严重程度分布",
        "| 级别 | 案例数 | 占比 |",
        "|------|--------|------|",
    ]
    for level in ('Critical', 'High', 'Medium', 'Low'):
        cnt = stats['sev_counts'].get(level, 0)
        pct = cnt / stats['total'] * 100
        lines.append(f"| {level} | {cnt} | {pct:.1f}% |")

    # Other severities not in standard list
    for sev, cnt in stats['sev_counts'].items():
        if sev not in ('Critical', 'High', 'Medium', 'Low'):
            pct = cnt / stats['total'] * 100
            lines.append(f"| {sev} | {cnt} | {pct:.1f}% |")

    lines += [
        "",
        "## ⏱️ 解决效率",
        f"- **全局平均解决时间**：{stats['avg_res_time']} 小时",
        "",
        "按问题类型分组：",
        "| 问题类型 | 平均解决时间 (hrs) | 案例数 |",
        "|---------|-------------------|--------|",
    ]
    for itype, avg_t in sorted(stats['avg_by_type'].items(), key=lambda x: x[1], reverse=True):
        cnt = stats['issue_counts'].get(itype, 0)
        lines.append(f"| {itype} | {avg_t} | {cnt} |")

    lines += [
        "",
        "## 🚨 升级率分析",
        f"- **总体升级率**：{stats['escalation_rate']}%  ({stats['escalated']} / {stats['total']} 条)",
        f"- **升级率最高类型**：{stats['highest_esc_type']}"
        f" （{stats['esc_rates'].get(stats['highest_esc_type'], 0)}%）",
        "",
        "各类型升级率：",
        "| 问题类型 | 升级率 |",
        "|---------|--------|",
    ]
    for itype, rate in sorted(stats['esc_rates'].items(), key=lambda x: x[1], reverse=True):
        lines.append(f"| {itype} | {rate}% |")

    # Recommendations
    recs = generate_recommendations(stats)
    lines += ["", "## 💡 改进建议", ""]
    for i, rec in enumerate(recs, 1):
        lines.append(f"{i}. {rec}")

    lines += [
        "",
        "---",
        f"*本报告由 support-case-analyzer 自动生成 @ "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ]

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Support Case Analyzer — generates a structured analysis report',
        epilog='Example: python analyze.py data/cases.xlsx'
    )
    parser.add_argument('cases_file', help='Path to cases Excel (.xlsx) or CSV file')
    parser.add_argument('--output-dir', default='outputs',
                        help='Output directory (default: outputs)')
    args = parser.parse_args()

    cases_path = Path(args.cases_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not cases_path.exists():
        print(f"❌ Error: File not found: {cases_path}")
        sys.exit(1)

    print("📊 Support Case Analyzer")
    print(f"   Input: {cases_path}")
    print()

    print("[1/7] 读取数据文件...")
    cases = load_cases(cases_path)
    print(f"      ✓ {len(cases)} 条案例")

    if len(cases) < 10:
        print("      ⚠️  样本量不足 10 条，分析结论仅供参考。")

    print("[2/7] 统计案例总量与时间范围...")
    print("[3/7] 分析 Top 3 高频问题类型...")
    print("[4/7] 计算严重程度分布...")
    print("[5/7] 计算解决效率（全局 + 分类）...")
    print("[6/7] 分析升级率...")
    stats = analyze(cases)
    print(
        f"      ✓ 总体升级率 {stats['escalation_rate']}%，"
        f"平均解决时间 {stats['avg_res_time']} 小时"
    )

    print("[7/7] 生成改进建议 & 写入输出文件...")
    md_content = render_markdown(cases_path.name, stats)

    md_path = output_dir / 'support_case_analysis.md'
    md_path.write_text(md_content, encoding='utf-8')

    json_path = output_dir / 'support_case_analysis.json'
    json_path.write_text(
        json.dumps(
            {'file': str(cases_path), 'generated_at': datetime.now().isoformat(),
             'stats': stats},
            ensure_ascii=False, indent=2
        ),
        encoding='utf-8',
    )

    print(f"      ✓ {md_path}")
    print(f"      ✓ {json_path}")
    print()
    print("🎉 完成！")
    return 0


if __name__ == '__main__':
    sys.exit(main())

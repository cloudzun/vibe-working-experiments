#!/usr/bin/env python3
"""
RFP Question Extractor
Reads an RFP document (.txt, .md, or .docx) and extracts all structured questions.

Outputs:
  outputs/01_RFP_Questions.md     - Human-readable Markdown report
  outputs/01_rfp_questions.json   - Machine-readable data for pipeline
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime
from itertools import groupby

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


# ---------------------------------------------------------------------------
# File reading
# ---------------------------------------------------------------------------

def read_file(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix in ('.txt', '.md'):
        return file_path.read_text(encoding='utf-8', errors='ignore')
    if suffix == '.docx':
        if not HAS_DOCX:
            print("  Warning: python-docx not installed (pip install python-docx).")
            print("  Falling back to plain-text read – formatting may be lost.")
            return file_path.read_text(encoding='utf-8', errors='ignore')
        doc = docx.Document(str(file_path))
        return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
    # Fallback
    return file_path.read_text(encoding='utf-8', errors='ignore')


# ---------------------------------------------------------------------------
# Section identification
# ---------------------------------------------------------------------------

def identify_sections(text: str) -> list:
    """Split text into sections using heading heuristics."""
    sections = []
    current = {'title': 'Document Header', 'content': []}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Heading patterns (ordered from most-specific to least)
        if re.match(r'^\d+\.\d+\s+\S', line):           # "1.1 Sub-Section"
            _flush(sections, current)
            current = {'title': line, 'content': []}
        elif re.match(r'^\d+\.\s+\S', line):             # "1. Section Title"
            _flush(sections, current)
            current = {'title': line, 'content': []}
        elif re.match(r'^#{1,3}\s+\S', line):            # Markdown headings
            _flush(sections, current)
            current = {'title': re.sub(r'^#+\s+', '', line), 'content': []}
        elif len(line) > 5 and line == line.upper() and not re.search(r'\d', line):
            # ALL-CAPS lines with no digits  →  treat as heading
            _flush(sections, current)
            current = {'title': line, 'content': []}
        else:
            current['content'].append(line)

    _flush(sections, current)
    return sections


def _flush(sections, current):
    if current['content']:
        sections.append(dict(current))


# ---------------------------------------------------------------------------
# Question classification
# ---------------------------------------------------------------------------

# Patterns ordered: most-explicit types first, imperative verbs last for hard_req
PATTERNS = {
    'direct': [
        r'\?\s*$',
        r'\bplease\s+(describe|provide|explain|list|detail|specify|submit|include|outline)\b',
        r'\b请\s*(说明|提供|描述|列出|详述|填写)\b',
    ],
    'qualification': [
        r'\b(at\s+least|minimum|not\s+less\s+than|no\s+fewer\s+than)\b',
        r'\b(demonstrated|proven|references?|certif(ied|ication)|accredit|credential|qualification)\b',
        r'\b(experience\s+in|years?\s+of\s+experience)\b',
        r'\b(具备|至少|不少于|资质|认证|经验)\b',
    ],
    'expectation': [
        r'\b(should|prefer(red|ably)?|recommend(ed)?|ideally|optionally|as\s+a\s+plus|bonus|希望|建议|期望|优先|加分)\b',
    ],
    'hard_req': [
        r'\b(must|shall|required|mandatory|requirement|compliance|comply|必须|应当|需要|要求)\b',
        # Imperative verbs at (or near) the start of the string
        r'(?i)^(deploy|supply|install|integrate|provide|ensure|support|enable|achieve|deliver|'
        r'implement|maintain|include|use|secure|conduct|submit|offer|demonstrate|'
        r'address|prepare|design|develop|create|establish|configure|manage|monitor|'
        r'describe|outline|detail|present|show|explain)',
    ],
}

TYPE_META = {
    'direct':        {'icon': '🔴', 'label': '直接问题',  'priority': '高'},
    'hard_req':      {'icon': '🟡', 'label': '硬性要求',  'priority': '高'},
    'expectation':   {'icon': '🟢', 'label': '期望描述',  'priority': '中'},
    'qualification': {'icon': '🔵', 'label': '资质门槛',  'priority': '高'},
}

# ---------------------------------------------------------------------------
# Section-aware extraction
# Lines in these sections are treated as questions even without explicit
# trigger keywords, because the section context tells us they are requirements.
# ---------------------------------------------------------------------------

SECTION_DEFAULT_TYPES = [
    (r'project\s+objectives?|objectives?\s*$',                    'hard_req'),
    (r'scope\s+of\s+work|scope\s*$',                              'hard_req'),
    (r'technical\s+req|specifications?\s*$|requirements?\s*$',    'hard_req'),
    (r'evaluation\s+crit|scoring\s+crit|evaluation\s+factor',     'expectation'),
    (r'vendor\s+qual|qualif|supplier\s+req',                      'qualification'),
    (r'submission\s+instruct|proposal\s+submission',              'hard_req'),
]


def section_default_type(title: str) -> str:
    """
    Return a fallback question type for all content lines in a known
    requirement section, or '' if the section has no default type.
    """
    t = title.lower()
    for pat, qtype in SECTION_DEFAULT_TYPES:
        if re.search(pat, t):
            return qtype
    return ''


def is_excluded_line(line: str) -> bool:
    """
    Return True for lines that should never be treated as requirements,
    even if they appear inside a requirement section.
    Filters: email addresses, contact/deadline labels, placeholder tokens.
    """
    if re.search(r'\b@\w+\.\w{2,}\b', line):                              # email
        return True
    if re.search(r'^\s*(Deadline|Phone|Email|Address|Contact):', line,
                 re.IGNORECASE):                                            # key: value labels
        return True
    if re.search(r'\[Insert\b|\[TBD\b|\[placeholder', line, re.IGNORECASE):  # placeholder tokens
        return True
    return False


def classify_line(line: str) -> str:
    """Return question type key, or empty string if not a question."""
    s = line.lower()
    for qtype in ('direct', 'qualification', 'expectation', 'hard_req'):
        for pat in PATTERNS[qtype]:
            if re.search(pat, s, re.IGNORECASE):
                return qtype
    return ''


# ---------------------------------------------------------------------------
# Response hints
# ---------------------------------------------------------------------------

HINT_RULES = [
    (r'sso|single\s+sign', '需确认 SSO/OAuth/SAML 集成能力'),
    (r'encrypt|tls|ssl|https',    '需提供加密方案（传输层 + 静态数据）证明'),
    (r'iso\s*27001',               '需提供 ISO 27001 认证文件'),
    (r'\bapi\b|open\s+api',        '需提供 API 文档及第三方集成案例'),
    (r'sensor|iot',                '需确认传感器类型、通讯协议及覆盖范围'),
    (r'cloud|portal',              '需展示云平台架构和移动端功能截图'),
    (r'scal(e|able|ability)',      '需说明弹性扩展架构（多属性/跨地区）'),
    (r'certif|leed|energy\s+star', '需提供认证支持文档或已获认证案例'),
    (r'support|maintenance',       '需说明技术支持体系、SLA 及运维团队'),
    (r'training',                  '需列出培训计划、课程大纲及交付方式'),
    (r'monitor|real.?time',        '需展示实时监控仪表盘和告警功能'),
    (r'report|analytic',           '需展示报告模板和自定义分析功能'),
    (r'integrat|pms|bms',          '需说明与 PMS/BMS 系统的集成方案'),
    (r'demand\s+response',         '需展示需求响应自动化功能'),
    (r'hvac|lighting|plug\s+load', '需展示设备自动控制策略'),
    (r'mobile|ios|android',        '需展示移动 App 功能演示或截图'),
    (r'reference|similar\s+project','必须准备 3+ 个酒店类似项目参考联系人'),
    (r'experience|track\s+record', '需提供酒店行业项目经验清单和案例'),
    (r'payback|roi|cost',          '需提供 ROI 测算模型或过往节能数据'),
    (r'sustainab|footprint|carbon','需提供碳减排数据及可持续发展声明'),
    (r'wireless|zigbee|wi.fi',     '需列出无线协议支持范围及覆盖方案'),
]

DEFAULT_HINTS = {
    'direct':        '需提供具体数据和案例支撑',
    'hard_req':      '需明确承诺满足，并提供产品证据或功能截图',
    'expectation':   '可作为亮点和差异化项详细说明',
    'qualification': '需准备书面证明材料或联系人清单',
}


def get_hint(text: str, qtype: str) -> str:
    tl = text.lower()
    for pat, hint in HINT_RULES:
        if re.search(pat, tl):
            return hint
    return DEFAULT_HINTS.get(qtype, '需明确回应')


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------

def extract_questions(sections: list) -> list:
    questions = []
    counter = 1

    for section in sections:
        sec_default = section_default_type(section['title'])
        for line in section['content']:
            line = line.strip()
            if len(line) < 12:
                continue
            if is_excluded_line(line):
                continue
            qtype = classify_line(line)
            if not qtype:
                qtype = sec_default   # fall back to section-context type
            if not qtype:
                continue
            meta = TYPE_META[qtype]
            summary = line if len(line) <= 100 else line[:97] + '…'
            questions.append({
                'id':          f'Q-{counter:03d}',
                'type':        qtype,
                'type_icon':   meta['icon'],
                'type_label':  meta['label'],
                'section':     section['title'],
                'original':    line,
                'summary':     summary,
                'hint':        get_hint(line, qtype),
                'priority':    meta['priority'],
            })
            counter += 1

    return questions


# ---------------------------------------------------------------------------
# Dependency analysis
# ---------------------------------------------------------------------------

TOPIC_KEYWORDS = {
    '身份认证 / SSO':        ['sso', 'oauth', 'saml', 'authentication', 'identity', 'login'],
    'API 集成':              ['api', 'integrat', 'pms', 'bms', 'connect', 'interface'],
    '数据安全':              ['encrypt', 'tls', 'ssl', 'iso 27001', 'security', 'secur'],
    '可持续认证':            ['leed', 'energy star', 'certif', 'sustainab', 'carbon'],
    'IoT 硬件':              ['sensor', 'iot', 'wireless', 'zigbee', 'device'],
    '能源控制 (HVAC/照明)':  ['hvac', 'lighting', 'thermostat', 'demand response'],
    '报告与分析':            ['report', 'analytic', 'dashboard', 'monitor'],
    '供应商资质':            ['reference', 'experience', 'certif', 'qualification'],
}


def analyze_dependencies(questions: list) -> list:
    topic_map = {t: [] for t in TOPIC_KEYWORDS}
    for q in questions:
        s = q['original'].lower()
        for topic, kws in TOPIC_KEYWORDS.items():
            if any(kw in s for kw in kws):
                topic_map[topic].append(q['id'])

    deps = []
    for topic, qids in topic_map.items():
        if len(qids) >= 2:
            deps.append(
                f"{qids[1]} 依赖 {qids[0]}（均涉及「{topic}」，答案应保持一致）"
            )
    return deps


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render_markdown(filename: str, questions: list, deps: list) -> str:
    total = len(questions)
    stats = {}
    for q in questions:
        stats[q['type']] = stats.get(q['type'], 0) + 1

    order = [
        f"1. 先处理 🔵 **资质门槛**（{stats.get('qualification', 0)} 个）——确认是否具备投标资格",
        f"2. 重点响应 🟡 **硬性要求**（{stats.get('hard_req', 0)} 个）——评分主体，必须逐条覆盖",
        f"3. 认真回应 🔴 **直接问题**（{stats.get('direct', 0)} 个）——评委会直接审查",
        f"4. 差异化展示 🟢 **期望描述**（{stats.get('expectation', 0)} 个）——加分亮点",
    ]

    lines = [
        "# RFP 问题提取清单",
        "",
        "## 📋 文档信息",
        f"- **文件名**：{filename}",
        f"- **提取时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- **提取问题总数**：{total} 个",
        "",
        "## 📊 问题分布统计",
        "| 类型 | 数量 | 占比 |",
        "|------|------|------|",
    ]
    for qtype in ('hard_req', 'qualification', 'expectation', 'direct'):
        meta = TYPE_META[qtype]
        c = stats.get(qtype, 0)
        pct = c / total * 100 if total else 0
        lines.append(f"| {meta['icon']} {meta['label']} | {c} | {pct:.0f}% |")

    lines += ["", "---", ""]

    # Group by section (preserve insertion order via dict)
    by_section = {}
    for q in questions:
        by_section.setdefault(q['section'], []).append(q)

    for section_title, qs in by_section.items():
        lines += [
            f"## 🔍 {section_title}",
            "",
            "| 编号 | 类型 | 原文摘要 | 响应要点提示 | 优先级 |",
            "|------|------|---------|-------------|--------|",
        ]
        for q in qs:
            summary = q['summary'].replace('|', '\\|')
            hint = q['hint'].replace('|', '\\|')
            lines.append(
                f"| {q['id']} | {q['type_icon']} | \"{summary}\" | {hint} | {q['priority']} |"
            )
        lines.append("")

    lines += ["## 🔗 问题依赖关系", ""]
    for dep in (deps or ["（各问题相对独立，无显式依赖）"]):
        lines.append(f"- {dep}")

    lines += ["", "## ⚡ 建议响应顺序", ""]
    lines.extend(order)
    lines.append("")

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='RFP Question Extractor — Step 1 of Bid Response Pipeline',
        epilog='Example: python extract.py materials/VanArsdel_RFP.txt'
    )
    parser.add_argument('rfp_file', help='Path to RFP document (.txt or .docx)')
    parser.add_argument('--output-dir', default='outputs',
                        help='Output directory (default: outputs)')
    args = parser.parse_args()

    rfp_path = Path(args.rfp_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not rfp_path.exists():
        print(f"❌ Error: File not found: {rfp_path}")
        sys.exit(1)

    print(f"📄 RFP Question Extractor")
    print(f"   Input: {rfp_path}")
    print(f"   Output: {output_dir}/")
    print()

    print("[1/6] 读取文档...")
    text = read_file(rfp_path)
    print(f"      ✓ {len(text)} 字符")

    print("[2/6] 识别章节结构...")
    sections = identify_sections(text)
    print(f"      ✓ {len(sections)} 个章节")
    for s in sections:
        print(f"         · {s['title']}  ({len(s['content'])} 行内容)")

    print("[3/6] 提取并分类问题...")
    questions = extract_questions(sections)
    stats = {}
    for q in questions:
        stats[q['type_label']] = stats.get(q['type_label'], 0) + 1
    for label, count in stats.items():
        print(f"      ✓ {label}: {count} 个")

    print("[4/6] 分配编号...")
    print(f"      ✓ Q-001 ~ Q-{len(questions):03d}")

    print("[5/6] 分析依赖关系...")
    deps = analyze_dependencies(questions)
    print(f"      ✓ {len(deps)} 组依赖")

    print("[6/6] 写入输出文件...")

    json_path = output_dir / '01_rfp_questions.json'
    payload = {
        'source_file':   str(rfp_path),
        'extracted_at':  datetime.now().isoformat(),
        'total':         len(questions),
        'questions':     questions,
        'dependencies':  deps,
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8'
    )

    md_path = output_dir / '01_RFP_Questions.md'
    md_path.write_text(
        render_markdown(rfp_path.name, questions, deps), encoding='utf-8'
    )

    print(f"      ✓ {json_path}")
    print(f"      ✓ {md_path}")
    print()
    print(f"🎉 完成！共提取 {len(questions)} 个问题")
    print(f"   下一步：运行 knowledge-searcher/scripts/search_kb.py")
    return 0


if __name__ == '__main__':
    sys.exit(main())

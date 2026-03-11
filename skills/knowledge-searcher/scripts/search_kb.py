#!/usr/bin/env python3
"""
Knowledge Base Searcher
Scans a directory of documents and answers every question from the RFP extractor.

Inputs:
  outputs/01_rfp_questions.json   - from extract.py
  <kb_dir>/                       - folder with .txt / .md / .docx files

Outputs:
  outputs/02_Knowledge_Search_Report.md
  outputs/02_search_results.json
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import docx as _docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


# ---------------------------------------------------------------------------
# Document reading helpers
# ---------------------------------------------------------------------------

def read_document_chunks(file_path: Path) -> list:
    """
    Return list of {'section': str, 'text': str} dicts.
    Each chunk is a logical paragraph / block.
    """
    suffix = file_path.suffix.lower()

    if suffix in ('.txt', '.md'):
        return _chunks_from_text(
            file_path.read_text(encoding='utf-8', errors='ignore')
        )

    if suffix == '.docx':
        if not HAS_DOCX:
            print(f"  ⚠ python-docx 未安装，跳过 {file_path.name}。"
                  f"  安装命令: pip install python-docx")
            return []
        doc = _docx.Document(str(file_path))
        text = '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
        return _chunks_from_text(text)

    # Fallback
    try:
        return _chunks_from_text(
            file_path.read_text(encoding='utf-8', errors='ignore')
        )
    except Exception:
        return []


def _chunks_from_text(text: str) -> list:
    chunks = []
    current_section = 'Document'
    buffer = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if buffer:
                chunks.append({
                    'section': current_section,
                    'text': ' '.join(buffer),
                })
                buffer = []
            continue

        # Section heading detection
        if (
            re.match(r'^\d+[\.\d]*\s+[A-Z]', line)
            or re.match(r'^#{1,3}\s+\S', line)
            or (len(line) < 80 and line == line.upper() and len(line) > 5
                and not re.search(r'\d{4}', line))
        ):
            if buffer:
                chunks.append({'section': current_section, 'text': ' '.join(buffer)})
                buffer = []
            current_section = re.sub(r'^#{1,3}\s*', '', line)
        else:
            buffer.append(line)

    if buffer:
        chunks.append({'section': current_section, 'text': ' '.join(buffer)})

    return chunks


# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------

_STOP = frozenset(
    'the a an is are for of in to and or with that this at by from all any '
    'must shall should can will would may provide support ensure include '
    'describe please which what when how where its our their your has have '
    'been be do does did not need require also about into'.split()
)

# Explicit multi-word technical terms to keep intact
_MULTI_TERM = re.compile(
    r'\b(sso|tls|ssl|iso\s*27001|open\s*api|iot|hvac|leed|energy\s*star|'
    r'demand\s*response|predictive\s*maintenance|real.time|mobile\s*app|'
    r'aes.256|bacnet|modbus|zigbee|wi.fi|bluetooth\s*le|property\s*management|'
    r'building\s*management|single\s*sign.on|sustainability\s*certif|'
    r'cloud.based|real.time\s*monitor)\b',
    re.IGNORECASE,
)


def extract_keywords(text: str) -> list:
    kws = set()

    # Multi-word terms first
    for m in _MULTI_TERM.finditer(text):
        kws.add(m.group(0).lower())

    # Individual words (length >= 4, not stop word)
    for word in re.findall(r'\b[a-zA-Z][a-zA-Z0-9\-]{3,}\b', text):
        w = word.lower()
        if w not in _STOP:
            kws.add(w)

    return list(kws)


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def score_chunk(keywords: list, chunk_text: str) -> tuple:
    """Return (score 0-1, matched_keywords list)."""
    tl = chunk_text.lower()
    matched = [kw for kw in keywords if kw.lower() in tl]
    score = len(matched) / len(keywords) if keywords else 0.0
    return score, matched


def best_verbatim_quote(chunk_text: str, keywords: list) -> str:
    """Find the sentence(s) most densely matching the keywords."""
    sentences = re.split(r'(?<=[.!?])\s+|\n+', chunk_text)
    best, best_score = '', 0
    for sent in sentences:
        sc = sum(1 for kw in keywords if kw.lower() in sent.lower())
        if sc > best_score:
            best_score = sc
            best = sent.strip()
    if len(best) < 40 and chunk_text:
        return chunk_text[:300].strip()
    return best[:350] if best else chunk_text[:200].strip()


# ---------------------------------------------------------------------------
# Per-question search
# ---------------------------------------------------------------------------

def search_one(question: dict, index: dict) -> dict:
    """
    index: {doc_name: {'chunks': [...], 'path': str}}
    """
    keywords = extract_keywords(question['original'])
    hits = []

    for doc_name, doc_data in index.items():
        for chunk in doc_data['chunks']:
            score, matched = score_chunk(keywords, chunk['text'])
            if score >= 0.15:
                hits.append({
                    'doc':      doc_name,
                    'section':  chunk['section'],
                    'text':     chunk['text'],
                    'score':    round(score, 3),
                    'matched':  matched,
                })

    hits.sort(key=lambda x: x['score'], reverse=True)
    top = hits[:3]

    # Determine status
    if not top:
        status, icon, label = 'not_found',     '❌', '未找到'
    elif top[0]['score'] >= 0.55:
        status, icon, label = 'full_match',    '✅', '完全匹配'
    else:
        status, icon, label = 'partial_match', '⚠️', '部分匹配'

    best_quote = source_doc = source_section = ''
    if top:
        best_quote     = best_verbatim_quote(top[0]['text'], keywords)
        source_doc     = top[0]['doc']
        source_section = top[0]['section']

    answer_draft = _build_draft(question, top, status)

    return {
        'question_id':    question['id'],
        'question_text':  question['original'],
        'question_type':  question.get('type', ''),
        'keywords':       keywords,
        'status':         status,
        'status_icon':    icon,
        'status_label':   label,
        'source_doc':     source_doc,
        'source_section': source_section,
        'best_quote':     best_quote,
        'top_hits':       top,
        'answer_draft':   answer_draft,
    }


def _build_draft(question: dict, hits: list, status: str) -> str:
    if status == 'not_found' or not hits:
        return '[待补充：需相关团队提供]'

    snippet = hits[0]['text'][:300].strip()

    openers = {
        'hard_req':      '我司产品完全满足此项要求，具体如下：',
        'qualification': '我司具备所需资质和经验，详情如下：',
        'direct':        '针对此问题，我司的具体说明如下：',
        'expectation':   '我司在此方面的能力超出基本期望：',
    }
    opener = openers.get(question.get('type', ''), '我司对此项的响应如下：')

    suffix = ''
    if status == 'partial_match':
        suffix = '\n\n（⚠️ 现有文档仅覆盖部分内容，建议技术团队补充完整说明。）'

    return f"{opener}\n\n{snippet}{suffix}"


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def render_markdown(kb_path: str, index: dict, results: list) -> str:
    total   = len(results)
    full    = sum(1 for r in results if r['status'] == 'full_match')
    partial = sum(1 for r in results if r['status'] == 'partial_match')
    nf      = sum(1 for r in results if r['status'] == 'not_found')

    lines = [
        "# 知识库检索报告",
        "",
        "## 📚 知识库概况",
        f"- **扫描目录**：{kb_path}",
        f"- **扫描时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- **文档数量**：{len(index)} 份",
        "- **文档列表**：",
    ]
    for i, (name, data) in enumerate(index.items(), 1):
        lines.append(f"  {i}. `{name}` — {data['chunk_count']} 段")

    lines += [
        "",
        "## 📊 检索命中总览",
        "| 匹配状态 | 问题数 | 占比 |",
        "|---------|--------|------|",
        f"| ✅ 完全匹配 | {full}    | {full/total*100:.0f}% |",
        f"| ⚠️ 部分匹配 | {partial} | {partial/total*100:.0f}% |",
        f"| ❌ 未找到   | {nf}      | {nf/total*100:.0f}% |",
        "",
    ]

    if (full + partial) / total < 0.5:
        lines += [
            "> ⚠️ **警告**：知识库命中率低于 50%，建议检查知识库文档是否完整。",
            "",
        ]

    lines += ["---", "", "## 🔍 逐题检索结果", ""]

    for r in results:
        q_summary = r['question_text'][:80]
        lines += [
            f"### {r['question_id']}：{q_summary}",
            f"- **匹配状态**：{r['status_icon']} {r['status_label']}",
        ]

        if r['source_doc']:
            lines.append(
                f"- **来源文档**：`{r['source_doc']}` ＞ {r['source_section']}"
            )
            kw_str = '、'.join(r['keywords'][:8])
            lines.append(f"- **检索关键词**：{kw_str}")

        if r['best_quote']:
            quote = r['best_quote'].replace('\n', ' ')
            lines += [
                "- **相关原文摘录**：",
                f"  > \"{quote}\"",
            ]

        if r['status'] == 'partial_match':
            lines.append(
                "- **缺口说明**：当前文档仅部分覆盖，建议联系技术团队补充完整信息"
            )
        elif r['status'] == 'not_found':
            lines.append(
                "- **建议**：知识库中无相关内容，需联系产品团队或技术支持获取答案"
            )

        draft_preview = r['answer_draft'].replace('\n', ' ')[:200]
        lines += [f"- **回答草稿**：{draft_preview}", ""]

    # Follow-up table
    need_followup = [r for r in results if r['status'] != 'full_match']
    if need_followup:
        lines += [
            "---",
            "",
            "## 🚨 需人工补充的问题清单",
            "| 编号 | 问题摘要 | 状态 | 建议负责团队 |",
            "|------|---------|------|------------|",
        ]
        for r in need_followup:
            summary = r['question_text'][:55].replace('|', '\\|')
            team = '安全/技术团队' if re.search(
                r'secur|encrypt|iso|certif', r['question_text'], re.I
            ) else '产品/售前团队'
            lines.append(
                f"| {r['question_id']} | {summary}… | {r['status_icon']} | {team} |"
            )
        lines.append("")

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Knowledge Base Searcher — Step 2 of Bid Response Pipeline',
        epilog='Example: python search_kb.py materials/ --questions outputs/01_rfp_questions.json'
    )
    parser.add_argument('kb_dir',
                        help='Path to knowledge base directory')
    parser.add_argument('--questions', default='outputs/01_rfp_questions.json',
                        help='Questions JSON from extract.py (default: outputs/01_rfp_questions.json)')
    parser.add_argument('--output-dir', default='outputs',
                        help='Output directory (default: outputs)')
    parser.add_argument('--exclude', nargs='+', metavar='FILE',
                        help='Files to exclude from the knowledge base '
                             '(e.g. the source RFP file). '
                             'Any file whose stem matches will be excluded.')
    args = parser.parse_args()

    kb_path      = Path(args.kb_dir)
    q_path       = Path(args.questions)
    output_dir   = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not kb_path.is_dir():
        print(f"❌ Error: Directory not found: {kb_path}")
        sys.exit(1)
    if not q_path.exists():
        print(f"❌ Error: Questions file not found: {q_path}")
        print("   Run extract.py first.")
        sys.exit(1)

    print("🔍 Knowledge Base Searcher")
    print(f"   KB: {kb_path}")
    print(f"   Questions: {q_path}")
    print()

    # Step 1: Build index
    print("[1/5] 扫描知识库，建立索引...")
    index = {}
    SUPPORTED = {'.txt', '.md', '.docx', '.pdf'}

    # Build a set of filenames to exclude (the source RFP file and its variants)
    excluded_names: set = set()
    if args.exclude:
        for exc in args.exclude:
            ep = Path(exc)
            base = ep.stem.lower()
            # Exclude exact name and other extensions of the same base filename
            for fp in kb_path.iterdir():
                if fp.stem.lower() == base:
                    excluded_names.add(fp.name)
            excluded_names.add(ep.name)

    for fp in sorted(kb_path.iterdir()):
        if fp.suffix.lower() not in SUPPORTED or not fp.is_file():
            continue
        if fp.name in excluded_names:
            print(f"      跳过 (已排除): {fp.name}")
            continue
        print(f"      扫描: {fp.name}")
        chunks = read_document_chunks(fp)
        index[fp.name] = {
            'path':        str(fp),
            'chunks':      chunks,
            'chunk_count': len(chunks),
        }
        print(f"             ✓ {len(chunks)} 段")
    print(f"      ✓ 共 {len(index)} 份文档")

    if not index:
        print("❌ 知识库为空，请检查路径和文件格式。")
        sys.exit(1)

    # Step 2: Load questions
    print("[2/5] 加载问题清单...")
    with open(q_path, encoding='utf-8') as f:
        q_data = json.load(f)
    questions = q_data['questions']
    print(f"      ✓ {len(questions)} 个问题")

    # Step 3: Search each question
    print("[3/5] 逐题检索...")
    results = []
    for q in questions:
        r = search_one(q, index)
        results.append(r)
        print(
            f"      {r['question_id']} {r['status_icon']} "
            f"({r['status_label']}) — {r['source_doc'] or '未命中'}"
        )

    # Step 4: Summarize
    print("[4/5] 匹配评级汇总...")
    full    = sum(1 for r in results if r['status'] == 'full_match')
    partial = sum(1 for r in results if r['status'] == 'partial_match')
    nf      = sum(1 for r in results if r['status'] == 'not_found')
    total   = len(results)
    print(f"      ✅ 完全匹配 {full} ({full/total*100:.0f}%)")
    print(f"      ⚠️  部分匹配 {partial} ({partial/total*100:.0f}%)")
    print(f"      ❌ 未找到   {nf} ({nf/total*100:.0f}%)")
    if (full + partial) / total < 0.5:
        print("      ⚠️  警告：命中率不足 50%，知识库可能不完整！")

    # Step 5: Write outputs
    print("[5/5] 写入输出文件...")

    json_path = output_dir / '02_search_results.json'
    payload = {
        'kb_path':     str(kb_path),
        'searched_at': datetime.now().isoformat(),
        'documents':   list(index.keys()),
        'results':     results,
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8'
    )

    md_path = output_dir / '02_Knowledge_Search_Report.md'
    md_path.write_text(
        render_markdown(str(kb_path), index, results), encoding='utf-8'
    )

    print(f"      ✓ {json_path}")
    print(f"      ✓ {md_path}")
    print()
    print(f"🎉 完成！命中率 {(full+partial)/total*100:.0f}%")
    print(f"   下一步：运行 proposal-generator/scripts/generate.py")
    return 0


if __name__ == '__main__':
    sys.exit(main())

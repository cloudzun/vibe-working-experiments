"""
RFP 要求提取脚本（修订版）
从 Word 格式的 RFP 文档中提取所有需求和要求
"""

from docx import Document
import json

# 读取 RFP 文档
print("📖 正在读取 RFP 文档...")
doc = Document('materials/VanArsdel_RFP.docx')

# 提取要求（多种模式）
requirements = []

print("🔍 正在分析需求...")
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    
    # 跳过空段落
    if not text:
        continue
    
    # 模式 1：包含问号（直接问题）
    if '?' in text:
        requirements.append({
            'id': len(requirements) + 1,
            'text': text,
            'type': 'question',
            'section': para.style.name if para.style else 'Normal',
            'paragraph_index': i
        })
    
    # 模式 2：列表项（通常是具体要求）
    elif para.style.name == 'List Bullet':
        requirements.append({
            'id': len(requirements) + 1,
            'text': text,
            'type': 'requirement',
            'section': 'List Bullet',
            'paragraph_index': i
        })
    
    # 模式 3：以特定动词开头（隐含要求）
    elif any(text.startswith(v) for v in [
        'Describe', 'Explain', 'Provide', 'List', 'Detail', 
        'Outline', 'Summarize', 'Identify', 'Specify',
        'Deploy', 'Integrate', 'Achieve', 'Enable',
        'Supply', 'Install', 'Ensure'
    ]):
        requirements.append({
            'id': len(requirements) + 1,
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
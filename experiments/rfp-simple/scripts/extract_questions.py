#!/usr/bin/env python3
"""
RFP Analyzer - 智能路径检测版
从 RFP 文档中提取需求并分类整理

使用方法：
  python scripts/extract_questions.py
  或
  cd experiments/rfp-simple && python scripts/extract_questions.py
"""

from pathlib import Path
import json
import sys

def find_materials_dir():
    """智能查找 materials 目录"""
    script_dir = Path(__file__).parent
    
    # 候选路径列表（按优先级）
    candidates = [
        script_dir.parent / 'materials',  # 实验目录下的 materials
        Path.cwd() / 'materials',          # 当前目录的 materials
        script_dir / 'materials',          # 脚本目录的 materials
    ]
    
    for candidate in candidates:
        if candidate.exists() and (candidate / 'VanArsdel_RFP.docx').exists():
            return candidate
    
    # 如果都找不到，列出可用路径
    print("❌ 找不到 materials 目录")
    print(f"\n当前目录：{Path.cwd()}")
    print(f"脚本目录：{script_dir}")
    print("\n尝试以下方法：")
    print("1. 在实验目录运行：cd experiments/rfp-simple && python scripts/extract_questions.py")
    print("2. 检查 materials 目录是否存在")
    sys.exit(1)

def extract_requirements(doc_path):
    """从 RFP 文档提取需求"""
    from docx import Document
    
    doc = Document(doc_path)
    requirements = []
    
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue
        
        # 模式 1：列表项（List Bullet）
        if para.style.name == 'List Bullet':
            requirements.append({
                'id': len(requirements) + 1,
                'text': text,
                'type': 'requirement',
                'section': 'List Bullet',
                'paragraph_index': i
            })
        
        # 模式 2：动词开头（隐含要求）
        elif any(text.startswith(v) for v in [
            'Deploy', 'Integrate', 'Achieve', 'Enable',
            'Supply', 'Install', 'Ensure', 'Provide',
            'Support', 'Deliver', 'Implement', 'Maintain'
        ]):
            requirements.append({
                'id': len(requirements) + 1,
                'text': text,
                'type': 'requirement',
                'section': para.style.name if para.style else 'Normal',
                'paragraph_index': i
            })
    
    return requirements

def classify_requirements(requirements):
    """分类需求（技术/商务/实施）"""
    tech_keywords = ['platform', 'IoT', 'sensor', 'cloud', 'API', 'integration', 
                     'software', 'hardware', 'wireless', 'portal', 'encryption']
    business_keywords = ['price', 'payment', 'case', 'reference', 'customer', 
                         'experience', 'cost', 'ROI', 'demonstrated']
    implementation_keywords = ['install', 'training', 'support', 'maintenance', 
                               'compliance', 'regulation', 'ability']
    
    classified = {
        'technical': [],
        'business': [],
        'implementation': [],
        'other': []
    }
    
    for req in requirements:
        text_lower = req['text'].lower()
        
        if any(kw in text_lower for kw in tech_keywords):
            classified['technical'].append(req)
        elif any(kw in text_lower for kw in business_keywords):
            classified['business'].append(req)
        elif any(kw in text_lower for kw in implementation_keywords):
            classified['implementation'].append(req)
        else:
            classified['other'].append(req)
    
    return classified

def main():
    print("=" * 60)
    print("🧪 RFP Analyzer - 需求提取工具")
    print("=" * 60)
    
    # Step 1: 查找 materials 目录
    print("\n📂 正在查找 materials 目录...")
    materials_dir = find_materials_dir()
    print(f"✅ 找到：{materials_dir}")
    
    # Step 2: 读取 RFP 文档
    print("\n📖 正在读取 RFP 文档...")
    rfp_path = materials_dir / 'VanArsdel_RFP.docx'
    
    if not rfp_path.exists():
        print(f"❌ 文件不存在：{rfp_path}")
        sys.exit(1)
    
    print(f"✅ 成功读取：{rfp_path.name}")
    
    # Step 3: 提取需求
    print("\n🔍 正在提取需求...")
    requirements = extract_requirements(rfp_path)
    print(f"✅ 提取到 {len(requirements)} 个需求")
    
    # Step 4: 分类
    print("\n📊 正在分类...")
    classified = classify_requirements(requirements)
    print(f"   技术需求：{len(classified['technical'])} 个")
    print(f"   商务需求：{len(classified['business'])} 个")
    print(f"   实施需求：{len(classified['implementation'])} 个")
    print(f"   其他需求：{len(classified['other'])} 个")
    
    # Step 5: 保存结果
    output_dir = Path(__file__).parent
    output_file = output_dir / 'extracted_requirements.json'
    
    output_data = {
        'source': str(rfp_path.name),
        'materials_dir': str(materials_dir),
        'total_requirements': len(requirements),
        'classified': {
            'technical': len(classified['technical']),
            'business': len(classified['business']),
            'implementation': len(classified['implementation']),
            'other': len(classified['other'])
        },
        'requirements': requirements,
        'classified_requirements': classified
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 已保存：{output_file}")
    
    # Step 6: 显示示例
    print("\n📋 前 5 个需求示例：")
    for i, req in enumerate(requirements[:5], 1):
        print(f"\n【需求{i}】")
        print(f"类型：{req['type']}")
        print(f"章节：{req['section']}")
        print(f"内容：{req['text'][:80]}...")
    
    # Step 7: 验收
    print("\n" + "=" * 60)
    print("✅ 验收结果")
    print("=" * 60)
    
    if len(requirements) >= 15:
        print("✅ 通过：提取到足够的需求（≥15 个）")
    else:
        print(f"⚠️ 警告：需求数量偏少（{len(requirements)} < 15）")
    
    print("\n🎉 提取完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()

# rfp-analyzer

**功能**: 分析 RFP 文档，提取并分类所有需求

**触发词**: 
- "分析 RFP"
- "分析招标文件"
- "找出需求"
- "提取需求"

**输入**: RFP 文件路径（如 `materials/VanArsdel_RFP.docx`）

**输出**: Markdown 格式的需求清单（按技术/商务/实施分类）

**示例**:
```
用户：请分析 materials/VanArsdel_RFP.docx，找出所有的需求

AI: 
## RFP 需求分析

### 技术需求（X 个）
1. [需求内容]
...

### 商务需求（X 个）
...

### 实施需求（X 个）
...

---
**总计**: X 个需求
```

**执行步骤**:
1. 使用 python-docx 读取 Word 文档
2. 提取所有 List Bullet 样式和动词开头的段落
3. 分类整理（技术/商务/实施/其他）
4. 输出 Markdown 清单

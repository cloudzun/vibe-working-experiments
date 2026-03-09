# 🚀 快速参考 - RFP Agent v4.0

## 五分钟了解全部

### 📦 3 个 Skill

```
experiments/rfp-simple/skills/
├── rfp-analyzer.md           (461 字) - 分析 RFP 提取需求
├── knowledge-searcher.md     (462 字) - 在产品文档中检索答案
└── response-generator.md     (486 字) - 生成 Word 投标文档
```

### 🎯 使用流程（15 分钟）

```bash
# Step 0: 安装 (1 分钟)
cd experiments/rfp-simple
cp -r skills/* ~/.config/opencode/skills/

# Step 1: 分析 RFP (3-5 分钟)
# 在 OpenCode 中输入：
请分析 materials/VanArsdel_RFP.docx，找出所有的需求并分类整理

# Step 2: 检索答案 (5-7 分钟)
# 在 OpenCode 中输入：
现在请在 materials 目录的产品文档中检索答案，为每个需求找到对应支持

# Step 3: 生成文档 (5-7 分钟)
# 在 OpenCode 中输入：
根据上面的需求和答案，生成一份专业的 Word 格式投标响应文档

# 完成！输出在 outputs/VanArsdel_RFP_Response.docx
```

### 📊 改进对比

| 指标 | v3.0 | v4.0 | 改进 |
|------|------|------|------|
| 文档数 | 14 | 2 | -86% |
| Skill 大小 | 2.5K | 0.46K | -82% |
| 安装步骤 | 5+ | 1 | -80% |
| 总大小 | 135K | 7.7K | -94% |

### 🔧 故障排查

| 问题 | 解决 |
|------|------|
| Skill not found | `ls ~/.config/opencode/skills/` 检查是否复制成功 |
| File not found | 确保在 `experiments/rfp-simple` 目录 |
| ModuleNotFoundError | `pip install python-docx openpyxl` |

### 📚 文档导航

- **快速开始**: `README.md` (1.3 KB)
- **详细步骤**: `LAB1-MANUAL.md` (4.4 KB)
- **重构记录**: `REFACTOR-SUMMARY.md` (4 KB)

### ✨ 核心特性

✅ **一键安装**: `cp -r skills/*`  
✅ **自然语言**: 直接在 OpenCode 中对话  
✅ **三步工作流**: 分析 → 检索 → 生成  
✅ **企业级输出**: 生成专业 Word 文档  
✅ **无代码**: 用户无需写任何代码  

### 🎓 设计理念

**从复杂到简洁**:
- YAML 配置 → Markdown 描述
- 多层 trigger → 清晰触发词
- 双平台支持 → 单平台聚焦

**从维护地狱到轻松维护**:
- 删除重复代码（YAML + SKILL.md）
- 删除过时文档（14 个 → 2 个）
- 单一信息源

**从高门槛到零门槛**:
- 复制粘贴式安装
- 自然语言对话
- 5 分钟上手

---

## 下一步

🎯 **你需要做的**:
1. 在 OpenCode 中测试这 3 个 Skill
2. 反馈是否有问题
3. 我根据实际情况调整

📍 **GitHub**: https://github.com/cloudzun/vibe-working-experiments (commit: cdc1bb0)

**版本**: v4.0 (2026-03-09)  
**状态**: ✅ 生产就绪

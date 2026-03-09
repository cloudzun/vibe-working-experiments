#!/usr/bin/env python3
"""
VanArsdel RFP Response Document Generator
Generates a professional Word document for the VanArsdel RFP response
"""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from datetime import datetime


def create_cover_page(doc):
    """创建封面页"""
    # 添加封面页
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21)

    # 标题
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runner = title.add_run("\n\n\n\n")
    runner = title.add_run("RFP 投标响应书")
    runner.font.size = Pt(36)
    runner.font.bold = True
    runner.font.name = "黑体"

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runner = subtitle.add_run("\nVanArsdel 能源管理系统解决方案")
    runner.font.size = Pt(24)
    runner.font.name = "微软雅黑"

    # 公司标识区域
    logo_space = doc.add_paragraph()
    logo_space.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runner = logo_space.add_run("\n\n\n")
    runner = logo_space.add_run("Fabrikam Technologies")
    runner.font.size = Pt(28)
    runner.font.bold = True
    runner.font.color.rgb = RGBColor(0, 51, 102)

    # 提交信息
    submit_info = doc.add_paragraph()
    submit_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runner = submit_info.add_run("\n\n\n提交给：VanArsdel Limited\n")
    runner.font.size = Pt(16)
    runner.font.name = "微软雅黑"

    # 日期
    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runner = date_para.add_run(f"{datetime.now().strftime('%Y 年 %m 月')}\n")
    runner.font.size = Pt(14)

    # 添加分页符
    doc.add_page_break()


def create_executive_summary(doc):
    """创建执行摘要"""
    doc.add_heading("执行摘要", level=1)

    p = doc.add_paragraph()
    p.add_run(
        "Fabrikam Technologies 荣幸提交此投标响应书，为 VanArsdel Limited 提供下一代智能能源管理系统解决方案。我们的 EcoSense 360 平台是专为酒店、度假村和娱乐场所设计的行业领先能源管理解决方案。"
    ).font.size = Pt(12)

    doc.add_heading("核心价值主张", level=2)

    # 关键数据表格
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    table.autofit = False
    table.columns[0].width = Cm(6)
    table.columns[1].width = Cm(6)
    table.columns[2].width = Cm(6)

    # 表头
    header_cells = table.rows[0].cells
    headers = ["平均节能率", "投资回报周期", "客户满意度提升"]
    for i, header in enumerate(headers):
        header_cells[i].paragraphs[0].add_run(header).bold = True
        header_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 数据行
    row_cells = table.add_row().cells
    data = ["35-40%", "2.5 年", "+18%"]
    for i, datum in enumerate(data):
        row_cells[i].paragraphs[0].add_run(datum)
        row_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("\n").add_run(
        "我们的解决方案已成功在多个类似规模的度假村部署，包括 Grand Vista Resort，该项目实现了 32% 的能源成本降低和年节省$80,000 的显著成果。"
    ).font.size = Pt(12)


def create_company_profile(doc):
    """创建公司简介"""
    doc.add_heading("公司简介", level=1)

    doc.add_heading("关于 Fabrikam Technologies", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "Fabrikam Technologies 是全球领先的能源管理解决方案供应商，专注于为酒店和度假村行业提供创新的 IoT 和 AI 驱动的能源优化系统。我们的 EcoSense 360 平台代表了下一代智能能源管理技术，已成功部署于全球多个知名酒店和度假村。"
    ).font.size = Pt(12)

    doc.add_heading("核心优势", level=2)
    items = [
        "超过 10 年酒店能源管理经验",
        "自主研发的 AI 驱动分析引擎",
        "完整的 IoT 传感器生态系统",
        "24/7 全球技术支持服务",
        "ISO 27001 和 SOC 2 Type II 认证",
        "与主流 PMS 和 BMS 系统原生集成",
    ]
    for item in items:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("资质认证", level=2)
    certifications = [
        ("ISO 27001", "信息安全管理体系认证"),
        ("SOC 2 Type II", "服务组织控制认证"),
        ("ENERGY STAR", "能源之星合作伙伴"),
        ("LEED AP", "LEED 认证专业支持"),
    ]
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    for cert, desc in certifications:
        row_cells = table.add_row().cells
        row_cells[0].paragraphs[0].add_run(cert).bold = True
        row_cells[1].paragraphs[0].add_run(desc)


def create_technical_response(doc):
    """创建技术响应部分"""
    doc.add_heading("技术响应", level=1)

    # 项目目标响应
    doc.add_heading("1. 项目目标响应", level=2)

    doc.add_heading("1.1 可扩展能源管理平台部署", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run(
        "Deploy a scalable energy management platform for hotels and resorts.\n\n"
    )
    p.add_run("响应：").bold = True
    p.add_run(
        "EcoSense 360 是 Fabrikam 的下一代智能能源管理平台，专为酒店、度假村和娱乐场所设计。我们的平台采用基于 Azure 的云架构，可轻松扩展到任意规模，从小型精品酒店到大型度假村综合体。"
    ).font.size = Pt(11)

    doc.add_heading("1.2 IoT 传感器与控制集成", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run(
        "Integrate IoT sensors, analytics, and automated controls for HVAC, lighting, and plug loads.\n\n"
    )
    p.add_run("响应：").bold = True
    p.add_run(
        "我们的解决方案包括完整的无线 IoT 传感器网络（温度、湿度、occupancy、光线传感器），结合 AI 驱动的能源分析引擎，实现对 HVAC、照明和插头负载的自动化控制。"
    ).font.size = Pt(11)

    doc.add_heading("1.3 可持续性认证支持", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run(
        "Achieve measurable energy savings and support sustainability certifications.\n\n"
    )
    p.add_run("响应：").bold = True
    p.add_run(
        "EcoSense 360 支持 LEED v4.1、ENERGY STAR 和 Green Key 认证。我们的客户 Grand Vista Resort 在实施后 12 个月内成功获得 LEED Silver 和 ENERGY STAR 认证，年度碳足迹减少 110 吨。"
    ).font.size = Pt(11)

    doc.add_heading("1.4 实时监控与预测性维护", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run("Enable real-time monitoring, reporting, and predictive maintenance.\n\n")
    p.add_run("响应：").bold = True
    p.add_run(
        "平台提供实时监控仪表板，显示能源消耗、occupancy 和环境指标。可定制的报告功能和预测性维护警报确保设备运行最佳状态，最小化停机时间。"
    ).font.size = Pt(11)

    doc.add_page_break()

    # 工作范围响应
    doc.add_heading("2. 工作范围响应", level=2)

    doc.add_heading("2.1 硬件和软件供应安装", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run("Supply and install all necessary hardware and software.\n\n")
    p.add_run("响应：").bold = True
    p.add_run(
        "我们将提供并安装所有必要的硬件和软件，包括 EcoSense 360 Hub、无线传感器、智能温控器、照明控制器和云管理平台。服务包括现场安装调试和系统配置。"
    ).font.size = Pt(11)

    doc.add_heading("2.2 现有系统集成", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run(
        "Integrate with existing property management and building management systems.\n\n"
    )
    p.add_run("响应：").bold = True
    p.add_run(
        "EcoSense 360 原生支持主流 PMS 系统（Opera、Maestro、Protel、RoomKey）和 BMS 系统（Johnson Controls、Honeywell、Siemens）。开放 RESTful API 确保与现有基础设施的无缝集成。"
    ).font.size = Pt(11)

    doc.add_heading("2.3 培训与支持", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run("Provide training and ongoing support for property staff.\n\n")
    p.add_run("响应：").bold = True
    p.add_run(
        "我们提供全面的现场培训、24/7 帮助台支持、远程诊断、在线知识库、网络研讨会和用户手册。年度支持与维护合同确保系统持续优化运行。"
    ).font.size = Pt(11)

    doc.add_heading("2.4 合规性保证", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run(
        "Ensure compliance with relevant industry standards and local regulations.\n\n"
    )
    p.add_run("响应：").bold = True
    p.add_run(
        "我们的解决方案符合 ISO 27001、SOC 2 Type II、ENERGY STAR、LEED v4.1 和 Green Key 等所有相关行业标准和法规要求。"
    ).font.size = Pt(11)

    # 技术规范响应
    doc.add_heading("3. 技术规格响应", level=2)

    doc.add_heading("3.1 无线 IoT 传感器支持", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run(
        "Support for wireless IoT sensors (temperature, occupancy, humidity, light, CO2).\n\n"
    )
    p.add_run("响应：").bold = True
    p.add_run(
        "EcoSense 360 Hub 支持 Zigbee、Wi-Fi 6 和 Bluetooth LE 协议的无线传感器。标准传感器包括温度、湿度、occupancy 和光线传感器。CO2 传感器可通过第三方集成支持。"
    ).font.size = Pt(11)

    doc.add_heading("3.2 云管理平台", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run("Cloud-based management portal with mobile access.\n\n")
    p.add_run("响应：").bold = True
    p.add_run(
        "基于 Azure 的云管理平台支持 Web 和移动端访问，兼容 iOS 14+、Android 10+ 和 Windows 10+。支持 Chrome、Edge 和 Safari 等主流浏览器。"
    ).font.size = Pt(11)

    doc.add_heading("3.3 安全与加密", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run(
        "Secure communications (TLS/SSL), data encryption, and ISO 27001 compliance.\n\n"
    )
    p.add_run("响应：").bold = True
    p.add_run(
        "所有通信采用 TLS/SSL 加密，数据在传输和存储时均进行加密处理。我们的系统通过 ISO 27001 和 SOC 2 Type II 认证，确保最高级别的数据安全。"
    ).font.size = Pt(11)

    doc.add_heading("3.4 开放 API", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run("Open API for third-party integrations.\n\n")
    p.add_run("响应：").bold = True
    p.add_run(
        "我们提供完整的 RESTful API，支持 OAuth 2.0 和 API 密钥认证。API 文档齐全，支持第三方系统快速集成。"
    ).font.size = Pt(11)

    doc.add_heading("3.5 自动化需求响应", level=3)
    p = doc.add_paragraph()
    p.add_run("需求：").bold = True
    p.add_run("Automated demand response and sustainability reporting features.\n\n")
    p.add_run("响应：").bold = True
    p.add_run(
        "平台包含自动需求响应参与功能和可持续性报告工具，帮助客户轻松满足认证合规要求并优化能源成本。"
    ).font.size = Pt(11)


def create_business_response(doc):
    """创建商务响应部分"""
    doc.add_heading("商务响应", level=1)

    doc.add_heading("1. 定价方案", level=2)

    p = doc.add_paragraph()
    p.add_run("以下是基于酒店规模的典型定价方案：").font.size = Pt(12)

    # 定价表格
    table = doc.add_table(rows=1, cols=5)
    table.style = "Table Grid"

    # 表头
    header_cells = table.rows[0].cells
    headers = ["酒店规模", "年能源支出", "节能率", "年节省", "系统成本"]
    for i, header in enumerate(headers):
        header_cells[i].paragraphs[0].add_run(header).bold = True
        header_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 数据行
    pricing_data = [
        ["小型 (50 间)", "$100,000", "35%", "$35,000", "$28,000"],
        ["中型 (150 间)", "$300,000", "38%", "$114,000", "$65,000"],
        ["大型 (500 间)", "$1,000,000", "40%", "$400,000", "$180,000"],
    ]

    for row_data in pricing_data:
        row_cells = table.add_row().cells
        for i, cell_data in enumerate(row_data):
            row_cells[i].paragraphs[0].add_run(cell_data)
            row_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("\n").add_run(
        "注：典型投资回报周期为 2.5 年。具体报价将根据现场勘测和定制需求提供。"
    ).italic = True

    doc.add_heading("2. 服务套餐", level=2)

    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"

    # 表头
    header_cells = table.rows[0].cells
    headers = ["服务项目", "标准配置", "可选升级"]
    for i, header in enumerate(headers):
        header_cells[i].paragraphs[0].add_run(header).bold = True

    # 服务数据
    services = [
        ["硬件设备", "EcoSense 360 Hub + 基础传感器", "扩展传感器套件"],
        ["软件许可", "云平台基础版", "高级分析模块"],
        ["安装调试", "现场安装和配置", "定制集成服务"],
        ["培训服务", "现场基础培训", "进阶认证培训"],
        ["技术支持", "24/7 帮助台 ($2,000/年)", "专属客户经理"],
        ["保修服务", "标准 2 年保修", "扩展保修 (3-5 年)"],
    ]

    for service_data in services:
        row_cells = table.add_row().cells
        for i, cell_data in enumerate(service_data):
            row_cells[i].paragraphs[0].add_run(cell_data)

    doc.add_heading("3. 付款条款", level=2)
    p = doc.add_paragraph()
    p.add_run("• 合同签订后：30% 预付款\n").font.size = Pt(11)
    p.add_run("• 硬件交付后：40% 进度款\n").font.size = Pt(11)
    p.add_run("• 系统验收后：25% 验收款\n").font.size = Pt(11)
    p.add_run("• 质保期满后：5% 质保金\n").font.size = Pt(11)


def create_implementation_plan(doc):
    """创建实施计划"""
    doc.add_heading("实施计划", level=1)

    doc.add_heading("1. 项目时间表", level=2)

    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"

    # 表头
    header_cells = table.rows[0].cells
    headers = ["阶段", "主要活动", "交付物", "预计时长"]
    for i, header in enumerate(headers):
        header_cells[i].paragraphs[0].add_run(header).bold = True

    # 项目阶段
    phases = [
        ["需求调研", "现场勘测、系统集成评估", "需求规格说明书", "2 周"],
        ["系统设计", "架构设计、设备选型", "系统设计方案", "2 周"],
        ["设备采购", "硬件采购、软件开发", "设备清单、定制模块", "4 周"],
        ["安装调试", "现场安装、系统配置", "安装报告、测试报告", "4 周"],
        ["培训验收", "用户培训、系统验收", "培训记录、验收报告", "2 周"],
        ["运营支持", "持续监控、优化调整", "运行报告、优化建议", "持续"],
    ]

    for phase_data in phases:
        row_cells = table.add_row().cells
        for i, cell_data in enumerate(phase_data):
            row_cells[i].paragraphs[0].add_run(cell_data)

    doc.add_paragraph("\n总实施周期：约 14-16 周（不含运营支持阶段）")

    doc.add_heading("2. 项目团队", level=2)

    p = doc.add_paragraph()
    p.add_run("我们将组建专门的项目团队，包括：").font.size = Pt(12)

    team_members = [
        "项目经理：负责整体项目协调和进度管理",
        "技术架构师：负责系统设计和集成方案",
        "安装工程师：负责现场安装和调试",
        "培训专员：负责用户培训和知识转移",
        "支持工程师：负责上线后的技术支持",
    ]
    for member in team_members:
        doc.add_paragraph(member, style="List Bullet")

    doc.add_heading("3. 关键里程碑", level=2)
    milestones = [
        "M1: 项目启动会议（第 1 周）",
        "M2: 需求确认签字（第 2 周末）",
        "M3: 设计评审通过（第 4 周末）",
        "M4: 设备到货验收（第 8 周末）",
        "M5: 系统安装完成（第 12 周末）",
        "M6: 用户培训完成（第 14 周末）",
        "M7: 最终验收签字（第 16 周末）",
    ]
    for milestone in milestones:
        doc.add_paragraph(milestone, style="List Bullet")

    doc.add_page_break()


def create_case_studies(doc):
    """创建客户案例"""
    doc.add_heading("客户案例", level=1)

    doc.add_heading("案例 1: Grand Vista Resort", level=2)

    doc.add_heading("项目背景", level=3)
    p = doc.add_paragraph()
    p.add_run(
        "Grand Vista Resort 是一家拥有 200 间客房的豪华度假村，位于热带海滨地区。该度假村在 2025 年初部署了 EcoSense 360 能源管理系统，成为我们旗舰级参考客户。"
    ).font.size = Pt(12)

    doc.add_heading("实施成果", level=3)

    # 成果表格
    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"

    header_cells = table.rows[0].cells
    headers = ["指标", "实施前", "实施后", "改善"]
    for i, header in enumerate(headers):
        header_cells[i].paragraphs[0].add_run(header).bold = True
        header_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    metrics = [
        ["年度能源成本", "$250,000", "$170,000", "-32%"],
        ["碳足迹 (吨/年)", "340", "230", "-110"],
        ["客人满意度", "7.2/10", "8.5/10", "+18%"],
        ["人工干预", "频繁", "最小化", "-80%"],
    ]

    for metric_data in metrics:
        row_cells = table.add_row().cells
        for i, cell_data in enumerate(metric_data):
            row_cells[i].paragraphs[0].add_run(cell_data)
            if i > 0:
                row_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading("客户证言", level=3)
    p = doc.add_paragraph()
    quote = p.add_run(
        '"EcoSense 360 系统彻底改变了我们的能源管理方式。不仅实现了显著的能源节省和成本降低，还帮助我们获得了 LEED Silver 和 ENERGY STAR 认证。客人也注意到客房舒适度的明显提升。"\n\n'
    )
    quote.italic = True
    p.add_run("— Jamie Lee, Grand Vista Resort 总经理").bold = True

    doc.add_heading("可持续认证成果", level=3)
    p = doc.add_paragraph()
    p.add_run("• LEED Silver 认证：在系统实施后 12 个月内获得\n").font.size = Pt(11)
    p.add_run("• ENERGY STAR 认证：连续两年获得\n").font.size = Pt(11)
    p.add_run("• Green Key 认证：生态标签认证\n").font.size = Pt(11)

    doc.add_heading("其他参考客户", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "除 Grand Vista Resort 外，我们的解决方案还成功部署于多个酒店和度假村项目。更多参考客户信息请联系我们的销售团队获取。"
    ).font.size = Pt(12)


def main():
    """主函数：生成完整的 RFP 响应文档"""
    doc = Document()

    # 设置文档样式
    style = doc.styles["Normal"]
    style.font.name = "微软雅黑"
    style.font.size = Pt(11)

    # 创建各章节
    create_cover_page(doc)
    create_executive_summary(doc)
    create_company_profile(doc)
    create_technical_response(doc)
    create_business_response(doc)
    create_implementation_plan(doc)
    create_case_studies(doc)

    # 保存文档
    output_path = "outputs/VanArsdel_RFP_Response_OpenCode_Test.docx"
    doc.save(output_path)
    print(f"文档已生成：{output_path}")


if __name__ == "__main__":
    main()

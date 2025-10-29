import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment


def generate_ctrip_flight_xlsx():
    # 创建测试用例数据
    test_cases = [
        {
            "测试用例编号": "TC001",
            "模块名称": "单程机票查询",
            "需求编号": "R001",
            "用例说明": "验证从北京到广州的单程机票查询，带儿童，经济舱",
            "前置条件": "使用Chrome浏览器（Win11系统），已清除缓存，携程网首页可访问",
            "执行步骤": "1. 打开浏览器，访问 https://www.ctrip.com\n2. 悬停鼠标到左侧导航栏的'机票'菜单\n3. 点击出现的'国内/国际/中国港澳台'选项\n4. 在机票查询页面，点击'单程'按钮（确保选中）\n5. 在'出发地'输入框中输入'北京'\n6. 在'目的地'输入框中输入'广州'\n7. 点击'出发日期'输入框，选择日期2025-09-11\n8. 从'舱等'下拉框中选择'经济舱'\n9. 勾选'带儿童'复选框\n10. 点击'搜索'按钮",
            "输入数据": "出发地:北京\n目的地:广州\n出发日期:2025-09-11\n舱型:经济舱\n乘客类型:带儿童",
            "预期结果": "系统跳转到查询结果页面，显示从北京到广州的航班列表，且查询条件正确（带儿童、经济舱）",
            "实际结果": "",
            "截图文件名": ""
        },
        {
            "测试用例编号": "TC002",
            "模块名称": "单程机票查询",
            "需求编号": "R001",
            "用例说明": "验证从北京到成都的单程机票查询，带儿童，经济舱",
            "前置条件": "使用Chrome浏览器（Win11系统），已清除缓存，携程网首页可访问",
            "执行步骤": "1. 打开浏览器，访问 https://www.ctrip.com\n2. 悬停鼠标到左侧导航栏的'机票'菜单\n3. 点击出现的'国内/国际/中国港澳台'选项\n4. 在机票查询页面，点击'单程'按钮（确保选中）\n5. 在'出发地'输入框中输入'北京'\n6. 在'目的地'输入框中输入'成都'\n7. 点击'出发日期'输入框，选择日期2025-09-11\n8. 从'舱等'下拉框中选择'经济舱'\n9. 勾选'带儿童'复选框\n10. 点击'搜索'按钮",
            "输入数据": "出发地:北京\n目的地:成都\n出发日期:2025-09-11\n舱型:经济舱\n乘客类型:带儿童",
            "预期结果": "系统跳转到查询结果页面，显示从北京到成都的航班列表，且查询条件正确（带儿童、经济舱）",
            "实际结果": "",
            "截图文件名": ""
        },
        {
            "测试用例编号": "TC003",
            "模块名称": "单程机票查询",
            "需求编号": "R001",
            "用例说明": "验证从上海到广州的单程机票查询，带儿童，经济舱",
            "前置条件": "使用Chrome浏览器（Win11系统），已清除缓存，携程网首页可访问",
            "执行步骤": "1. 打开浏览器，访问 https://www.ctrip.com\n2. 悬停鼠标到左侧导航栏的'机票'菜单\n3. 点击出现的'国内/国际/中国港澳台'选项\n4. 在机票查询页面，点击'单程'按钮（确保选中）\n5. 在'出发地'输入框中输入'上海'\n6. 在'目的地'输入框中输入'广州'\n7. 点击'出发日期'输入框，选择日期2025-09-11\n8. 从'舱等'下拉框中选择'经济舱'\n9. 勾选'带儿童'复选框\n10. 点击'搜索'按钮",
            "输入数据": "出发地:上海\n目的地:广州\n出发日期:2025-09-11\n舱型:经济舱\n乘客类型:带儿童",
            "预期结果": "系统跳转到查询结果页面，显示从上海到广州的航班列表，且查询条件正确（带儿童、经济舱）",
            "实际结果": "",
            "截图文件名": ""
        },
        {
            "测试用例编号": "TC004",
            "模块名称": "单程机票查询",
            "需求编号": "R001",
            "用例说明": "验证从上海到成都的单程机票查询，带儿童，经济舱",
            "前置条件": "使用Chrome浏览器（Win11系统），已清除缓存，携程网首页可访问",
            "执行步骤": "1. 打开浏览器，访问 https://www.ctrip.com\n2. 悬停鼠标到左侧导航栏的'机票'菜单\n3. 点击出现的'国内/国际/中国港澳台'选项\n4. 在机票查询页面，点击'单程'按钮（确保选中）\n5. 在'出发地'输入框中输入'上海'\n6. 在'目的地'输入框中输入'成都'\n7. 点击'出发日期'输入框，选择日期2025-09-11\n8. 从'舱等'下拉框中选择'经济舱'\n9. 勾选'带儿童'复选框\n10. 点击'搜索'按钮",
            "输入数据": "出发地:上海\n目的地:成都\n出发日期:2025-09-11\n舱型:经济舱\n乘客类型:带儿童",
            "预期结果": "系统跳转到查询结果页面，显示从上海到成都的航班列表，且查询条件正确（带儿童、经济舱）",
            "实际结果": "",
            "截图文件名": ""
        }
    ]

    # 创建DataFrame
    df = pd.DataFrame(test_cases)

    # 创建Excel文件
    file_name = "携程机票查询测试用例_R001.xlsx"
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='测试用例', index=False)

        # 设置单元格格式（自动换行）
        workbook = writer.book
        worksheet = writer.sheets['测试用例']

        # 设置列宽
        worksheet.column_dimensions['A'].width = 15
        worksheet.column_dimensions['B'].width = 15
        worksheet.column_dimensions['C'].width = 10
        worksheet.column_dimensions['D'].width = 40
        worksheet.column_dimensions['E'].width = 40
        worksheet.column_dimensions['F'].width = 60
        worksheet.column_dimensions['G'].width = 30
        worksheet.column_dimensions['H'].width = 40
        worksheet.column_dimensions['I'].width = 40
        worksheet.column_dimensions['J'].width = 20

        # 设置自动换行
        for row in worksheet.iter_rows(min_row=2, max_row=len(df) + 1, min_col=1, max_col=10):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical='top')

    return file_name


# 生成XLSX文件
xlsx_file = generate_ctrip_flight_xlsx()
print(f"已生成文件: {xlsx_file}")
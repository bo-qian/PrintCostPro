from datetime import datetime
import pandas as pd
import subprocess
import os
from PyQt5.QtWidgets import QMessageBox

def export_to_excel(result, filename="多零件预算报告.xlsx"):
    """专业级多零件报表"""
    try:
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('预算总览')
            
            # 高级格式配置
            header_format = workbook.add_format({
                'bold': True, 'bg_color': '#4F81BD', 'font_color': '#FFFFFF', 'border': 1,
                'align': 'center', 'valign': 'vcenter'
            })
            part_name_format = workbook.add_format({
                'bold': True, 'bg_color': '#D9E1F2', 'border': 1,
                'align': 'center', 'valign': 'vcenter'
            })
            part_detail_format = workbook.add_format({
                'bg_color': '#FCE4D6', 'border': 1,
                'align': 'center', 'valign': 'vcenter'
            })
            currency_format = workbook.add_format({
                'num_format': '¥##0.00', 'bg_color': '#E2EFDA', 'border': 1,
                'align': 'center', 'valign': 'vcenter'
            })
            number_format = workbook.add_format({
                'num_format': '0.00', 'bg_color': '#FFF2CC', 'border': 1,
                'align': 'center', 'valign': 'vcenter'
            })
            normal_format = workbook.add_format({
                'bg_color': '#FFFFFF', 'border': 1,
                'align': 'center', 'valign': 'vcenter'
            })
            
            # 标题区块
            worksheet.merge_range('A1:B1', '金属3D打印预算报告',
                                  workbook.add_format({
                                      'bold': True, 'font_size': 14, 'bg_color': '#4F81BD', 'font_color': '#FFFFFF',
                                      'align': 'center', 'border': 1
                                  }))
            worksheet.merge_range('A2:B2', f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
                                  normal_format)
            
            # 输入参数动态生成
            params = [
                ['总打印时长', result['输入参数']['总打印时长']],
                ['零件数量', f"{result['输入参数']['零件数量']}件"]
            ]
            
            # 修改零件体积提取逻辑，直接从字典中获取数据
            for i, part in enumerate(result['输入参数']['零件清单'], 1):
                params.extend([
                    [f'零件{i}名称', part['name']],
                    [f'零件{i}体积', f"{part['volume']:.3f}mm³"],
                    [f'零件{i}支撑体积', f"{part['support_volume']:.3f}mm³"]
                ])
            
            # 定义定价标准的单位
            pricing_units = {
                "钛粉密度": "g/cm³",
                "致密系数": "",  # 无单位
                "用量比例": "",  # 无单位
                "材料单价": "元/公斤",
                "机时费率": "元/小时",
                "氩气单价": "元",
                "氩气耗率": "升/小时",
                "后处理费": "元",
                "折扣优惠": ""  # 无单位
            }
            
            # 为定价标准添加单位
            pricing_standard_with_units = [
                [param, f"{value} {pricing_units.get(param, '')}".strip()]
                for param, value in result['定价标准'].items()
            ]
            
            # 数据写入逻辑
            def write_section(data, start_row, title):
                worksheet.merge_range(start_row, 0, start_row, 1, title, header_format)
                for row_idx, (label, value) in enumerate(data, start_row + 1):
                    if "零件" in label and "名称" in label:  # 零件名称行加背景颜色
                        cell_format = part_name_format
                    elif "体积" in label:  # 零件体积和支撑体积行加背景颜色
                        cell_format = part_detail_format
                    elif title == "费用明细":
                        if "费用" in label or "金额" in label or "后处理费" in label:  # 判断是否为货币
                            cell_format = currency_format
                        else:
                            cell_format = normal_format
                    else:
                        cell_format = number_format if isinstance(value, (int, float)) else normal_format
                    
                    worksheet.write(row_idx, 0, label, cell_format)
                    worksheet.write(row_idx, 1, value, cell_format)
                return start_row + len(data) + 2
            
            current_row = 3
            current_row = write_section(params, current_row, "输入参数")
            current_row = write_section(pricing_standard_with_units, current_row, "定价标准")
            current_row = write_section(
                [[k, v] for k, v in result['计算明细'].items()],
                current_row, "费用明细"
            )
            
            # 智能列宽设置
            worksheet.set_column('A:A', 25)
            worksheet.set_column('B:B', 25)
            
            QMessageBox.information(None, "导出成功", f"Excel 报表已成功保存至：\n{filename}")
            normalized_path = os.path.normpath(filename)
            subprocess.Popen(f'explorer /select,"{normalized_path}"')

    except PermissionError:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("文件被占用")
        msg_box.setText(f"文件 {filename} 正在被占用，无法写入。\n\n请关闭该文件后重试。")
        msg_box.setIcon(QMessageBox.Warning)
        retry_button = msg_box.addButton("重试", QMessageBox.AcceptRole)
        cancel_button = msg_box.addButton("取消", QMessageBox.RejectRole)
        msg_box.exec_()

        if msg_box.clickedButton() == retry_button:
            export_to_excel(result, filename)  # 递归重试
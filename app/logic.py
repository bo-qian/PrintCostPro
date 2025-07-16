'''
Author: bo-qian bqian@shu.edu.cn
Date: 2025-07-16 15:18:52
LastEditors: bo-qian bqian@shu.edu.cn
LastEditTime: 2025-07-16 20:38:27
FilePath: \PrintCostPro\app\logic.py
Description: Logic calculations for the 3D printing cost calculator application
Copyright (c) 2025 by Bo Qian, All Rights Reserved. 
'''

import re

def convert_duration_to_hours(duration_str):
    # 初始化时间单位
    days = hours = minutes = seconds = 0
    
    # 使用正则表达式提取各时间单位
    patterns = {
        'days': r'(\d+)天',
        'hours': r'(\d+)小时',
        'minutes': r'(\d+)分',
        'seconds': r'(\d+)秒'
    }
    
    for unit, pattern in patterns.items():
        match = re.search(pattern, duration_str)
        if match:
            value = int(match.group(1))
            if unit == 'days':
                days = value
            elif unit == 'hours':
                hours = value
            elif unit == 'minutes':
                minutes = value
            elif unit == 'seconds':
                seconds = value
    
    # 转换为总小时数（保留3位小数）
    total_hours = (
        days * 24 + 
        hours + 
        minutes / 60 + 
        seconds / 3600
    )

    # 四舍五入到2位小数
    return total_hours

def calculate_multipart_cost(parts, total_print_duration, pricing_standard):
    # 总材料计算，使用零件体积和支撑体积的总和
    total_volume = sum(p['volume'] + p['support_volume'] for p in parts)
    material_weight_g = (total_volume * 1e-3 * pricing_standard["钛粉密度"]
                         * pricing_standard["用量比例"] * pricing_standard["致密系数"])
    material_cost = material_weight_g * pricing_standard["材料单价"] * 1e-3

    # 机时费用
    machine_hours = convert_duration_to_hours(total_print_duration)
    machine_cost = machine_hours * pricing_standard["机时费率"]

    # 其他费用
    argon_cost = (pricing_standard["氩气单价"] / 165) * (pricing_standard["氩气耗率"] * machine_hours)
    post_processing = pricing_standard["后处理费"]

    # 费用汇总
    total_cost = material_cost + machine_cost + argon_cost + post_processing
    actual_cost = total_cost * pricing_standard["折扣优惠"]

    return {
        "输入参数": {
            "零件清单": [f"{p['name']} (零件体积：{p['volume']:.3f}mm³，支撑体积：{p['support_volume']:.3f}mm³)" for p in parts],
            "总打印时长": total_print_duration,
            "零件数量": len(parts)
        },
        "定价标准": pricing_standard,
        "计算明细": {
            "材料费用": round(material_cost, 2),
            "机时费用": round(machine_cost, 2),
            "氩气费用": round(argon_cost, 2),
            "后处理费": round(post_processing, 2),
            "总费用": round(total_cost, 2),
            "实际费用": round(actual_cost, 2)
        }
    }
import unicodedata

def get_display_width(text):
    """计算字符串的显示宽度"""
    width = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ('F', 'W'):  # 全角字符
            width += 2
        else:  # 半角字符
            width += 1
    return width

def center_text(text, total_width):
    """根据显示宽度居中字符串"""
    text_width = get_display_width(text)
    padding = (total_width - text_width) // 2
    return " " * padding + text + " " * padding

def format_terminal_output(result, char_count):
    
    """增强型终端报表，支持对齐"""
    char_count = char_count - 0
    border = "=" * char_count

    # 确保零件清单中的每个元素是字典
    parts_info = "\n".join([
        f"  零件{i+1}: {part['name']}（总体积：{part['volume'] + part['support_volume']:.3f}mm³）"
        if isinstance(part, dict) else f"  零件{i+1}: {part}"  # 如果不是字典，直接输出字符串
        for i, part in enumerate(result['输入参数']['零件清单'])
    ])

    # 使用宽度感知的居中方法
    title = " 预算计算结果 "
    border = "=" * char_count
    centered_title = center_text(title, char_count)

    left_width = 20
    right_width = char_count - left_width - 7
    dash_line = "  " + "-" * (char_count - 4) + "  "

    output = [
        f"{border}",
        centered_title,
        border,
        "[打印参数]",
        f"  零件数量：{result['输入参数']['零件数量']}件",
        f"  打印时长：{result['输入参数']['总打印时长']}",
        "\n[零件清单]",
        f"{parts_info}",
        "\n[费用明细]",
        f"{'  项目名称'.ljust(left_width)}{'金额'.rjust(right_width - 1)}",
        dash_line,
        f"{'  材料成本：'.ljust(left_width)}{'¥{:>10,.2f}'.format(result['计算明细']['材料费用']).rjust(right_width)}",
        f"{'  机时费用：'.ljust(left_width)}{'¥{:>10,.2f}'.format(result['计算明细']['机时费用']).rjust(right_width)}",
        f"{'  氩气消耗：'.ljust(left_width)}{'¥{:>10,.2f}'.format(result['计算明细']['氩气费用']).rjust(right_width)}",
        f"{'  后处理费：'.ljust(left_width)}{'¥{:>10,.2f}'.format(result['计算明细']['后处理费']).rjust(right_width)}",
        dash_line,
        f"{'  合计金额：'.ljust(left_width)}{'¥{:>10,.2f}'.format(result['计算明细']['总费用']).rjust(right_width)}",
        f"{'  折扣优惠：'.ljust(left_width)}{str(result['定价标准']['折扣优惠']).rjust(right_width)}",
        f"{'  实付金额：'.ljust(left_width)}{'¥{:>10,.2f}'.format(result['计算明细']['实际费用']).rjust(right_width)}",
        border
    ]
    return "\n".join(output)
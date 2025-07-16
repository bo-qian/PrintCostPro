from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QPlainTextEdit, QFileDialog, QFormLayout, QCheckBox, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon, QFontDatabase
from PyQt5.QtCore import Qt
from utils import resource_path
import os
import pandas as pd

from openpyxl import load_workbook
from logic import calculate_multipart_cost
from formatter import format_terminal_output
from exporter import export_to_excel

class CostCalculatorApp(QWidget):
    def __init__(self):
        super().__init__()
        icon_path = resource_path("app/resources/3dprint.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.setWindowTitle("PrintCostPro - 3D打印预算计算器")
        # self.setMinimumSize(800, 500)
        self.setMinimumWidth(900)  # 初始窗口宽度
        # self.initial_height = 500  # 初始窗口高度
        self.expanded_height = 900  # 扩展后窗口高度

        self.parts = []
        self.pricing_standard = {
            "钛粉密度": 4.50,
            "致密系数": 0.9995,
            "用量比例": 1.5,
            "材料单价": 1800,
            "机时费率": 250,
            "氩气单价": 1800,
            "氩气耗率": 27.5,
            "后处理费": 1500,
            "折扣优惠": 1.0
        }

        self.init_ui()

    def init_ui(self):
        font = QFont("Microsoft YaHei", 10)

        main_layout = QVBoxLayout()  # 主布局，垂直分布

        # 尝试加载系统字体
        font = self.load_chinese_font()

        # 设置样式表，应用圆角框并将背景颜色改为白色
        rounded_style = """
            QLineEdit, QPushButton, QPlainTextEdit {
            border: 2px solid #8f8f91;
            border-radius: 10px;
            padding: 5px;
            background-color: #ffffff;  /* 设置背景颜色为白色 */
            }
            QLineEdit:focus, QPushButton:pressed, QPlainTextEdit:focus {
            border: 2px solid #0078d7;
            }
        """

        # 创建水平布局：左侧零件信息，右侧定价标准参数
        content_layout = QHBoxLayout()

        # 左侧布局：零件信息输入
        left_layout = QVBoxLayout()

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)  # 设置标签右对齐

        # 替换零件信息输入部分为读取 Excel 文件按钮
        load_button = QPushButton("加载零件信息 (xlsm)", self)
        load_button.setFont(font)
        load_button.setStyleSheet("""
            QPushButton {
            background-color: #4CAF50;  /* 绿色背景 */
            color: white;  /* 白色文字 */
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            }
            QPushButton:hover {
            background-color: #45a049;  /* 鼠标悬停时的颜色 */
            }
            QPushButton:pressed {
            background-color: #3e8e41;  /* 按下时的颜色 */
            }
        """)
        load_button.clicked.connect(self.load_parts_from_excel)
        left_layout.addWidget(load_button)  # 将按钮添加到左侧布局

        # 零件信息框
        self.parts_display = QPlainTextEdit(self)
        self.parts_display.setFont(font)
        self.parts_display.setReadOnly(True)
        self.parts_display.setStyleSheet(rounded_style)
        self.parts_display.setLineWrapMode(QPlainTextEdit.NoWrap)  # 禁用自动换行

        # 美化滑动条样式
        self.parts_display.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 启用垂直滚动条
        self.parts_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 启用水平滚动条
        self.parts_display.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
            border: none;
            background: #f0f0f0;
            width: 12px;
            margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
            background: #c0c0c0;
            border-radius: 6px;
            min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
            background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
            height: 0px;
            }
        """)
        self.parts_display.horizontalScrollBar().setStyleSheet("""
            QScrollBar:horizontal {
            border: none;
            background: #f0f0f0;
            height: 12px;
            margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
            background: #c0c0c0;
            border-radius: 6px;
            min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
            background: #a0a0a0;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            background: none;
            width: 0px;
            }
        """)

        # 调整零件信息框的高度
        # self.parts_display.setFixedHeight(343)  # 设置固定高度为 343 像素

        # 将零件信息框添加到左侧布局
        left_layout.addWidget(self.parts_display)

        # 打印时长输入框
        duration_label = QLabel("打印时长", self)
        duration_label.setFont(font)
        self.duration_input = QLineEdit(self)
        self.duration_input.setText("11天11小时11分11秒")  # 设置默认值
        self.duration_input.setFont(font)
        self.duration_input.setStyleSheet(rounded_style)

        # 将打印时长输入框添加到布局
        duration_layout = QFormLayout()
        duration_layout.addRow(duration_label, self.duration_input)
        left_layout.addLayout(duration_layout)

        # 启用导出到 Excel 的复选框
        self.export_checkbox = QCheckBox("导出到 Excel 报告", self)
        self.export_checkbox.setFont(font)  # 使用加载的 Microsoft YaHei 字体
        self.export_checkbox.setChecked(False)  # 默认未选中
        self.export_checkbox.setFixedHeight(self.duration_input.sizeHint().height())  # 设置高度与打印时长输入框一致
        self.export_checkbox.setStyleSheet("""
            QCheckBox {
            spacing: 10px;  /* 文字与复选框的间距 */
            vertical-align: middle;  /* 垂直居中 */
            }
            QCheckBox::indicator {
            width: 18px;  /* 复选框宽度 */
            height: 18px;  /* 复选框高度 */
            }
            QCheckBox::indicator:unchecked {
            border: 2px solid #8f8f91;  /* 未选中时的边框颜色 */
            background-color: #ffffff;  /* 未选中时的背景颜色 */
            border-radius: 6px;  /* 圆角 */
            }
            QCheckBox::indicator:checked {
            border: 2px solid #4CAF50;  /* 选中时的边框颜色 */
            background-color: #4CAF50;  /* 选中时的背景颜色 */
            border-radius: 6px;  /* 圆角 */
            }
            QCheckBox::indicator:unchecked:hover {
            border: 2px solid #0078D7;  /* 鼠标悬停时未选中状态的边框颜色 */
            }
            QCheckBox::indicator:checked:hover {
            border: 2px solid #45a049;  /* 鼠标悬停时选中状态的边框颜色 */
            background-color: #45a049;  /* 鼠标悬停时选中状态的背景颜色 */
            }
        """)
        
        # 将复选框添加到布局中，与右侧的折扣优惠上下对齐
        duration_layout.addRow(self.export_checkbox)

        # 一键清零按钮
        clear_button = QPushButton("一键清零", self)
        clear_button.setFont(font)
        clear_button.setStyleSheet("""
            QPushButton {
            background-color: #FF5722;  /* 橙色背景 */
            color: white;  /* 白色文字 */
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            }
            QPushButton:hover {
            background-color: #E64A19;  /* 鼠标悬停时的颜色 */
            }
            QPushButton:pressed {
            background-color: #D84315;  /* 按下时的颜色 */
            }
        """)
        clear_button.clicked.connect(self.clear_parts_display)  # 连接到修改后的方法

        # 将一键清零按钮添加到左侧布局的最下面
        left_layout.addWidget(clear_button)

        content_layout.addLayout(left_layout)

        # 右侧布局：定价标准参数输入和打印时长
        right_layout = QVBoxLayout()

        param_layout = QFormLayout()
        param_layout.setLabelAlignment(Qt.AlignRight)  # 设置标签右对齐
        self.param_inputs = {}
        for param, default_value in self.pricing_standard.items():
            label = QLabel(param, self)
            label.setFont(font)

            # 创建输入框和单位标签
            param_input_layout = QHBoxLayout()
            input_field = QLineEdit(self)
            input_field.setFont(font)
            input_field.setStyleSheet(rounded_style)
            input_field.setText(str(default_value))  # 设置默认值
            self.param_inputs[param] = input_field
            param_input_layout.addWidget(input_field)

            # 添加单位标签（如果有）
            if param == "钛粉密度":
                unit_label = QLabel("g/cm³", self)
            elif param == "材料单价":
                unit_label = QLabel("元/公斤", self)
            elif param == "机时费率":
                unit_label = QLabel("元/小时", self)
            elif param == "氩气单价":
                unit_label = QLabel("元/瓶（165L）", self)
            elif param == "氩气耗率":
                unit_label = QLabel("升/小时", self)
            elif param == "后处理费":
                unit_label = QLabel("元", self)
            else:
                unit_label = None

            if unit_label:
                unit_label.setFont(font)
                param_input_layout.addWidget(unit_label)

            param_layout.addRow(label, param_input_layout)

        right_layout.addLayout(param_layout)

        # 计算成本按钮
        calc_button = QPushButton("计算成本", self)
        calc_button.setFont(font)
        calc_button.setStyleSheet("""
            QPushButton {
            background-color: #0078D7;  /* 蓝色背景 */
            color: white;  /* 白色文字 */
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            }
            QPushButton:hover {
            background-color: #005A9E;  /* 鼠标悬停时的颜色 */
            }
            QPushButton:pressed {
            background-color: #004578;  /* 按下时的颜色 */
            }
        """)
        calc_button.clicked.connect(self.calculate_cost)

        right_layout.addWidget(calc_button)

        content_layout.addLayout(right_layout)

        # 添加内容布局到主布局
        main_layout.addLayout(content_layout)

        # 设置结果显示框容器
        self.result_container = QWidget(self)  # 创建一个容器
        result_layout = QVBoxLayout(self.result_container)  # 容器内部使用垂直布局
        result_layout.setContentsMargins(0, 0, 0, 0)  # 去除容器的边距

        # 设置容器的圆角样式
        self.result_container.setStyleSheet("""
            QLineEdit, QPushButton, QPlainTextEdit {
            border: 2px solid #8f8f91;
            border-radius: 10px;
            padding: 5px;
            background-color: #ffffff;  /* 设置背景颜色为白色 */
            }
            QLineEdit:focus, QPushButton:pressed, QPlainTextEdit:focus {
            border: 2px solid #0078d7;
            }
        """)

        self.result_output = QPlainTextEdit(self)
        self.result_output.setFont(QFont("Maple Mono NF CN", 10))  # 设置等宽字体
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet(rounded_style)
        self.result_output.setLineWrapMode(QPlainTextEdit.NoWrap)  # 禁用自动换行

        # 美化滑动条样式
        self.result_output.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 启用垂直滚动条
        self.result_output.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 启用水平滚动条
        self.result_output.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
            border: none;
            background: #f0f0f0;
            width: 12px;
            margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
            background: #c0c0c0;
            border-radius: 6px;
            min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
            background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
            height: 0px;
            }
        """)
        self.result_output.horizontalScrollBar().setStyleSheet("""
            QScrollBar:horizontal {
            border: none;
            background: #f0f0f0;
            height: 12px;
            margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
            background: #c0c0c0;
            border-radius: 6px;
            min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
            background: #a0a0a0;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            background: none;
            width: 0px;
            }
        """)

        # 设置最小高度
        self.result_output.setMinimumHeight(300)  # 设置最小高度为 300 像素

        # 启用滚动条并设置滚动条样式
        self.result_output.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 启用垂直滚动条
        self.result_output.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 启用水平滚动条

        # 将结果显示框添加到容器布局
        result_layout.addWidget(self.result_output)

        # 将容器添加到主布局
        main_layout.addWidget(self.result_container, stretch=1)

        # 设置主布局
        self.setLayout(main_layout)

        self.adjustSize()  # 告诉 Qt 自动计算需要的窗口大小
        self.parts_display.setFixedHeight(self.parts_display.height())
        self.initial_size = self.size()  # 现在再获取尺寸才是正确的
        print(f"初始窗口大小: {self.initial_size.width()}x{self.initial_size.height()}")

    def load_chinese_font(self):
        font_path = resource_path("app/resources/PingFang-Medium.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        loaded_fonts = QFontDatabase.applicationFontFamilies(font_id)

        if loaded_fonts:
            font = QFont(loaded_fonts[0])
            font.setBold(True)
            font.setPointSize(12)
            return font
        else:
            print("⚠️ 字体加载失败，使用默认字体")
            return QFont()
    
    def clear_parts_display(self):
        """清空零件信息框和输出信息框的内容"""
        self.parts_display.clear()  # 清空零件信息框
        self.result_output.clear()  # 清空输出信息框
        self.parts = []  # 清空零件信息列表


    def load_parts_from_excel(self):
        """从 Excel 文件加载零件信息"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 Excel 文件", "", "Excel 文件 (*.xlsm)")
        if not file_path:
            return

        try:
            workbook = load_workbook(file_path, data_only=True)
            sheet = workbook.active

            # 从 Excel 文件中读取零件信息
            part_count = int(sheet["C2"].value)
            self.parts = []
            self.parts_display.clear()

            for row in range(8, 8 + part_count):
                name = sheet[f"B{row}"].value
                volume = float(sheet[f"C{row}"].value)
                support_volume = float(sheet[f"D{row}"].value)
                self.parts.append({'name': name, 'volume': volume, 'support_volume': support_volume})
                # 修改输出格式
                self.parts_display.appendPlainText(
                    f"零件{row - 7}: {name}\n    零件体积：{volume:.3f}mm³\n    支撑体积：{support_volume:.3f}mm³"
                )

        except Exception as e:
            self.result_output.setStyleSheet("color: red; font-size: 12pt;")
            self.result_output.setPlainText(f"加载 Excel 文件失败：{e}")


    def calculate_cost(self):
        try:
            for param, input_field in self.param_inputs.items():
                try:
                    value = float(input_field.text())
                    self.pricing_standard[param] = value
                except ValueError:
                    self.result_output.setStyleSheet("color: red; font-size: 12pt;")  # 设置字体为红色和大小
                    self.result_output.setPlainText(f"参数 {param} 的值无效，请输入数字！")
                    return

            # 调用成本计算函数
            total_print_duration = self.duration_input.text().strip()
            if not total_print_duration or not self.parts:
                self.result_output.setStyleSheet("color: red; font-size: 12pt;")  # 设置字体为红色和大小
                self.result_output.setPlainText("请先加载零件信息和填写打印时长！\n")
                return

            # 确保零件信息格式正确
            formatted_parts = [
                {'name': part['name'], 'volume': part['volume'], 'support_volume': part['support_volume']}
                for part in self.parts
            ]

            # 调用成本计算函数
            result = calculate_multipart_cost(formatted_parts, total_print_duration, self.pricing_standard)

            # 确保支撑体积在报告中正确显示
            result['输入参数']['零件清单'] = formatted_parts

            char_count = 70
            report = format_terminal_output(result, char_count)
            self.result_output.setStyleSheet("color: black; font-size: 12pt;")  # 恢复正常字体颜色
            self.result_output.setPlainText(report)

            # 显示结果显示框
            self.result_output.parentWidget().setVisible(True)

            # 检查是否启用了导出功能
            if self.export_checkbox.isChecked():
                filename, _ = QFileDialog.getSaveFileName(self, "保存为 Excel", "多零件预算报告.xlsx", "Excel 文件 (*.xlsx)")
                if filename:
                    export_to_excel(result, filename)
                    self.result_output.appendPlainText(f"\n报表已保存至：{filename}")

        except Exception as e:
            self.result_output.setStyleSheet("color: red; font-size: 12pt;")
            self.result_output.setPlainText(f"❌ 计算失败：{e}")
            self.result_container.setVisible(True)  # ✅ 出错时也显示出来
'''
Author: bo-qian bqian@shu.edu.cn
Date: 2025-07-16 15:18:40
LastEditors: bo-qian bqian@shu.edu.cn
LastEditTime: 2025-07-16 15:25:15
FilePath: \PrintCostPro\app\gui.py
Description: GUI for the 3D printing cost calculator application
Copyright (c) 2025 by Bo Qian, All Rights Reserved. 
'''

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class CostCalculatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PrintCostPro - 多零件3D打印成本助手")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel("🎉 欢迎使用 PrintCostPro")
        layout.addWidget(label)
        self.setLayout(layout)
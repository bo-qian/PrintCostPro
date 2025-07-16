'''
Author: bo-qian bqian@shu.edu.cn
Date: 2025-07-16 15:18:32
LastEditors: bo-qian bqian@shu.edu.cn
LastEditTime: 2025-07-16 15:22:28
FilePath: \PrintCostPro\app\main.py
Description: main entry point for the 3D printing cost calculator application
Copyright (c) 2025 by Bo Qian, All Rights Reserved. 
'''

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from gui import CostCalculatorApp
import os

def main():
    app = QApplication(sys.argv)

    # 图标路径（项目相对路径）
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "3dprint.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = CostCalculatorApp()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from gui import CostCalculatorApp
from utils import resource_path
import os

def main():
    try:
        app = QApplication(sys.argv)

        # 图标路径
        icon_path = resource_path("app/resources/3dprint.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

        window = CostCalculatorApp()
        window.show()

        sys.exit(app.exec_())

    except Exception as e:
        QMessageBox.critical(None, "启动失败", f"错误信息：{str(e)}")

if __name__ == "__main__":
    main()
# PrintCostPro

> 桌面端多零件 3D 打印成本估算工具，基于 PyQt5 开发。

---

## 📁 项目结构

```
PrintCostPro/
├── app/
│   ├── main.py
│   ├── gui.py
│   ├── logic.py
│   ├── exporter.py
│   ├── formatter.py
│   ├── utils.py
│   └── resources/
│       ├── 3dprint.ico
│       ├── MapleMono-NF-CN-Regular.ttf
│       └── PingFang-Medium.ttf
├── dist/
├── build.bat
├── requirements.txt
├── README.md
```

---

## 📦 安装依赖

- 推荐 Python 3.8–3.10
- 安装依赖：

  ```bash
  pip install -r requirements.txt
  ```

**requirements.txt 内容：**

```
PyQt5
openpyxl
pandas
xlsxwriter
pyinstaller
```

---

## 🚀 运行方式

开发调试：

```bash
python app/main.py
```

---

## 🔨 打包为 Windows 可执行文件

1. 安装 PyInstaller：

   ```bash
   pip install pyinstaller
   ```

2. 执行打包脚本：

   - 双击 `build.bat`（包含删除中间文件），或在终端输入：

     ```bash
     build.bat
     ```

   - 实际运行命令：

     ```bash
     pyinstaller app/main.py --onefile --noconsole --icon=app/resources/3dprint.ico \
       --add-data "app/resources/3dprint.ico;app/resources" \
       --add-data "app/resources/MapleMono-NF-CN-Regular.ttf;app/resources" \
       --add-data "app/resources/PingFang-Medium.ttf;app/resources" \
       --name PrintCostPro --paths=app
     ```

   - 打包后可执行文件位置：

     ```
     dist/PrintCostPro.exe
     ```

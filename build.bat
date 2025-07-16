@echo off
chcp 65001 >nul
echo 🔧 正在使用 PyInstaller 打包 PrintCostPro...

pyinstaller app/main.py ^
  --onefile ^
  --noconsole ^
  --icon=app/resources/3dprint.ico ^
  --add-data "app/resources/3dprint.ico;app/resources" ^
  --add-data "app/resources/MapleMono-NF-CN-Regular.ttf;app/resources" ^
  --add-data "app/resources/PingFang-Medium.ttf;app/resources" ^
  --name PrintCostPro ^
  --paths=app

echo ✅ 打包完成，结果位于 dist\PrintCostPro.exe

echo 🧹 正在清理中间文件...

rd /s /q build
rd /s /q __pycache__
del /q *.spec

echo ✅ 清理完毕
pause
@echo off
chcp 65001 >nul
title 智剧通启动器打包工具

echo.
echo ========================================
echo   智剧通启动器打包工具
echo ========================================
echo.

cd /d "%~dp0"

python build_launcher.py

echo.
echo 按任意键退出...
pause >nul

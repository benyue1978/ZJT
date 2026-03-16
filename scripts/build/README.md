# 智剧通启动器打包工具

## 功能

这个工具会自动：
1. 检查 Python 环境中是否安装了必需的模块（pystray、PIL、PyInstaller）
2. 自动安装缺失的模块
3. 清理之前的构建文件
4. 执行打包生成 "点我启动.exe"
5. 验证输出文件

## 使用方法

### 方法一：使用批处理脚本（推荐）
```bash
# 双击运行或在命令行执行
scripts\build\build.bat
```

### 方法二：直接运行 Python 脚本
```bash
python scripts\build\build_launcher.py
```

### 方法三：手动执行
```bash
cd scripts\build
python build_launcher.py
```

## 输出

打包成功后会在项目根目录生成：
- `点我启动.exe` - 可执行的启动器程序

## 环境要求

- Python 3.10+
- Windows 系统
- 网络连接（用于安装依赖）

## 故障排除

如果遇到问题：
1. 确保当前 Python 环境有管理员权限
2. 检查网络连接
3. 手动安装依赖：
   ```bash
   pip install pystray Pillow pyinstaller
   ```

## 托盘功能

打包后的程序应该具备：
- 系统托盘图标显示
- 启动状态指示（橙色=启动中，绿色=就绪，红色=错误）
- 右键菜单（打开浏览器、查看日志、退出）
- 自动打开浏览器

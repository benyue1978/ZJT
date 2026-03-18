#!/usr/bin/env python
"""
智剧通启动器打包脚本
自动检查环境依赖并执行打包
"""
import os
import sys
import subprocess
import shutil


def check_module(module_name):
    """检查模块是否存在"""
    try:
        __import__(module_name)
        print(f"✓ {module_name} 已安装")
        return True
    except ImportError:
        print(f"✗ {module_name} 未安装")
        return False


def install_module(module_name):
    """安装模块"""
    print(f"正在安装 {module_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
        print(f"✓ {module_name} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ {module_name} 安装失败")
        return False


def check_environment():
    """检查运行环境"""
    print("=== 环境检查 ===")
    print(f"Python 路径: {sys.executable}")
    print(f"Python 版本: {sys.version}")
    
    # 检查必需的模块
    required_modules = ["pystray", "PIL", "PyInstaller"]
    missing_modules = []
    
    for module in required_modules:
        if not check_module(module):
            missing_modules.append(module)
    
    # 安装缺失的模块
    if missing_modules:
        print("\n=== 安装缺失模块 ===")
        for module in missing_modules:
            if not install_module(module):
                print(f"无法安装 {module}，请手动安装")
                return False
    
    return True


def clean_build():
    """清理构建文件"""
    print("\n=== 清理构建文件 ===")
    
    # 删除构建目录和文件
    dirs_to_clean = ["build", "dist"]
    files_to_clean = ["点我启动.spec", "点我启动.exe"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✓ 删除目录: {dir_name}")
            except Exception as e:
                print(f"✗ 删除目录失败 {dir_name}: {e}")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"✓ 删除文件: {file_name}")
            except Exception as e:
                print(f"✗ 删除文件失败 {file_name}: {e}")


def build_launcher():
    """执行打包"""
    print("\n=== 开始打包 ===")
    
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    # 切换到项目根目录
    os.chdir(project_root)
    print(f"工作目录: {project_root}")
    
    # 构建打包命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole", 
        "--name", "点我启动",
        "--icon=files/logo.ico",
        "--distpath=.",
        "--hidden-import=pystray",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageDraw", 
        "--hidden-import=PIL.ImageFont",
        "--add-data", "files/logo.ico;files",
        "scripts/launchers/launcher.py"
    ]
    
    print("执行命令:")
    print(" ".join(f'"{arg}"' if " " in arg else arg for arg in cmd))
    
    try:
        subprocess.check_call(cmd)
        print("\n✓ 打包成功！")
        
        # 检查输出文件
        exe_path = os.path.join(project_root, "点我启动.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"✓ 输出文件: {exe_path} ({file_size:.1f} MB)")
            return True
        else:
            print("✗ 未找到输出文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 打包失败: {e}")
        return False


def main():
    """主函数"""
    print("智剧通启动器打包工具")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        print("\n环境检查失败，请解决后重试")
        return False
    
    # 清理构建文件
    clean_build()
    
    # 执行打包
    if build_launcher():
        print("\n🎉 打包完成！")
        print("可以运行 '点我启动.exe' 测试托盘功能")
        return True
    else:
        print("\n❌ 打包失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

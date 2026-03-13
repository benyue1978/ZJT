#!/usr/bin/env python3
"""
ZJT 打包脚本
生成三个平台的发布包：Windows、macOS x86_64、macOS ARM
"""

import os
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path


# ============================================
# 配置
# ============================================

# NAS 盘路径（存放二进制文件）
NAS_PATH = Path(r"U:\智剧通")

# 当前脚本所在目录（代码目录）
CODE_PATH = Path(__file__).parent.resolve()

# 输出目录
OUTPUT_PATH = CODE_PATH / "dist"

# 不需要打包的文件/目录
EXCLUDE_PATTERNS = [
    "bin",
    ".git",
    "__pycache__",
    "dist",
    "auto_test",
    ".python-version",
]

# 不需要打包的文件
EXCLUDE_FILES = [
    "config_unit.yml",
    "package.py",
    "package.bat",
]


# ============================================
# 平台配置
# ============================================

PLATFORMS = {
    "Windows": {
        "mysql_src": "mysql",
        "mysql_dst": "mysql",
        "ffmpeg_src": "ffmpeg",
        "ffmpeg_dst": "ffmpeg",
        "uv_src": "uv.exe",
        "uv_dst": "uv.exe",
        "extra_files": ["start.bat"],
        "exclude_files": ["start.command", "create_mac_app.sh"],
    },
    "macOS-x86": {
        "mysql_src": "mysql-macos-x86",
        "mysql_dst": "mysql",
        "ffmpeg_src": "ffmpeg_mac",
        "ffmpeg_dst": "ffmpeg",
        "uv_src": "mac_x86_uv",
        "uv_dst": "uv",
        "extra_files": ["start.command", "create_mac_app.sh"],
        "exclude_files": ["start.bat"],
    },
    "macOS-ARM": {
        "mysql_src": "mysql-macos-arm",
        "mysql_dst": "mysql",
        "ffmpeg_src": "ffmpeg_mac",
        "ffmpeg_dst": "ffmpeg",
        "uv_src": "mac_arm_uv",
        "uv_dst": "uv",
        "extra_files": ["start.command", "create_mac_app.sh"],
        "exclude_files": ["start.bat"],
    },
}


# ============================================
# 工具函数
# ============================================

def get_version():
    """获取版本号，优先使用 git tag，否则使用日期"""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=CODE_PATH,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return datetime.now().strftime("%Y%m%d")


def should_exclude(name: str, is_dir: bool = False) -> bool:
    """判断文件/目录是否应该被排除"""
    if is_dir:
        return name in EXCLUDE_PATTERNS
    return name in EXCLUDE_FILES or name.startswith("config_") and name.endswith(".yml")


def copy_source_files(src_dir: Path, dst_dir: Path, exclude_files: list):
    """复制源代码文件"""
    for item in src_dir.iterdir():
        # 跳过排除项
        if should_exclude(item.name, item.is_dir()):
            continue
        if item.name in exclude_files:
            continue

        dst = dst_dir / item.name

        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)


def copy_binaries(dst_dir: Path, platform_config: dict):
    """复制二进制文件"""
    bin_dir = dst_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    # 复制 MySQL
    mysql_src = NAS_PATH / "bin" / platform_config["mysql_src"]
    mysql_dst = bin_dir / platform_config["mysql_dst"]
    print(f"    - MySQL: {platform_config['mysql_src']} -> {platform_config['mysql_dst']}")
    shutil.copytree(mysql_src, mysql_dst)

    # 复制 FFmpeg
    ffmpeg_src = NAS_PATH / "bin" / platform_config["ffmpeg_src"]
    ffmpeg_dst = bin_dir / platform_config["ffmpeg_dst"]
    print(f"    - FFmpeg: {platform_config['ffmpeg_src']} -> {platform_config['ffmpeg_dst']}")
    shutil.copytree(ffmpeg_src, ffmpeg_dst)

    # 复制 UV
    uv_src = NAS_PATH / "bin" / "uv" / platform_config["uv_src"]
    uv_dst_dir = bin_dir / "uv"
    uv_dst_dir.mkdir(parents=True, exist_ok=True)
    uv_dst = uv_dst_dir / platform_config["uv_dst"]
    print(f"    - UV: {platform_config['uv_src']} -> uv/{platform_config['uv_dst']}")
    shutil.copy2(uv_src, uv_dst)


def create_zip(src_dir: Path, output_file: Path):
    """创建 ZIP 压缩包"""
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(src_dir.parent)
                zf.write(file_path, arcname)


def build_platform(name: str, config: dict, version: str):
    """构建单个平台的发布包"""
    print(f"[{name}] Building...")

    # 创建临时目录
    temp_dir = OUTPUT_PATH / "temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 包目录
    package_name = f"ZJT-{name}"
    package_dir = temp_dir / package_name
    package_dir.mkdir(parents=True, exist_ok=True)

    # 复制源代码
    print("  - Copying source files...")
    copy_source_files(CODE_PATH, package_dir, config["exclude_files"])

    # 复制二进制文件
    print("  - Copying binaries...")
    copy_binaries(package_dir, config)

    # 复制额外的启动文件
    print("  - Copying startup files...")
    for extra_file in config["extra_files"]:
        src = CODE_PATH / extra_file
        if src.exists():
            shutil.copy2(src, package_dir / extra_file)

    # 创建 ZIP
    output_file = OUTPUT_PATH / f"{package_name}-{version}.zip"
    print(f"  - Creating archive: {output_file.name}...")
    create_zip(package_dir, output_file)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    print(f"  [OK] {package_name}-{version}.zip")
    print()

    return output_file


# ============================================
# 主函数
# ============================================

def main():
    print()
    print("=" * 50)
    print("  ZJT Package Builder")
    print("=" * 50)
    print()

    # 检查 NAS 路径
    if not NAS_PATH.exists():
        print(f"[ERROR] NAS path not found: {NAS_PATH}")
        print("[INFO] Please ensure NAS drive is connected")
        input("\nPress Enter to exit...")
        return

    # 创建输出目录
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # 获取版本号
    version = get_version()
    print(f"[INFO] Version: {version}")
    print(f"[INFO] Source: {CODE_PATH}")
    print(f"[INFO] Binaries: {NAS_PATH}")
    print(f"[INFO] Output: {OUTPUT_PATH}")
    print()

    # 构建各平台
    output_files = []
    for i, (name, config) in enumerate(PLATFORMS.items(), 1):
        print(f"[{i}/{len(PLATFORMS)}] ", end="")
        output_file = build_platform(name, config, version)
        output_files.append(output_file)

    # 完成
    print("=" * 50)
    print("  Build Complete!")
    print("=" * 50)
    print()
    print("Output files:")
    for f in output_files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  - {f.name} ({size_mb:.1f} MB)")
    print()
    print(f"Location: {OUTPUT_PATH}")
    print()

    input("Press Enter to exit...")


if __name__ == "__main__":
    main()

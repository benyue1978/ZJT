#!/bin/bash
export comfyui_env=prod


# 使用统一启动器管理 scheduler 和 gunicorn
python3 run_prod.py

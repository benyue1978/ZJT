#!/bin/bash

# ZJT Mac 停止脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "========================================"
echo "  ZJT Server Stop (macOS)"
echo "========================================"
echo ""

# 停止 MySQL
echo "[INFO] Checking MySQL..."
if pgrep -f "mysqld" > /dev/null 2>&1; then
    echo "[INFO] Stopping MySQL service..."
    pkill -f mysqld

    # 等待进程结束
    timeout=10
    while [ $timeout -gt 0 ]; do
        if ! pgrep -f "mysqld" > /dev/null 2>&1; then
            echo "[OK] MySQL stopped"
            break
        fi
        sleep 1
        timeout=$((timeout - 1))
    done

    # 超时后强制停止
    if pgrep -f "mysqld" > /dev/null 2>&1; then
        echo "[WARN] MySQL did not stop gracefully, forcing..."
        pkill -9 -f mysqld
    fi
else
    echo "[INFO] MySQL not running"
fi

# 停止 Python（项目相关）
echo ""
echo "[INFO] Checking Python processes..."

# 查找并停止 run_prod.py
if pgrep -f "run_prod.py" > /dev/null 2>&1; then
    echo "[INFO] Stopping Python application (run_prod.py)..."
    pkill -f "run_prod.py"

    # 等待进程结束
    timeout=10
    while [ $timeout -gt 0 ]; do
        if ! pgrep -f "run_prod.py" > /dev/null 2>&1; then
            echo "[OK] Python stopped"
            break
        fi
        sleep 1
        timeout=$((timeout - 1))
    done

    # 超时后强制停止
    if pgrep -f "run_prod.py" > /dev/null 2>&1; then
        echo "[WARN] Python did not stop gracefully, forcing..."
        pkill -9 -f "run_prod.py"
    fi
else
    echo "[INFO] Python application not running"
fi

# 停止 run_scheduler.py
if pgrep -f "run_scheduler.py" > /dev/null 2>&1; then
    echo "[INFO] Stopping scheduler process..."
    pkill -f "run_scheduler.py"
fi

# 停止 gunicorn（Web 服务）
if pgrep -f "gunicorn.*server:app" > /dev/null 2>&1; then
    echo "[INFO] Stopping gunicorn..."
    pkill -f "gunicorn.*server:app"
fi

echo ""
echo "========================================"
echo "[OK] All services stopped"
echo "========================================"
echo ""

# 短暂暂停以便用户看到输出
sleep 2

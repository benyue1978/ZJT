# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "mysql-connector-python>=8.0.0",
#   "pyyaml>=6.0",
# ]
# ///
"""
Windows 启动脚本
用于 Windows 系统上启动和管理本地服务

功能：
1. 启动 MySQL 服务（bin/mysql）
2. 首次启动时执行 --initialize-insecure 初始化
3. 从 config_{env}.yml 读取数据库密码并设置
4. 首次初始化时导入 model/sql/baseline.sql
5. 通过 uv 启动 run_{env}.py（Web 服务 + 定时任务）
6. 服务监控和自动重启
"""
import subprocess
import os
import sys
import time
import logging
import socket
import atexit
import signal
import shutil
import yaml

import mysql.connector
from mysql.connector import Error as MysqlError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

mysql_process = None
app_process = None
is_shutting_down = False


def get_current_dir():
    """
    获取当前目录，兼容打包后的路径
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def load_config():
    """
    加载配置文件
    根据环境变量 comfyui_env 加载对应的配置文件
    默认使用 config_prod.yml
    """
    env = os.getenv("comfyui_env", "prod")
    config_file = os.path.join(get_current_dir(), f"config_{env}.yml")

    if not os.path.exists(config_file):
        logger.error(f"配置文件不存在: {config_file}")
        return None

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            logger.info(f"已加载配置文件: {config_file}")
            return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return None


def check_mysql_path():
    """
    检查 MySQL 相关路径
    Returns:
        tuple: (bool, dict|str) - (是否找到所有必需文件, 包含所有路径的字典或错误信息)
    """
    try:
        current_dir = get_current_dir()
        mysql_dir = os.path.join(current_dir, 'bin', 'mysql')

        if not os.path.exists(mysql_dir):
            return False, f"MySQL目录不存在: {mysql_dir}"

        mysql_bin_dir = os.path.join(mysql_dir, 'bin')
        if not os.path.exists(mysql_bin_dir):
            return False, f"MySQL bin目录不存在: {mysql_bin_dir}"

        mysqld_exe = os.path.join(mysql_bin_dir, 'mysqld.exe')
        if not os.path.exists(mysqld_exe):
            return False, f"mysqld.exe不存在: {mysqld_exe}"

        mysql_client = os.path.join(mysql_bin_dir, 'mysql.exe')
        if not os.path.exists(mysql_client):
            return False, f"mysql.exe不存在: {mysql_client}"

        mysql_ini = os.path.join(mysql_dir, 'my.ini')
        if not os.path.exists(mysql_ini):
            return False, f"my.ini不存在: {mysql_ini}"

        paths = {
            'mysql_dir': mysql_dir,
            'mysql_bin_dir': mysql_bin_dir,
            'mysqld_exe': mysqld_exe,
            'mysql_client': mysql_client,
            'mysql_ini': mysql_ini
        }
        return True, paths

    except Exception as e:
        return False, f"检查MySQL路径时发生错误: {e}"


def check_mysql_data_dir():
    """
    检查 MySQL 数据目录是否为空或不存在
    Returns:
        bool: 如果目录为空或不存在返回 True（需要初始化），否则返回 False
    """
    try:
        data_dir = os.path.join(get_current_dir(), 'data', 'mysql')

        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            logger.info(f"创建数据目录: {data_dir}")
            return True

        if len(os.listdir(data_dir)) == 0:
            return True

        return False
    except Exception as e:
        logger.error(f"检查MySQL数据目录时出错: {e}")
        return True


def get_mysql_port():
    """
    从 MySQL 配置文件中获取端口号
    Returns:
        int: MySQL 端口号，默认为 3306
    """
    try:
        current_dir = get_current_dir()
        mysql_ini = os.path.join(current_dir, 'bin', 'mysql', 'my.ini')

        if not os.path.exists(mysql_ini):
            logger.warning(f"MySQL配置文件不存在: {mysql_ini}，使用默认端口3306")
            return 3306

        with open(mysql_ini, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('port='):
                    try:
                        return int(line.split('=')[1])
                    except (IndexError, ValueError):
                        logger.warning(f"解析端口号失败: {line}")
                        return 3306

        logger.info("未在配置文件中找到端口配置，使用默认端口3306")
        return 3306
    except Exception as e:
        logger.error(f"读取MySQL端口配置时出错: {e}")
        return 3306


def check_port_in_use(port):
    """
    检查指定端口是否被占用
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            return result == 0
    except Exception as e:
        logger.error(f"检查端口状态时发生错误: {e}")
        return False


def start_mysql_service():
    """
    启动 MySQL 服务
    Returns:
        tuple: (bool, str, bool) - (是否成功启动, 消息, 是否是首次初始化)
    """
    global mysql_process

    try:
        mysql_exists, mysql_paths = check_mysql_path()
        if not mysql_exists:
            return False, mysql_paths, False

        mysqld_exe = mysql_paths['mysqld_exe']
        mysql_ini = mysql_paths['mysql_ini']

        port = get_mysql_port()
        is_first_init = check_mysql_data_dir()

        if check_port_in_use(port):
            logger.info(f"MySQL服务已经在端口 {port} 运行")
            return True, "MySQL服务已经在运行", False

        if is_first_init:
            logger.info("MySQL数据目录为空，正在初始化...")
            cmd = [mysqld_exe, f'--defaults-file={mysql_ini}', '--initialize-insecure']
            logger.info(f"正在执行初始化命令: {' '.join(cmd)}")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            stdout, stderr = process.communicate()
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                return False, f"MySQL初始化失败，错误信息：{error_msg}", False
            logger.info("MySQL数据目录初始化成功")

        cmd = [mysqld_exe, f"--defaults-file={mysql_ini}"]
        logger.info(f"正在执行启动命令: {' '.join(cmd)}")

        mysql_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        retry_count = 0
        max_retries = 60 if is_first_init else 30

        while retry_count < max_retries:
            if check_port_in_use(port):
                logger.info(f"MySQL服务已启动，端口: {port}")
                return True, "MySQL服务启动成功", is_first_init

            if mysql_process.poll() is not None:
                stdout, stderr = mysql_process.communicate()
                error_msg = stderr.decode('utf-8', errors='ignore')
                return False, f"MySQL进程已退出，错误信息：{error_msg}", False

            logger.info(f"等待MySQL启动... ({retry_count + 1}/{max_retries})")
            time.sleep(1)
            retry_count += 1

        stdout, stderr = mysql_process.communicate()
        error_msg = stderr.decode('utf-8', errors='ignore')
        if error_msg:
            return False, f"MySQL服务启动超时，错误信息：{error_msg}", False
        return False, "MySQL服务启动超时，无错误信息", False

    except Exception as e:
        return False, f"启动MySQL服务时发生错误: {e}", False


def init_database(config):
    """
    检查并初始化数据库
    - 首次启动时设置 root 密码
    - 导入 baseline.sql
    """
    try:
        mysql_port = get_mysql_port()
        target_password = config['database']['password']

        logger.info("开始尝试连接MySQL...")

        conn = None
        current_password = ""
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                logger.info(f"尝试使用密码连接MySQL... (第{retry_count + 1}次)")
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password=target_password,
                    port=mysql_port
                )
                current_password = target_password
                logger.info("使用目标密码连接成功")
                break
            except MysqlError as e:
                logger.warning(f"使用目标密码连接失败: {e}")
                if retry_count >= max_retries - 1:
                    try:
                        logger.info("尝试使用空密码连接（首次初始化场景）...")
                        conn = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="",
                            port=mysql_port
                        )
                        current_password = ""
                        logger.info("使用空密码连接成功，需要设置新密码")

                        cursor = conn.cursor()
                        cursor.execute(f"ALTER USER 'root'@'localhost' IDENTIFIED BY '{target_password}'")
                        conn.commit()
                        cursor.close()
                        logger.info("MySQL root密码设置成功")

                        conn.close()
                        conn = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password=target_password,
                            port=mysql_port
                        )
                        current_password = target_password
                        break
                    except MysqlError as empty_pass_error:
                        return False, f"无法连接MySQL: {empty_pass_error}"
                retry_count += 1
                time.sleep(1)

        if conn is None:
            return False, "无法连接到MySQL服务"

        cursor = conn.cursor()

        logger.info("检查zjt数据库是否存在...")
        cursor.execute("SHOW DATABASES LIKE 'zjt'")
        database_exists = cursor.fetchone() is not None

        if not database_exists:
            logger.info("zjt数据库不存在，准备导入baseline.sql...")

            current_dir = get_current_dir()
            baseline_sql_path = os.path.join(current_dir, 'model', 'sql', 'baseline.sql')

            if not os.path.exists(baseline_sql_path):
                cursor.close()
                conn.close()
                return False, f"找不到baseline.sql文件: {baseline_sql_path}"

            mysql_exists, mysql_paths = check_mysql_path()
            if not mysql_exists:
                cursor.close()
                conn.close()
                return False, "MySQL路径检查失败"

            mysql_client = mysql_paths['mysql_client']

            logger.info(f"使用MySQL客户端程序导入: {mysql_client}")
            cmd = [
                mysql_client,
                '-uroot',
                f'-P{mysql_port}',
                f'-p{current_password}',
                '-e',
                f'source {baseline_sql_path}'
            ]
            logger.info(f"执行命令: {mysql_client} -uroot -P{mysql_port} -p*** -e 'source {baseline_sql_path}'")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                logger.info("数据库表初始化成功")
            else:
                error_msg = stderr.decode('utf-8', errors='ignore')
                cursor.close()
                conn.close()
                return False, f"数据库初始化失败: {error_msg}"
        else:
            logger.info("zjt数据库已存在，跳过初始化")

        cursor.close()
        conn.close()
        logger.info("数据库操作完成，连接已关闭")

        return True, "数据库初始化成功"

    except Exception as e:
        logger.error(f"初始化数据库时发生错误: {e}")
        return False, f"初始化数据库时发生错误: {e}"


def check_mysql_status():
    """
    检查 MySQL 是否正在运行
    """
    global mysql_process

    port = get_mysql_port()

    if not check_port_in_use(port):
        return False

    if mysql_process is not None and mysql_process.poll() is not None:
        return False

    return True


def check_app_status():
    """
    检查应用进程是否正在运行
    """
    global app_process

    if app_process is None:
        return False

    if app_process.poll() is not None:
        return False

    return True


def get_env():
    """
    获取当前环境
    """
    return os.getenv("comfyui_env", "prod")


def start_app_service():
    """
    通过 uv 启动 run_{env}.py
    Returns:
        tuple: (bool, str) - (是否成功启动, 消息)
    """
    global app_process

    try:
        env = get_env()
        current_dir = get_current_dir()
        run_script = os.path.join(current_dir, f"run_{env}.py")

        if not os.path.exists(run_script):
            return False, f"启动脚本不存在: {run_script}"

        uv_path = shutil.which("uv")
        if uv_path is None:
            uv_path = os.path.join(os.path.expanduser("~"), ".local", "bin", "uv.exe")
            if not os.path.exists(uv_path):
                return False, "找不到 uv 可执行文件，请确保已安装 uv"

        logger.info(f"使用 uv 启动: {run_script}")
        requirements_file = os.path.join(current_dir, "requirements.txt")

        cmd = [uv_path, "run"]
        if os.path.exists(requirements_file):
            cmd.extend(["--with-requirements", requirements_file])
            logger.info(f"使用依赖文件: {requirements_file}")
        cmd.append(run_script)

        logger.info(f"执行命令: {' '.join(cmd)}")

        app_process = subprocess.Popen(
            cmd,
            cwd=current_dir,
            stdout=sys.stdout,
            stderr=sys.stderr
        )

        time.sleep(3)

        if app_process.poll() is not None:
            return False, f"应用进程启动后立即退出，退出码: {app_process.returncode}"

        return True, f"应用服务启动成功 (run_{env}.py)"

    except Exception as e:
        return False, f"启动应用服务时发生错误: {e}"


def monitor_services():
    """
    监控 MySQL 和应用服务，异常退出时自动重启
    """
    global is_shutting_down

    logger.info("开始监控服务...")
    mysql_restart_count = 0
    app_restart_count = 0
    max_restarts = 5

    while not is_shutting_down:
        try:
            if not check_mysql_status():
                if is_shutting_down:
                    break

                mysql_restart_count += 1
                if mysql_restart_count > max_restarts:
                    logger.error(f"MySQL已重启{max_restarts}次，超过最大限制，停止监控")
                    break

                logger.warning(f"检测到MySQL服务异常，尝试重启... (第{mysql_restart_count}次)")
                success, message, _ = start_mysql_service()
                if success:
                    logger.info(f"MySQL服务重启成功: {message}")
                else:
                    logger.error(f"MySQL服务重启失败: {message}")
                    time.sleep(10)
            else:
                mysql_restart_count = 0

            if not check_app_status():
                if is_shutting_down:
                    break

                app_restart_count += 1
                if app_restart_count > max_restarts:
                    logger.error(f"应用服务已重启{max_restarts}次，超过最大限制，停止监控")
                    break

                logger.warning(f"检测到应用服务异常，尝试重启... (第{app_restart_count}次)")
                success, message = start_app_service()
                if success:
                    logger.info(f"应用服务重启成功: {message}")
                else:
                    logger.error(f"应用服务重启失败: {message}")
                    time.sleep(10)
            else:
                app_restart_count = 0

            time.sleep(5)

        except Exception as e:
            logger.error(f"监控服务时发生错误: {e}")
            time.sleep(5)


def stop_mysql_gracefully():
    """
    使用 mysqladmin shutdown 优雅停止 MySQL
    """
    try:
        mysql_exists, mysql_paths = check_mysql_path()
        if not mysql_exists:
            return False

        current_dir = get_current_dir()
        mysql_client = mysql_paths['mysql_client']
        mysqladmin = os.path.join(mysql_paths['mysql_bin_dir'], 'mysqladmin.exe')

        if not os.path.exists(mysqladmin):
            logger.warning(f"mysqladmin 不存在: {mysqladmin}")
            return False

        config = load_config()
        password = config['database']['password'] if config and 'database' in config else ""
        port = get_mysql_port()

        cmd = [mysqladmin, '-uroot', f'-P{port}', 'shutdown']
        if password:
            cmd.insert(2, f'-p{password}')

        logger.info("使用 mysqladmin shutdown 停止 MySQL...")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        stdout, stderr = process.communicate(timeout=15)

        if process.returncode == 0:
            logger.info("MySQL 已优雅停止")
            return True
        else:
            error_msg = stderr.decode('utf-8', errors='ignore')
            logger.warning(f"mysqladmin shutdown 失败: {error_msg}")
            return False

    except subprocess.TimeoutExpired:
        logger.warning("mysqladmin shutdown 超时")
        return False
    except Exception as e:
        logger.error(f"停止 MySQL 时出错: {e}")
        return False


def cleanup():
    """
    清理函数，停止所有服务
    """
    global mysql_process, app_process, is_shutting_down

    is_shutting_down = True
    logger.info("正在停止所有服务...")

    if app_process is not None:
        try:
            logger.info("正在停止应用服务...")
            app_process.terminate()
            app_process.wait(timeout=10)
            logger.info("应用服务已停止")
        except subprocess.TimeoutExpired:
            logger.warning("应用服务停止超时，强制结束")
            app_process.kill()
        except Exception as e:
            logger.error(f"停止应用服务时出错: {e}")

    if mysql_process is not None:
        logger.info("正在停止MySQL服务...")
        if not stop_mysql_gracefully():
            try:
                logger.info("尝试强制终止MySQL进程...")
                mysql_process.terminate()
                mysql_process.wait(timeout=10)
                logger.info("MySQL服务已停止")
            except subprocess.TimeoutExpired:
                logger.warning("MySQL服务停止超时，强制结束")
                mysql_process.kill()
            except Exception as e:
                logger.error(f"停止MySQL服务时出错: {e}")


def signal_handler(signum, frame):
    """
    信号处理函数
    """
    logger.info(f"收到信号 {signum}，正在退出...")
    cleanup()
    sys.exit(0)


def main():
    """
    主函数
    """
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup)

    env = get_env()
    logger.info("=" * 50)
    logger.info(f"Windows 启动脚本 (环境: {env})")
    logger.info("=" * 50)

    config = load_config()
    if config is None:
        logger.error("无法加载配置文件，退出")
        sys.exit(1)

    if 'database' not in config or 'password' not in config['database']:
        logger.error("配置文件中缺少 database.password 配置")
        sys.exit(1)

    mysql_exists, mysql_result = check_mysql_path()
    if not mysql_exists:
        logger.error(f"MySQL检查失败: {mysql_result}")
        sys.exit(1)
    logger.info("MySQL路径检查成功")

    logger.info("正在启动MySQL服务...")
    success, message, is_first_init = start_mysql_service()
    logger.info(message)
    if not success:
        logger.error("MySQL服务启动失败，退出")
        sys.exit(1)

    if is_first_init:
        logger.info("检测到首次初始化，正在初始化数据库...")
        success, message = init_database(config)
        logger.info(message)
        if not success:
            logger.error("数据库初始化失败，退出")
            sys.exit(1)

    logger.info("正在启动应用服务...")
    success, message = start_app_service()
    logger.info(message)
    if not success:
        logger.error("应用服务启动失败，退出")
        sys.exit(1)

    logger.info("所有服务已就绪，开始监控...")
    try:
        monitor_services()
    except KeyboardInterrupt:
        logger.info("收到退出信号")
    finally:
        cleanup()

    logger.info("Windows启动脚本退出")


if __name__ == "__main__":
    main()

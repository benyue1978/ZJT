# ComfyUI Server Windows 启动说明

## 📋 前置要求

在启动项目之前，请确保已完成以下准备工作：

### 1. 安装 Python
- 版本要求：Python 3.10 或更高版本
- 下载地址：https://www.python.org/downloads/
- **重要**：安装时请勾选 "Add Python to PATH"

### 2. 配置 MySQL
- 将 MySQL 解压到项目的 `bin/mysql` 目录
- 确保 `bin/mysql/bin/mysqld.exe` 存在
- 确保 `bin/mysql/my.ini` 配置文件存在
- **注意**：启动脚本会自动更新 `my.ini` 中的 `basedir` 和 `datadir` 路径为当前项目路径，无需手动修改

### 3. 创建配置文件
- 复制 `config.example.yml` 为 `config_prod.yml`（生产环境）
- 或复制为 `config_dev.yml`（开发环境）
- 根据实际情况修改配置文件中的参数，特别是：
  - `database.password`：数据库密码
  - `server.port`：服务端口
  - 其他 API 密钥等配置

## 🚀 启动方式

项目提供了三种启动方式，可根据需要选择：

### 方式一：双击启动（推荐新手）
**文件**：`启动（显示日志）.bat`

- ✅ 显示详细的启动日志
- ✅ 可以看到运行状态和错误信息
- ✅ 适合调试和查看问题
- 📝 双击即可运行，控制台窗口会保持打开

**使用场景**：
- 首次启动
- 需要查看日志
- 排查问题

### 方式二：后台启动（推荐日常使用）
**文件**：`启动（静默模式）.vbs`

- ✅ 后台运行，无控制台窗口
- ✅ 启动时显示提示框
- ✅ 不占用桌面空间
- 📝 双击即可运行

**使用场景**：
- 日常使用
- 不需要查看日志
- 希望界面简洁

### 方式三：命令行启动（推荐开发者）
**文件**：`启动.bat`

- ✅ 基础启动脚本
- ✅ 可以在命令行中调用
- ✅ 支持环境变量配置

**使用方法**：
```batch
# 默认使用生产环境（prod）
启动.bat

# 或在命令行中设置环境
set comfyui_env=dev
启动.bat
```

## 🔧 环境切换

项目支持多环境配置，通过环境变量 `comfyui_env` 控制：

### 生产环境（默认）
```batch
set comfyui_env=prod
```
使用配置文件：`config_prod.yml`

### 开发环境
```batch
set comfyui_env=dev
```
使用配置文件：`config_dev.yml`

### 单元测试环境
```batch
set comfyui_env=unit
```
使用配置文件：`config_unit.yml`

## 📊 启动流程

启动脚本会自动完成以下步骤：

1. ✓ 检查 Python 环境
2. ✓ 检查/安装 uv 包管理器
3. ✓ 检查配置文件
4. ✓ 检查 MySQL 目录
5. ✓ **自动更新 `my.ini` 中的路径为当前项目路径**
6. ✓ 启动 MySQL 服务（首次会自动初始化）
7. ✓ 设置数据库密码（首次启动）
8. ✓ 导入数据库表结构（首次启动）
9. ✓ 启动 Web 服务和定时任务
10. ✓ 监控服务状态，异常时自动重启

## ❓ 常见问题

### 1. 提示找不到 Python
**解决方法**：
- 安装 Python 3.10+
- 确保安装时勾选了 "Add Python to PATH"
- 或手动将 Python 添加到系统环境变量

### 2. MySQL 启动失败
**可能原因**：
- `bin/mysql` 目录不存在或不完整
- 端口被占用（默认 3306）
- `my.ini` 配置文件有误

**解决方法**：
- 检查 MySQL 文件是否完整
- 修改 `my.ini` 中的端口配置
- 查看日志文件排查具体错误

### 3. 配置文件不存在
**解决方法**：
```batch
# 复制示例配置文件
copy config.example.yml config_prod.yml

# 然后编辑 config_prod.yml，填入实际配置
```

### 4. uv 安装失败
**解决方法**：
```batch
# 手动安装 uv
python -m pip install uv

# 或使用国内镜像
python -m pip install uv -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5. 服务启动后无法访问
**检查项**：
- 查看控制台日志，确认服务是否成功启动
- 检查 `config_prod.yml` 中的 `server.port` 配置
- 确认防火墙是否允许该端口
- 浏览器访问：`http://localhost:端口号`

## 🛑 停止服务

### 方式一：控制台窗口
如果使用 `启动（显示日志）.bat`：
- 按 `Ctrl + C` 停止服务
- 脚本会自动优雅关闭 MySQL 和应用服务

### 方式二：任务管理器
如果使用静默模式：
1. 打开任务管理器（Ctrl + Shift + Esc）
2. 找到 `python.exe` 和 `mysqld.exe` 进程
3. 结束这些进程

### 方式三：创建停止脚本
可以创建一个 `停止.bat` 脚本：
```batch
@echo off
taskkill /F /IM mysqld.exe
taskkill /F /IM python.exe
echo 服务已停止
pause
```

## 📝 日志查看

- 应用日志：控制台输出或 `logs/` 目录
- MySQL 日志：`data/mysql/` 目录下的错误日志文件

## 🔄 更新项目

```batch
# 1. 停止服务
# 2. 拉取最新代码
git pull

# 3. 更新依赖（如有需要）
uv pip sync requirements.txt

# 4. 重新启动服务
启动（显示日志）.bat
```

## 📞 技术支持

如遇到问题，请：
1. 查看控制台日志
2. 检查 `logs/` 目录下的日志文件
3. 参考本文档的常见问题部分
4. 联系技术支持团队

---

**祝使用愉快！** 🎉

"""
Configuration utility functions for ComfyUI server
"""
import os


def resolve_bin_path(config_path: str, app_dir: str) -> str:
    """
    解析可执行文件路径

    - 如果是绝对路径，直接使用
    - 如果是相对路径，基于 app_dir 解析为绝对路径
    - 如果是纯命令名（无路径分隔符），直接使用（依赖 PATH）

    Args:
        config_path: 配置文件中的路径值
        app_dir: 应用根目录路径

    Returns:
        解析后的完整路径或命令名
    """
    if not config_path:
        return None

    # 如果是纯命令名（无路径分隔符），直接使用
    if os.sep not in config_path and '/' not in config_path:
        return config_path

    # 如果已经是绝对路径，直接使用
    if os.path.isabs(config_path):
        return config_path

    # 相对路径：基于 app_dir 解析
    return os.path.join(app_dir, config_path)


def get_config_path(config_path: str = None) -> str:
    """
    Get configuration file path based on environment variable
    
    Args:
        config_path: Optional explicit config path. If provided, returns as-is.
        
    Returns:
        Path to configuration file
        - If comfyui_env is not set: config_dev.yml (default development)
        - If comfyui_env is set: config_{env}.yml (e.g., config_prod.yml)
        
    Example:
        >>> # When comfyui_env is not set
        >>> get_config_path()
        'config_dev.yml'
        >>> # When comfyui_env=prod
        >>> get_config_path()
        'config_prod.yml'
        >>> # Explicit path
        >>> get_config_path("custom.yml")
        'custom.yml'
    """
    if config_path is not None:
        return config_path
    
    env = os.getenv("comfyui_env")
    
    # If env variable is not set, default to dev
    if env is None:
        return "config_dev.yml"
    
    # If env variable is set, use config_{env}.yml format
    return f"config_{env}.yml"


def is_dev_environment() -> bool:
    """
    Check if running in development environment
    
    Returns:
        True if comfyui_env is not set or equals 'dev', False otherwise
    """
    env = os.getenv("comfyui_env")
    return env is None or env == "dev"

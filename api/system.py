"""
系统状态 API 路由
"""
from fastapi import APIRouter
import logging

from model.users import UsersModel
from config.unified_config import UnifiedConfigRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/status")
async def get_system_status():
    """
    获取系统状态
    返回系统是否已初始化（是否有用户）
    """
    try:
        total_users = UsersModel.get_total_count()
        
        return {
            "code": 0,
            "data": {
                "initialized": total_users > 0,
                "total_users": total_users
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return {
            "code": 1,
            "message": str(e)
        }


@router.get("/task-configs")
async def get_task_configs():
    """
    获取所有任务类型配置
    
    返回前端需要的完整配置信息，包括：
    - 任务列表（支持的比例、尺寸、时长等）
    - 分类信息
    - 供应商信息
    
    前端可以根据此接口动态渲染模型选择器、参数配置等组件
    """
    try:
        frontend_config = UnifiedConfigRegistry.get_frontend_config()
        return {
            "code": 0,
            "data": frontend_config
        }
    except Exception as e:
        logger.error(f"Failed to get task configs: {e}")
        return {
            "code": 1,
            "message": str(e)
        }


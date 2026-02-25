"""
SerialNumberService 序列号服务 - 对应Go的handler/serial_number.go
"""
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from model.users import UsersModel
from model.valid_serial_number import ValidSerialNumberModel

logger = logging.getLogger(__name__)


class SerialNumberService:
    """序列号服务 - 获取、更新、验证序列号等"""
    
    @staticmethod
    def get_serial_number(user_id: int) -> Dict[str, Any]:
        """
        获取用户序列号
        
        Args:
            user_id: 用户ID
            
        Returns:
            序列号信息
        """
        user = UsersModel.get_by_id(user_id)
        if not user:
            return {"success": False, "message": "用户不存在"}
        
        serial_number = user.serial_number
        
        if not serial_number:
            return {
                "success": True,
                "data": {
                    "serial_number": None,
                    "valid": False,
                    "expiration_time": None,
                }
            }
        
        # 获取序列号详情
        vsn = ValidSerialNumberModel.get_by_serial_number(serial_number)
        if not vsn:
            return {
                "success": True,
                "data": {
                    "serial_number": serial_number,
                    "valid": False,
                    "expiration_time": None,
                }
            }
        
        is_valid = vsn.expired_time and vsn.expired_time > datetime.now() if vsn.expired_time else False
        
        return {
            "success": True,
            "data": {
                "serial_number": serial_number,
                "valid": is_valid,
                "expiration_time": vsn.expired_time.isoformat() if vsn.expired_time else None,
            }
        }
    
    @staticmethod
    def update_serial_number(user_id: int, serial_number: str) -> Dict[str, Any]:
        """
        更新用户序列号
        
        Args:
            user_id: 用户ID
            serial_number: 新序列号
            
        Returns:
            操作结果
        """
        if not serial_number:
            return {"success": False, "message": "序列号不能为空"}
        
        # 检查序列号是否已被其他用户使用
        if UsersModel.check_serial_number_exists(serial_number):
            return {"success": False, "message": "序列号已被使用"}
        
        # 检查序列号是否有效
        if not ValidSerialNumberModel.check_valid(serial_number):
            return {"success": False, "message": "序列号无效或已过期"}
        
        # 更新用户序列号
        UsersModel.update_serial_number(user_id, serial_number)
        
        # 标记序列号为已使用
        ValidSerialNumberModel.mark_used(serial_number, user_id)
        
        logger.info(f"序列号更新成功 - 用户ID: {user_id}, 序列号: {serial_number}")
        
        return {"success": True, "message": "序列号更新成功"}
    
    @staticmethod
    def check_serial_number(serial_number: str) -> Dict[str, Any]:
        """
        验证序列号是否有效
        
        Args:
            serial_number: 序列号
            
        Returns:
            验证结果
        """
        if not serial_number:
            return {"success": False, "message": "序列号不能为空"}
        
        is_valid = ValidSerialNumberModel.check_valid(serial_number)
        
        return {
            "success": True,
            "data": {
                "is_valid": is_valid,
            }
        }
    
    @staticmethod
    def create_serial_number(
        serial_number: str,
        expired_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        创建新的序列号
        
        Args:
            serial_number: 序列号
            expired_time: 过期时间
            
        Returns:
            创建结果
        """
        if not serial_number:
            return {"success": False, "message": "序列号不能为空"}
        
        # 检查是否已存在
        existing = ValidSerialNumberModel.get_by_serial_number(serial_number)
        if existing:
            return {"success": False, "message": "序列号已存在"}
        
        # 创建序列号
        ValidSerialNumberModel.create(serial_number, expired_time)
        
        logger.info(f"序列号创建成功: {serial_number}")
        
        return {"success": True, "message": "序列号创建成功"}
    
    @staticmethod
    def get_unused_serial_numbers(limit: int = 100) -> Dict[str, Any]:
        """
        获取未使用的序列号列表
        
        Args:
            limit: 返回数量限制
            
        Returns:
            序列号列表
        """
        serial_numbers = ValidSerialNumberModel.get_unused(limit)
        
        return {
            "success": True,
            "data": {
                "serial_numbers": [sn.to_dict() for sn in serial_numbers],
                "count": len(serial_numbers),
            }
        }

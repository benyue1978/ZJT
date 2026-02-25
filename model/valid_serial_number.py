"""
ValidSerialNumber Model - Database operations for valid_serial_number table
对应Go的models/valid_serial_number.go
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from .database import execute_query, execute_update, execute_insert
import logging

logger = logging.getLogger(__name__)


class ValidSerialNumber:
    """ValidSerialNumber model class"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.serial_number = kwargs.get('serial_number')
        self.is_used = kwargs.get('is_used', 0)
        self.used_by = kwargs.get('used_by')
        self.used_at = kwargs.get('used_at')
        self.created_at = kwargs.get('created_at')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'serial_number': self.serial_number,
            'is_used': self.is_used,
            'used_by': self.used_by,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ValidSerialNumberModel:
    """ValidSerialNumber database operations"""
    
    @staticmethod
    def get_by_serial_number(serial_number: str) -> Optional[ValidSerialNumber]:
        """根据序列号获取记录"""
        sql = "SELECT * FROM valid_serial_number WHERE serial_number = %s"
        try:
            result = execute_query(sql, (serial_number,), fetch_one=True)
            if result:
                return ValidSerialNumber(**result)
            return None
        except Exception as e:
            logger.error(f"Failed to get valid serial number: {e}")
            raise
    
    @staticmethod
    def check_valid(serial_number: str) -> bool:
        """检查序列号是否有效（存在且未使用）"""
        sql = "SELECT * FROM valid_serial_number WHERE serial_number = %s AND is_used = 0"
        try:
            result = execute_query(sql, (serial_number,), fetch_one=True)
            return result is not None
        except Exception as e:
            logger.error(f"Failed to check valid serial number: {e}")
            raise
    
    @staticmethod
    def mark_as_used(serial_number: str, user_id: int) -> int:
        """标记序列号为已使用"""
        sql = """
            UPDATE valid_serial_number 
            SET is_used = 1, used_by = %s, used_at = NOW() 
            WHERE serial_number = %s AND is_used = 0
        """
        try:
            return execute_update(sql, (user_id, serial_number))
        except Exception as e:
            logger.error(f"Failed to mark serial number as used: {e}")
            raise
    
    @staticmethod
    def create(serial_number: str) -> int:
        """创建新的序列号"""
        sql = "INSERT INTO valid_serial_number (serial_number) VALUES (%s)"
        try:
            record_id = execute_insert(sql, (serial_number,))
            logger.info(f"Created valid serial number with ID: {record_id}")
            return record_id
        except Exception as e:
            logger.error(f"Failed to create valid serial number: {e}")
            raise
    
    @staticmethod
    def get_unused(limit: int = 100) -> List[ValidSerialNumber]:
        """获取未使用的序列号列表"""
        sql = "SELECT * FROM valid_serial_number WHERE is_used = 0 LIMIT %s"
        try:
            results = execute_query(sql, (limit,), fetch_all=True)
            return [ValidSerialNumber(**row) for row in results] if results else []
        except Exception as e:
            logger.error(f"Failed to get unused serial numbers: {e}")
            raise

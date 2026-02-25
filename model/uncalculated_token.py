"""
UncalculatedToken Model - 未计算token表
对应Go的models/uncalculated_token.go
"""
from typing import Optional
from datetime import datetime
from model.database import get_db_connection


class UncalculatedToken:
    """未计算token实体"""
    
    def __init__(
        self,
        id: int = 0,
        user_id: int = 0,
        uncalculated_input_token: Optional[int] = None,
        uncalculated_output_token: Optional[int] = None,
        uncalculated_cache_read: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.uncalculated_input_token = uncalculated_input_token
        self.uncalculated_output_token = uncalculated_output_token
        self.uncalculated_cache_read = uncalculated_cache_read
        self.created_at = created_at
        self.updated_at = updated_at


class UncalculatedTokenModel:
    """未计算token数据库操作"""
    
    @staticmethod
    def create(
        user_id: int,
        input_token: Optional[int] = None,
        output_token: Optional[int] = None,
        cache_read: Optional[int] = None
    ) -> int:
        """创建未计算token记录"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO uncalculated_token 
                   (user_id, uncalculated_input_token, uncalculated_output_token, uncalculated_cache_read) 
                   VALUES (%s, %s, %s, %s)""",
                (user_id, input_token, output_token, cache_read)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_user_id(user_id: int) -> Optional[UncalculatedToken]:
        """根据用户ID获取未计算token记录"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT id, user_id, uncalculated_input_token, uncalculated_output_token, 
                   uncalculated_cache_read, created_at, updated_at 
                   FROM uncalculated_token WHERE user_id = %s""",
                (user_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return UncalculatedToken(
                id=row['id'],
                user_id=row['user_id'],
                uncalculated_input_token=row['uncalculated_input_token'],
                uncalculated_output_token=row['uncalculated_output_token'],
                uncalculated_cache_read=row['uncalculated_cache_read'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def update(
        user_id: int,
        input_token: Optional[int] = None,
        output_token: Optional[int] = None,
        cache_read: Optional[int] = None
    ) -> bool:
        """更新用户的未计算token"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """UPDATE uncalculated_token 
                   SET uncalculated_input_token = %s, uncalculated_output_token = %s, 
                       uncalculated_cache_read = %s, updated_at = CURRENT_TIMESTAMP 
                   WHERE user_id = %s""",
                (input_token, output_token, cache_read, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete(user_id: int) -> bool:
        """删除用户的未计算token记录"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM uncalculated_token WHERE user_id = %s",
                (user_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

"""
VendorModel Model - 供应商模型配置表
对应Go的models/vendor_model.go
"""
from typing import Optional, List
from datetime import datetime
from model.database import get_db_connection


class VendorModel:
    """供应商模型配置实体"""
    
    def __init__(
        self,
        id: int = 0,
        vendor_id: Optional[int] = None,
        model_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        input_token_threshold: Optional[int] = None,
        output_token_threshold: Optional[int] = None,
        cache_read_threshold: Optional[int] = None
    ):
        self.id = id
        self.vendor_id = vendor_id
        self.model_id = model_id
        self.created_at = created_at
        self.input_token_threshold = input_token_threshold
        self.output_token_threshold = output_token_threshold
        self.cache_read_threshold = cache_read_threshold


class VendorModelModel:
    """供应商模型配置数据库操作"""
    
    @staticmethod
    def create(
        vendor_id: Optional[int] = None,
        model_id: Optional[int] = None,
        input_threshold: Optional[int] = None,
        output_threshold: Optional[int] = None,
        cache_read_threshold: Optional[int] = None
    ) -> int:
        """创建供应商模型配置"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO vendor_model 
                   (vendor_id, model_id, input_token_threshold, out_token_threshold, cache_read_threshold) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (vendor_id, model_id, input_threshold, output_threshold, cache_read_threshold)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_vendor_model(vendor_id: int, model_id: int) -> Optional[VendorModel]:
        """根据vendor_id和model_id获取配置"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT id, vendor_id, model_id, created_at, 
                   input_token_threshold, out_token_threshold as output_token_threshold, cache_read_threshold 
                   FROM vendor_model WHERE vendor_id = %s AND model_id = %s""",
                (vendor_id, model_id)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return VendorModel(
                id=row['id'],
                vendor_id=row['vendor_id'],
                model_id=row['model_id'],
                created_at=row['created_at'],
                input_token_threshold=row['input_token_threshold'],
                output_token_threshold=row['output_token_threshold'],
                cache_read_threshold=row['cache_read_threshold']
            )
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_all(limit: int = 0, offset: int = 0) -> List[VendorModel]:
        """获取所有供应商模型配置"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """SELECT id, vendor_id, model_id, created_at, 
                       input_token_threshold, out_token_threshold as output_token_threshold, cache_read_threshold 
                       FROM vendor_model ORDER BY created_at DESC"""
            params = []
            if limit > 0:
                query += " LIMIT %s"
                params.append(limit)
                if offset > 0:
                    query += " OFFSET %s"
                    params.append(offset)
            
            cursor.execute(query, tuple(params) if params else None)
            rows = cursor.fetchall()
            return [
                VendorModel(
                    id=row['id'],
                    vendor_id=row['vendor_id'],
                    model_id=row['model_id'],
                    created_at=row['created_at'],
                    input_token_threshold=row['input_token_threshold'],
                    output_token_threshold=row['output_token_threshold'],
                    cache_read_threshold=row['cache_read_threshold']
                )
                for row in rows
            ]
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def update_thresholds(
        id: int,
        input_threshold: Optional[int] = None,
        output_threshold: Optional[int] = None,
        cache_read_threshold: Optional[int] = None
    ) -> bool:
        """更新阈值配置"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """UPDATE vendor_model 
                   SET input_token_threshold = %s, out_token_threshold = %s, cache_read_threshold = %s 
                   WHERE id = %s""",
                (input_threshold, output_threshold, cache_read_threshold, id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete(id: int) -> bool:
        """删除供应商模型配置"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM vendor_model WHERE id = %s", (id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

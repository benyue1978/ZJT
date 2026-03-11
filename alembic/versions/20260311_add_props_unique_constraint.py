"""add_props_unique_constraint

Revision ID: 20260311_props_unique
Revises: 20260303_ref_images
Create Date: 2026-03-11 17:30:00.000000+08:00

为 props、character、location 表添加 (world_id, name) 唯一约束，防止同一世界下名称重复
解决并发提交导致的重复创建问题
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260311_props_unique'
down_revision: Union[str, None] = '20260303_ref_images'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级数据库：为 props、character、location 表添加唯一约束"""
    
    # === props 表 ===
    # 先删除可能存在的重复数据，保留最早创建的记录
    op.execute("""
        DELETE p1 FROM props p1
        INNER JOIN props p2 
        WHERE p1.id > p2.id 
        AND p1.world_id = p2.world_id 
        AND p1.name = p2.name
    """)
    # 添加 (world_id, name) 唯一约束
    op.execute("""
        ALTER TABLE `props` 
        ADD UNIQUE INDEX `uk_world_name` (`world_id`, `name`)
    """)
    
    # === character 表 ===
    # 先删除可能存在的重复数据，保留最早创建的记录
    op.execute("""
        DELETE c1 FROM `character` c1
        INNER JOIN `character` c2 
        WHERE c1.id > c2.id 
        AND c1.world_id = c2.world_id 
        AND c1.name = c2.name
    """)
    # 添加 (world_id, name) 唯一约束
    op.execute("""
        ALTER TABLE `character` 
        ADD UNIQUE INDEX `uk_world_name` (`world_id`, `name`)
    """)
    
    # === location 表 ===
    # 先删除可能存在的重复数据，保留最早创建的记录
    op.execute("""
        DELETE l1 FROM `location` l1
        INNER JOIN `location` l2 
        WHERE l1.id > l2.id 
        AND l1.world_id = l2.world_id 
        AND l1.name = l2.name
    """)
    # 添加 (world_id, name) 唯一约束
    op.execute("""
        ALTER TABLE `location` 
        ADD UNIQUE INDEX `uk_world_name` (`world_id`, `name`)
    """)


def downgrade() -> None:
    """回滚数据库：删除唯一约束"""
    
    op.execute("ALTER TABLE `props` DROP INDEX `uk_world_name`")
    op.execute("ALTER TABLE `character` DROP INDEX `uk_world_name`")
    op.execute("ALTER TABLE `location` DROP INDEX `uk_world_name`")

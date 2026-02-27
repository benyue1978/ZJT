#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Action:
    """资源操作类型常量"""
    
    VIEW = "view"      # 查看权限
    EDIT = "edit"      # 编辑权限
    DELETE = "delete"  # 删除权限


class Edition:
    """版本模式管理类"""
    
    # 版本模式常量
    COMMUNITY = "community"
    ENTERPRISE = "enterprise"
    
    @staticmethod
    def get_mode() -> str:
        """获取当前版本模式"""
        from config.config_util import get_config_value
        return get_config_value("edition", "mode", default=Edition.COMMUNITY)
    
    @staticmethod
    def is_community() -> bool:
        """判断是否为开源/社区版"""
        return Edition.get_mode() == Edition.COMMUNITY
    
    @staticmethod
    def is_enterprise() -> bool:
        """判断是否为商业版"""
        return not Edition.is_community()
    
    @staticmethod
    def get_label() -> str:
        """获取版本模式标签"""
        mode = Edition.get_mode()
        return "社区版" if mode == Edition.COMMUNITY else "商业版"


class TaskType:
    """任务类型常量"""
    GENERATE_VIDEO = 'generate_video'
    GENERATE_AUDIO = 'generate_audio'


# 向后兼容别名
TASK_TYPE_GENERATE_VIDEO = TaskType.GENERATE_VIDEO
TASK_TYPE_GENERATE_AUDIO = TaskType.GENERATE_AUDIO

# 1: 图片编辑, 2: Sora2文生视频, 3: Sora2图生视频, 4: 高清放大, 5: ai视频高清修复, 6: 图生视频高清修复，7：图片编辑(nano-banana-pro), 8: 创建角色卡, 
# 9: AI音频生成, 10: LTX2.0图生视频, 11: Wan2.2图生视频（5秒=12，10秒=24）, 12: 可灵图生视频（5秒=38，10秒=55）, 13: 数字人生成, 14: Vidu图生视频（5秒=8）, 15: VEO3图生视频（8秒=6）
TASK_COMPUTING_POWER = {
    1: 2,
    2: 18, #原算力8
    3: 18, #原算力8
    4: 1,
    5: 10,
    6: 10,
    7: 6,
    8: 20,
    9: 5,
    10: 6,
    11: {5: 6, 10: 12},  # Wan2.2根据时长区分算力，原先是5:12 10:24，现在由于sora挂掉，需要它先半价。
    12: {5: 38, 10: 70},  # 可灵根据时长区分算力
    13: 12,  # 数字人生成
    14: {5: 16, 8: 22},  # Vidu根据时长区分算力
    15: 6,  # VEO3固定算力
}

# 视频驱动映射配置
# 任务类型 -> 业务驱动名称 -> 具体实现驱动
# 通过修改这个配置可以随时切换供应商或驱动版本
VIDEO_DRIVER_MAPPING = {
    1: "gemini_image_edit",           # 图片编辑（标准版）
    2: "sora2_text_to_video",          # Sora2 文生视频
    3: "sora2_image_to_video",         # Sora2 图生视频
    7: "gemini_image_edit_pro",        # 图片编辑（加强版）
    10: "ltx2_image_to_video",         # LTX2.0 图生视频
    11: "wan22_image_to_video",        # Wan2.2 图生视频
    12: "kling_image_to_video",        # 可灵图生视频
    13: "digital_human",               # 数字人生成
    14: "vidu_image_to_video",         # Vidu 图生视频
    15: "veo3_image_to_video",         # VEO3 图生视频
}

# 业务驱动名称到具体实现驱动的映射
# 修改这里可以切换不同的供应商或驱动版本
# 格式：业务驱动名称 -> 实现驱动类名
DRIVER_IMPLEMENTATION_MAPPING = {
    # Sora2 相关驱动
    "sora2_text_to_video": "sora2_duomi_v1",      # 使用多米供应商的 Sora2 v1 版本
    "sora2_image_to_video": "sora2_duomi_v1",     # 使用多米供应商的 Sora2 v1 版本
    
    # Kling 相关驱动
    "kling_image_to_video": "kling_duomi_v1",     # 使用多米供应商的 Kling v1 版本
    
    # Gemini 相关驱动
    "gemini_image_edit": "gemini_duomi_v1",       # 使用多米供应商的 Gemini v1 版本（标准版）
    "gemini_image_edit_pro": "gemini_pro_duomi_v1",  # 使用多米供应商的 Gemini Pro v1 版本（加强版）
    
    # VEO3 相关驱动
    "veo3_image_to_video": "veo3_duomi_v1",       # 使用多米供应商的 VEO3 v1 版本
    
    # RunningHub 相关驱动
    "ltx2_image_to_video": "ltx2_runninghub_v1",  # 使用 RunningHub 的 LTX2 v1 版本
    "wan22_image_to_video": "wan22_runninghub_v1", # 使用 RunningHub 的 Wan22 v1 版本
    "digital_human": "digital_human_runninghub_v1", # 使用 RunningHub 的数字人 v1 版本
    
    # Vidu 相关驱动
    "vidu_image_to_video": "vidu_default",         # 使用 Vidu 官方 API
}

# 视频模型时长选项配置
# 注意：时长选项必须与 TASK_COMPUTING_POWER 中对应任务类型的 key 保持一致
# ltx2 -> 任务类型10, wan22 -> 任务类型11, kling -> 任务类型12, vidu -> 任务类型14, sora2 -> 任务类型3
VIDEO_MODEL_DURATION_OPTIONS = {
    'ltx2': [5, 8, 10],  # LTX2.0 固定算力，支持5/8/10秒
    'wan22': list(TASK_COMPUTING_POWER[11].keys()),  # 从算力配置中自动获取时长选项
    'kling': list(TASK_COMPUTING_POWER[12].keys()),  # 从算力配置中自动获取时长选项
    'vidu': list(TASK_COMPUTING_POWER[14].keys()),   # 从算力配置中自动获取时长选项
    'sora2': [15, 10],  # Sora2 固定算力，支持10/15秒
    'veo3': [8],  # VEO3 固定算力，支持8秒
}

# AI Tools 类型分类配置
# 图生视频任务类型列表
IMAGE_TO_VIDEO_TYPES = [3, 10, 11, 12, 14, 15]

# 图片编辑任务类型列表
IMAGE_EDIT_TYPES = [1, 7]

# RunningHub 平台任务类型列表
RUNNINGHUB_TASK_TYPES = [10, 11, 13]

# 任务类型名称映射
TASK_TYPE_NAME_MAP = {
    1: '图片编辑',
    2: 'Sora2文生视频',
    3: '图片生成视频 (Sora2)',
    4: '视频高清放大',
    5: 'AI视频高清修复',
    6: '图生视频高清修复',
    7: '图片编辑 (Pro)',
    8: '创建角色卡',
    9: 'AI音频生成',
    10: '图片生成视频 (LTX2.0)',
    11: '图片生成视频 (Wan2.2)',
    12: '图片生成视频 (可灵)',
    13: '数字人生成',
    14: '图片生成视频 (Vidu)',
    15: '图片生成视频 (VEO3.1)'
}

class AIToolStatus:
    """AI工具状态常量"""
    PENDING = 0       # 未处理
    PROCESSING = 1    # 正在处理
    FAILED = -1       # 处理失败
    COMPLETED = 2     # 处理完成


class TaskStatus:
    """任务状态常量"""
    QUEUED = 0        # 队列中
    PROCESSING = 1    # 处理中
    COMPLETED = 2     # 处理完成
    FAILED = -1       # 处理失败


class AIAudioStatus:
    """AI音频状态常量"""
    PENDING = 0       # 未处理
    PROCESSING = 1    # 处理中
    FAILED = -1       # 处理失败
    COMPLETED = 2     # 处理完成


# 向后兼容别名 - AI Tools 状态
AI_TOOL_STATUS_PENDING = AIToolStatus.PENDING
AI_TOOL_STATUS_PROCESSING = AIToolStatus.PROCESSING
AI_TOOL_STATUS_FAILED = AIToolStatus.FAILED
AI_TOOL_STATUS_COMPLETED = AIToolStatus.COMPLETED

# 向后兼容别名 - Tasks 状态
TASK_STATUS_QUEUED = TaskStatus.QUEUED
TASK_STATUS_PROCESSING = TaskStatus.PROCESSING
TASK_STATUS_COMPLETED = TaskStatus.COMPLETED
TASK_STATUS_FAILED = TaskStatus.FAILED

# 向后兼容别名 - AI Audio 状态
AI_AUDIO_STATUS_PENDING = AIAudioStatus.PENDING
AI_AUDIO_STATUS_PROCESSING = AIAudioStatus.PROCESSING
AI_AUDIO_STATUS_FAILED = AIAudioStatus.FAILED
AI_AUDIO_STATUS_COMPLETED = AIAudioStatus.COMPLETED

class GridConfig:
    """宫格拆分配置常量"""
    SIZE_2X2 = 4                          # 2x2 宫格（标准版）
    SIZE_3X3 = 9                          # 3x3 宫格（加强版）
    VALID_SIZES = (4, 9)                  # 允许的宫格大小
    DEFAULT_SIZE_BY_TYPE = {1: 4, 7: 9}   # AI工具类型 → 默认宫格大小
    LOCK_TIMEOUT_SECONDS = 120            # 文件锁超时（秒）
    IMAGE_DOWNLOAD_TIMEOUT = 60.0         # 下载原图超时（秒）


# 向后兼容别名 - 宫格拆分
GRID_SIZE_2X2 = GridConfig.SIZE_2X2
GRID_SIZE_3X3 = GridConfig.SIZE_3X3
GRID_VALID_SIZES = GridConfig.VALID_SIZES
GRID_DEFAULT_SIZE_BY_TYPE = GridConfig.DEFAULT_SIZE_BY_TYPE
GRID_LOCK_TIMEOUT_SECONDS = GridConfig.LOCK_TIMEOUT_SECONDS
GRID_IMAGE_DOWNLOAD_TIMEOUT = GridConfig.IMAGE_DOWNLOAD_TIMEOUT

class FilePathConstants:
    """文件路径相关常量 - 兼容Windows的跨平台路径配置"""
    
    # 路径常量（相对路径）
    _TTS_AUDIO_SUBDIR = "files/tmp/tts/tmp_ref_audio"
    _JIANYING_EXPORT_SUBDIR = "files/tmp/jianying_export"
    _PIC_TMP_SUBDIR = "files/tmp/pic"
    _SCRIPT_WRITER_USER_DATA_SUBDIR = "files/script_writer"  # 剧本创作系统用户数据根目录

    @staticmethod
    def get_pic_tmp_dir(app_dir: str) -> str:
        """
        获取图片临时目录的完整路径（自动按年月日分组，自动创建目录）

        Args:
            app_dir: 应用根目录路径

        Returns:
            完整的图片临时目录路径，格式：files/tmp/pic/2026-02-26/
        """
        import os
        from datetime import datetime
        date_folder = datetime.now().strftime('%Y-%m-%d')
        path = os.path.join(app_dir, FilePathConstants._PIC_TMP_SUBDIR, date_folder)
        os.makedirs(path, exist_ok=True)
        return path
    
    @staticmethod
    def get_tts_audio_dir(app_dir: str) -> str:
        """
        获取TTS音频目录的完整路径（自动按当前日期分组，自动创建目录）
        
        Args:
            app_dir: 应用根目录路径
            
        Returns:
            完整的TTS音频目录路径，格式：files/tmp/tts/tmp_ref_audio/2026-02-24/
        """
        import os
        from datetime import datetime
        date_folder = datetime.now().strftime('%Y-%m-%d')
        path = os.path.join(app_dir, FilePathConstants._TTS_AUDIO_SUBDIR, date_folder)
        os.makedirs(path, exist_ok=True)
        return path
    
    @staticmethod
    def get_jianying_export_dir(app_dir: str, draft_name: str) -> str:
        """
        获取剪映导出目录的完整路径（自动按当前日期分组，自动创建目录）
        
        Args:
            app_dir: 应用根目录路径
            draft_name: 草稿名称
            
        Returns:
            完整的剪映导出目录路径，格式：files/tmp/jianying_export/2026-02-24/草稿名/
        """
        import os
        from datetime import datetime
        date_folder = datetime.now().strftime('%Y-%m-%d')
        path = os.path.join(app_dir, FilePathConstants._JIANYING_EXPORT_SUBDIR, date_folder, draft_name)
        os.makedirs(path, exist_ok=True)
        return path

RECHARGE_PACKAGES = [
    {
        "package_id": 1,
        "computing_power": 100,
        "price": 0.1,
        "description": "首充福利"
    },
    {
        "package_id": 2,
        "computing_power": 200,
        "price": 9.9,
        "description": "标准套餐"
    },
    {
        "package_id": 3,
        "computing_power": 1250,
        "price": 49.9,
        "description": "进阶套餐"
    }
]
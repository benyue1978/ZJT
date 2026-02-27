"""
阿里云短信发送服务
"""
import logging
import os
import yaml
from typing import Optional

logger = logging.getLogger(__name__)

# 短信配置缓存
_sms_config = None


def _load_sms_config():
    """加载短信配置"""
    global _sms_config
    if _sms_config is not None:
        return _sms_config
    
    try:
        from config.config_util import get_config_path
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_file = get_config_path()
        config_path = os.path.join(app_dir, config_file)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        _sms_config = config.get('sms', {})
        return _sms_config
    except Exception as e:
        logger.error(f"加载短信配置失败: {e}")
        return {}


def get_sms_agent_config(agent: str = 'default') -> Optional[dict]:
    """
    获取短信代理配置
    :param agent: 代理名称
    :return: 代理配置字典
    """
    config = _load_sms_config()
    agents = config.get('agents', {})
    return agents.get(agent)


def send_sms_code(phone: str, code: str, agent: str = 'default') -> dict:
    """
    发送短信验证码
    :param phone: 手机号
    :param code: 验证码
    :param agent: 短信代理名称
    :return: {"success": bool, "message": str}
    """
    try:
        agent_config = get_sms_agent_config(agent)
        if not agent_config:
            logger.error(f"未找到短信代理配置: {agent}")
            return {"success": False, "message": f"未找到短信代理: {agent}"}
        
        access_key_id = agent_config.get('access_key_id')
        access_key_secret = agent_config.get('access_key_secret')
        sign_name = agent_config.get('sign_name')
        template_code = agent_config.get('template_code')
        region_id = agent_config.get('region_id', 'cn-hangzhou')
        
        if not all([access_key_id, access_key_secret, sign_name, template_code]):
            logger.error("短信配置不完整")
            return {"success": False, "message": "短信配置不完整"}
        
        # 导入阿里云SDK
        from alibabacloud_dysmsapi20170525.client import Client as DysmsapiClient
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
        from alibabacloud_tea_util import models as util_models
        
        # 创建客户端配置
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            region_id=region_id
        )
        config.endpoint = f'dysmsapi.aliyuncs.com'
        
        # 创建客户端
        client = DysmsapiClient(config)
        
        # 构建请求
        send_sms_request = dysmsapi_models.SendSmsRequest(
            phone_numbers=phone,
            sign_name=sign_name,
            template_code=template_code,
            template_param=f'{{"code":"{code}"}}'
        )
        
        # 发送短信
        runtime = util_models.RuntimeOptions()
        response = client.send_sms_with_options(send_sms_request, runtime)
        
        if response.body.code == 'OK':
            logger.info(f"短信发送成功: {phone} 验证码：{code}")
            return {"success": True, "message": "验证码发送成功"}
        else:
            error_msg = f"{response.body.code} - {response.body.message}"
            logger.error(f"短信发送失败: {error_msg}")
            return {"success": False, "message": f"短信发送失败: {error_msg}"}
            
    except ImportError as e:
        logger.error(f"阿里云SDK未安装: {e}")
        return {"success": False, "message": "短信服务未配置"}
    except Exception as e:
        logger.error(f"发送短信失败: {e}")
        return {"success": False, "message": f"发送短信失败: {str(e)}"}


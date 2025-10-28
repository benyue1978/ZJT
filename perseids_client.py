import logging
import requests
import traceback
import hmac
import hashlib
import time
import secrets
import json
import os
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# 预共享的密钥（需与服务器端一致）
SECRET_KEY = "7LVmHyyj2UTu"

def generate_signature(data, timestamp, nonce):
    """
    生成签名
    :param data: dict 请求数据
    :param timestamp: int 时间戳
    :param nonce: str 随机字符串
    :return: str 签名
    """
    logger.debug("开始生成签名...")
    logger.debug(f"原始数据: {data}")
    logger.debug(f"时间戳: {timestamp}")
    logger.debug(f"随机数: {nonce}")

    # 将请求参数按字典序排序
    sorted_keys = sorted(data.keys())
    logger.debug(f"排序后的键: {sorted_keys}")
    
    # 构建参数对并进行 URL 编码
    pairs = []
    for k in sorted_keys:
        # 将值转换为字符串
        v = data[k]
        original_v = v
        if isinstance(v, bool):
            v = str(v).lower()
        elif isinstance(v, (int, float)):
            v = str(v)
        elif not isinstance(v, str):
            # 对于其他类型，尝试 JSON 序列化
            try:
                v = json.dumps(v)
            except:
                v = str(v)
        
        logger.debug(f"处理键值对 - 键: {k}, 原始值: {original_v}, 转换后: {v}")
        
        # URL 编码 key 和 value (使用 quote_plus 匹配 Go 的 url.QueryEscape 行为)
        k = quote_plus(str(k))
        v = quote_plus(str(v))
        pair = f"{k}={v}"
        logger.debug(f"URL编码后的键值对: {pair}")
        pairs.append(pair)
    
    # 拼接参数字符串
    data_str = "&".join(pairs)
    logger.debug(f"参数字符串: {data_str}")
    
    # 拼接签名字符串
    sign_str = f"{data_str}&timestamp={timestamp}&nonce={nonce}"
    logger.debug(f"完整签名字符串: {sign_str}")
    
    # 使用 HMAC-SHA256 生成签名
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    logger.debug(f"最终签名: {signature}")
    return signature


def make_perseids_request(base_url, endpoint, data=None, method='POST', headers=None):
    """
    向 Go 服务器发起请求
    :param endpoint: str 接口路径
    :param data: dict 请求数据
    :param method: str 请求方法
    :return: tuple (bool, str, dict) 是否成功，消息，响应数据
    """
    try:
        timeout = 30
        
        # 构建认证 URL，已含有添加 api/v1 前缀
        auth_url = f"{base_url}/{endpoint}"
        logger.info(f"调用认证服务器 URL: {auth_url}")
        
        # 生成签名所需参数
        timestamp = int(time.time())
        nonce = secrets.token_hex(16)
        
        # 构建请求数据
        payload = data or {}
        logger.debug(f"请求数据: {payload}")
        
        # 生成签名
        signature = generate_signature(payload, timestamp, nonce)
        
        # 构建请求头
        request_headers = headers or {}
        request_headers.update({
            'X-Timestamp': str(timestamp),
            'X-Nonce': nonce,
            'X-Signature': signature
        })
        logger.debug(f"请求头: {request_headers}")
        
        response = requests.request(method, auth_url, json=payload, headers=request_headers, timeout=timeout)
        logger.debug(f"响应状态码: {response.status_code}")
        logger.debug(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            return data.get('success', False), data.get('message', ''), data.get('data', {})
        else:
            # 尝试解析错误响应
            try:
                error_data = response.json()
                error_message = error_data.get('message', '未知错误')
            except:
                error_message = f'服务器错误 ({response.status_code}): {response.text}'
            
            logger.error(f'认证服务器返回错误: {error_message}')
            return False, error_message, { }

    except Exception as e:
        logger.error(f'调用认证服务器时发生错误: {str(e)}')
        logger.error(traceback.format_exc())
        return False, '服务器内部错误', {}


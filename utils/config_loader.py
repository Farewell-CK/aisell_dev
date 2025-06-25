import os
import yaml
from typing import Dict, Any

class ConfigLoader:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._load_configs()

    def _load_configs(self):
        """加载所有配置文件"""
        self._config = {}
        
        # 加载API密钥配置
        api_key_path = 'configs/apikey.yaml'
        if os.path.exists(api_key_path):
            with open(api_key_path, 'r', encoding='utf-8') as f:
                self._config['api_keys'] = yaml.safe_load(f)['api_keys']
        
        # 加载数据库配置
        db_config_path = 'configs/database.yaml'
        if os.path.exists(db_config_path):
            with open(db_config_path, 'r', encoding='utf-8') as f:
                self._config['database'] = yaml.safe_load(f)['database']

    def get_api_key(self, service: str, key_type: str = 'api_key') -> str:
        """
        获取指定服务的API密钥或base_url
        
        Args:
            service (str): 服务名称 (qwen, deepseek, ernie)
            key_type (str): 键类型 (api_key 或 base_url)
            
        Returns:
            str: API密钥或base_url
        """
        try:
            return self._config['api_keys'][service][key_type]
        except KeyError:
            raise KeyError(f"未找到服务 {service} 的 {key_type} 配置")

    def get_db_config(self) -> Dict[str, Any]:
        """
        获取数据库配置
        
        Returns:
            Dict[str, Any]: 数据库配置字典
        """
        return self._config.get('database', {}) 
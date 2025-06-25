import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatHistory:
    def __init__(self, tmp_dir: str = 'tmp'):
        """
        初始化聊天历史管理器
        Args:
            tmp_dir: 临时文件存储目录
        """
        self.tmp_dir = tmp_dir
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

    def _get_history_file_path(self, tenant_id: str, task_id: str, session_id: str) -> str:
        """
        获取历史记录文件路径
        """
        return os.path.join(self.tmp_dir, f"{tenant_id}_{task_id}_{session_id}.json")

    def load_history(self, tenant_id: str, task_id: str, session_id: str) -> List[Dict]:
        """
        加载历史聊天记录
        Args:
            tenant_id: 租户ID
            task_id: 任务ID
            session_id: 会话ID
        Returns:
            List[Dict]: 历史聊天记录列表
        """
        file_path = self._get_history_file_path(tenant_id, task_id, session_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载历史记录失败: {str(e)}")
                return []
        return []

    def save_history(self, tenant_id: str, task_id: str, session_id: str, 
                    query: str, response: str) -> None:
        """
        保存聊天记录
        Args:
            tenant_id: 租户ID
            task_id: 任务ID
            session_id: 会话ID
            query: 用户输入
            response: AI响应
        """
        file_path = self._get_history_file_path(tenant_id, task_id, session_id)
        history = self.load_history(tenant_id, task_id, session_id)
        
        # 添加新的对话记录
        history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response
        })
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存历史记录失败: {str(e)}")

    def get_formatted_history(self, tenant_id: str, task_id: str, session_id: str) -> str:
        """
        获取格式化的历史记录，用于模型输入
        Args:
            tenant_id: 租户ID
            task_id: 任务ID
            session_id: 会话ID
        Returns:
            str: 格式化的历史记录
        """
        history = self.load_history(tenant_id, task_id, session_id)
        formatted_history = []
        
        for record in history:
            formatted_history.append(f"用户: {record['query']}")
            formatted_history.append(f"销售: {record['response']}")
        
        return "\n".join(formatted_history) 
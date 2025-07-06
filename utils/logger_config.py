#!/usr/bin/env python3
"""
统一的日志配置模块
提供标准化的日志格式和配置，确保整个项目的日志输出一致
"""

import os
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

# 确保日志目录存在
def ensure_log_directory():
    """确保日志目录存在"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    return log_dir

def setup_logger(name: str = None, level: str = "INFO") -> logging.Logger:
    """
    设置标准化的日志记录器
    
    Args:
        name: 日志记录器名称，默认为模块名
        level: 日志级别，默认为INFO
        
    Returns:
        配置好的日志记录器
    """
    # 确保日志目录存在
    log_dir = ensure_log_directory()
    
    # 获取日志记录器
    logger = logging.getLogger(name or __name__)
    
    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(getattr(logging, level.upper()))
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 创建文件处理器（按日期轮转）
    today = datetime.now().strftime('%Y-%m-%d')
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / f"app_{today}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # 创建错误日志文件处理器
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / f"error_{today}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # 防止日志向上传播
    logger.propagate = False
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器的便捷方法
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器实例
    """
    return setup_logger(name)

# 创建默认的根日志记录器
root_logger = setup_logger("root")

# 导出常用的日志记录器
def get_api_logger() -> logging.Logger:
    """获取API服务的日志记录器"""
    return get_logger("api")

def get_summarizer_logger() -> logging.Logger:
    """获取文档总结器的日志记录器"""
    return get_logger("summarizer")

def get_database_logger() -> logging.Logger:
    """获取数据库操作的日志记录器"""
    return get_logger("database")

def get_utils_logger() -> logging.Logger:
    """获取工具模块的日志记录器"""
    return get_logger("utils") 
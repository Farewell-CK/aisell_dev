#!/usr/bin/env python3
"""
测试统一日志配置的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger_config import get_api_logger, get_summarizer_logger, get_database_logger, get_utils_logger

def test_logging():
    """测试各种日志记录器"""
    print("=== 测试统一日志配置 ===\n")
    
    # 测试API日志记录器
    api_logger = get_api_logger()
    api_logger.info("API服务日志测试 - 信息级别")
    api_logger.warning("API服务日志测试 - 警告级别")
    api_logger.error("API服务日志测试 - 错误级别")
    
    # 测试文档总结器日志记录器
    summarizer_logger = get_summarizer_logger()
    summarizer_logger.info("文档总结器日志测试 - 信息级别")
    summarizer_logger.debug("文档总结器日志测试 - 调试级别")
    summarizer_logger.warning("文档总结器日志测试 - 警告级别")
    
    # 测试数据库日志记录器
    db_logger = get_database_logger()
    db_logger.info("数据库操作日志测试 - 信息级别")
    db_logger.error("数据库操作日志测试 - 错误级别")
    
    # 测试工具模块日志记录器
    utils_logger = get_utils_logger()
    utils_logger.info("工具模块日志测试 - 信息级别")
    utils_logger.warning("工具模块日志测试 - 警告级别")
    
    print("\n=== 日志测试完成 ===")
    print("请检查 logs/ 目录下的日志文件：")
    print("- app_YYYY-MM-DD.log (应用日志)")
    print("- error_YYYY-MM-DD.log (错误日志)")

if __name__ == "__main__":
    test_logging() 
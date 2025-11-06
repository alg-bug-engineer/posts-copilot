"""
日志管理模块
提供统一的日志输出功能，支持控制台和文件输出
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logger(name='blog_publisher', log_level=logging.INFO):
    """
    设置并返回一个logger实例
    
    Args:
        name: logger名称
        log_level: 日志级别
    
    Returns:
        logging.Logger: 配置好的logger实例
    """
    logger = logging.getLogger(name)
    
    # 如果logger已经有handler，说明已经初始化过，直接返回
    if logger.handlers:
        return logger
    
    logger.setLevel(log_level)
    
    # 创建日志目录
    log_dir = Path(__file__).parent.parent.parent / 'data' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成日志文件名（按日期）
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # 定义日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"日志系统初始化完成，日志文件：{log_file}")
    
    return logger


def get_logger(name='blog_publisher'):
    """
    获取已存在的logger实例
    
    Args:
        name: logger名称
    
    Returns:
        logging.Logger: logger实例
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # 如果logger还没有初始化，自动初始化
        return setup_logger(name)
    return logger


# 为方便使用，提供一个默认的logger实例
default_logger = setup_logger()

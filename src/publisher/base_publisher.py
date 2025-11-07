"""
基础发布器抽象类
定义所有平台发布器的通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

from src.core.logger import get_logger
from src.core.session_manager import SessionManager

logger = get_logger(__name__)


class BasePublisher(ABC):
    """
    发布器基类，所有平台的发布器都应继承此类
    """
    
    # 平台名称，子类需要覆盖
    PLATFORM_NAME = "base"
    
    def __init__(self, common_config: Dict[str, Any], platform_config: Dict[str, Any]):
        """
        初始化发布器
        
        Args:
            common_config: 通用配置
            platform_config: 平台特定配置
        """
        self.common_config = common_config
        self.platform_config = platform_config
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # 初始化会话管理器
        self.session_manager = SessionManager(self.PLATFORM_NAME, common_config)
        self.driver = None
        
        self.logger.info(f"初始化 {self.PLATFORM_NAME} 发布器")
    
    def setup_driver(self, use_existing: bool = True):
        """
        设置浏览器驱动
        
        Args:
            use_existing: 是否使用现有的浏览器实例
        """
        self.driver = self.session_manager.create_driver(use_existing=use_existing)
        self.logger.info("浏览器驱动设置完成")
    
    def load_cookies_if_exists(self, site_url: str) -> bool:
        """
        如果存在保存的Cookie，则加载
        
        Args:
            site_url: 网站URL
        
        Returns:
            bool: 是否成功加载Cookie
        """
        return self.session_manager.load_cookies(site_url)
    
    def save_login_state(self, site_url: str):
        """
        保存登录状态（Cookie）
        
        Args:
            site_url: 网站URL
        """
        self.session_manager.save_cookies(site_url)
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """
        获取平台名称
        
        Returns:
            str: 平台名称
        """
        pass
    
    @abstractmethod
    def publish(self, article_path: str) -> bool:
        """
        发布文章到平台
        
        Args:
            article_path: 文章文件路径
        
        Returns:
            bool: 是否发布成功
        """
        pass
    
    def parse_article_metadata(self, article_path: str) -> Dict[str, Any]:
        """
        解析文章的front matter元数据
        
        Args:
            article_path: 文章文件路径
        
        Returns:
            Dict: 文章元数据
        """
        from src.utils.file_utils import parse_front_matter
        
        try:
            metadata = parse_front_matter(article_path)
            self.logger.info(f"成功解析文章元数据：{metadata.keys() if metadata else '无'}")
            return metadata or {}
        except Exception as e:
            self.logger.error(f"解析文章元数据失败：{e}", exc_info=True)
            return {}
    
    def clean_title(self, title: str) -> str:
        """
        清理标题，移除引号等不适合发布的字符
        
        Args:
            title: 原始标题
        
        Returns:
            str: 清理后的标题
        """
        if not title:
            return title
        
        # 移除各种引号
        # 双引号：" " " "
        # 单引号：' ' ' '
        cleaned = title.replace('"', '').replace('"', '').replace('"', '')
        cleaned = cleaned.replace("'", '').replace("'", '').replace("'", '')
        
        # 去除首尾空格
        cleaned = cleaned.strip()
        
        if cleaned != title:
            self.logger.info(f"标题已清理：'{title}' -> '{cleaned}'")
        
        return cleaned
    
    def read_article_content(self, article_path: str, include_footer: bool = True) -> str:
        """
        读取文章内容
        
        Args:
            article_path: 文章文件路径
            include_footer: 是否包含页脚
        
        Returns:
            str: 文章内容
        """
        from src.utils.file_utils import read_file_with_footer, read_file
        
        try:
            if include_footer:
                content = read_file_with_footer(article_path)
            else:
                content = read_file(article_path)
            
            self.logger.info(f"成功读取文章内容，长度：{len(content)}")
            return content
        except Exception as e:
            self.logger.error(f"读取文章内容失败：{e}", exc_info=True)
            return ""
    
    def cleanup(self):
        """
        清理资源
        """
        if self.session_manager:
            self.session_manager.close()
        self.logger.info(f"{self.PLATFORM_NAME} 发布器资源已清理")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()

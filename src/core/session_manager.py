"""
会话管理模块
负责管理浏览器会话、Cookie的保存和加载
"""

import os
import json
import pickle
import time
from pathlib import Path
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from .logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """
    会话管理器，负责：
    1. 浏览器驱动的创建和配置
    2. Cookie的保存和恢复
    3. 登录状态的维护
    """
    
    def __init__(self, platform: str, config: Dict[str, Any]):
        """
        初始化会话管理器
        
        Args:
            platform: 平台名称（如 'csdn', 'juejin' 等）
            config: 配置字典
        """
        self.platform = platform
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        
        # Cookie存储路径
        cookie_dir = Path(__file__).parent.parent.parent / 'data' / 'cookies'
        cookie_dir.mkdir(parents=True, exist_ok=True)
        self.cookie_file = cookie_dir / f"{platform}_cookies.pkl"
        
        # 浏览器运行模式配置
        self.background_mode = config.get('background_mode', True)  # 默认后台模式
        self.headless_mode = config.get('headless_mode', False)  # 新无头模式（可选）
        
        logger.info(f"初始化 {platform} 会话管理器，Cookie文件：{self.cookie_file}")
        if self.headless_mode:
            logger.info("浏览器模式: New Headless 模式（完全后台，无界面干扰）")
        elif self.background_mode:
            logger.info("浏览器模式: 后台模式（有界面但不切换）")
        else:
            logger.info("浏览器模式: 正常模式")
    
    def create_driver(self, use_existing: bool = True) -> webdriver.Chrome:
        """
        创建Chrome驱动实例
        
        Args:
            use_existing: 是否使用已存在的Chrome实例（调试模式）
        
        Returns:
            webdriver.Chrome: Chrome驱动实例
        """
        logger.info(f"正在创建Chrome驱动实例（use_existing={use_existing}）...")
        
        driver_type = self.config.get('driver_type', 'chrome')
        
        if driver_type == 'chrome':
            service = ChromeService(self.config.get('service_location'))
            options = ChromeOptions()
            options.page_load_strategy = 'normal'
            
            # # New Headless 模式配置（优先级最高）
            # if self.headless_mode and not use_existing:
            #     logger.info("启用 New Headless 模式")
            #     options.add_argument('--headless=new')
            #     options.add_argument('--disable-gpu')
            #     options.add_argument('--no-sandbox')
            #     options.add_argument('--disable-dev-shm-usage')
            #     options.add_argument('--disable-popup-blocking')
            #     options.add_argument('--disable-notifications')
            #     options.add_argument('--window-size=1920,1080')
            
            if use_existing:
                # 使用已存在的Chrome实例
                debugger_address = self.config.get('debugger_address')
                if debugger_address:
                    # 连接到现有实例时，只需要设置 debuggerAddress
                    # 不要添加其他选项，因为实例已经启动了
                    options.add_experimental_option('debuggerAddress', debugger_address)
                    logger.info(f"连接到现有Chrome实例：{debugger_address}")
                    
                    if self.background_mode:
                        logger.info("后台模式已启用（注意：连接现有实例时，需要在启动Chrome时配置后台选项）")
                    
                    # 增加连接超时时间
                    import socket
                    # 测试端口是否可访问
                    host, port = debugger_address.split(':')
                    port = int(port)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    try:
                        result = sock.connect_ex((host, port))
                        if result != 0:
                            logger.error(f"Chrome调试端口 {debugger_address} 无法连接")
                            raise ConnectionError(f"Chrome调试端口 {debugger_address} 无法连接")
                        logger.info(f"Chrome调试端口 {debugger_address} 连接正常")
                    finally:
                        sock.close()
            else:
                # 创建新的Chrome实例
                options.add_argument('--start-maximized')
                options.add_argument('--disable-blink-features=AutomationControlled')
                
                # # 后台模式配置
                # if self.background_mode:
                #     logger.info("启用后台模式配置（新实例）")
                #     options.add_argument('--disable-popup-blocking')
                #     options.add_argument('--disable-notifications')
                #     options.add_experimental_option('excludeSwitches', ['enable-automation'])
                #     options.add_experimental_option('useAutomationExtension', False)
                
                logger.info("创建新的Chrome实例")
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome驱动创建成功")
            return self.driver
        else:
            logger.error(f"不支持的驱动类型：{driver_type}")
            raise ValueError(f"不支持的驱动类型：{driver_type}")
    
    def save_cookies(self, url: Optional[str] = None, force_save: bool = False):
        """
        保存当前会话的Cookies
        
        Args:
            url: 需要访问的URL（用于设置Cookie的域）
            force_save: 是否强制保存（即使没有变化）
        """
        if not self.driver:
            logger.warning("驱动未初始化，无法保存Cookie")
            return
        
        try:
            # 如果提供了URL，先访问该页面
            if url:
                current_url = self.driver.current_url
                if not current_url.startswith(url):
                    logger.info(f"访问URL以获取Cookie：{url}")
                    self.driver.get(url)
                    time.sleep(2)
            
            cookies = self.driver.get_cookies()
            
            # 检查是否有变化（除非强制保存）
            if not force_save and self.cookie_file.exists():
                try:
                    with open(self.cookie_file, 'rb') as f:
                        old_cookies = pickle.load(f)
                    
                    # 简单比较cookies数量和内容
                    if len(cookies) == len(old_cookies):
                        # 比较关键cookie的值
                        cookies_dict = {c['name']: c.get('value', '') for c in cookies}
                        old_cookies_dict = {c['name']: c.get('value', '') for c in old_cookies}
                        
                        if cookies_dict == old_cookies_dict:
                            logger.debug(f"Cookie无变化，跳过保存：{self.cookie_file}")
                            return
                except Exception as e:
                    logger.warning(f"比较Cookie时出错，强制保存：{e}")
            
            # 保存cookies到文件
            with open(self.cookie_file, 'wb') as f:
                pickle.dump(cookies, f)
            
            logger.info(f"成功保存 {len(cookies)} 个Cookie到：{self.cookie_file}")
            
        except Exception as e:
            logger.error(f"保存Cookie失败：{e}", exc_info=True)
    
    def load_cookies(self, url: str) -> bool:
        """
        加载保存的Cookies
        
        Args:
            url: 需要访问的URL（用于设置Cookie的域）
        
        Returns:
            bool: 是否成功加载Cookie
        """
        if not self.driver:
            logger.warning("驱动未初始化，无法加载Cookie")
            return False
        
        if not self.cookie_file.exists():
            logger.info(f"Cookie文件不存在：{self.cookie_file}")
            return False
        
        try:
            # 先访问目标网站（如果当前不在该网站）
            from urllib.parse import urlparse
            target_domain = urlparse(url).netloc
            
            # 检查当前URL，避免重复访问
            current_url = self.driver.current_url
            if 'about:blank' in current_url or target_domain not in current_url:
                logger.info(f"访问目标网站：{url}")
                self.driver.get(url)
                time.sleep(2)
            else:
                logger.info(f"已在目标网站，跳过访问")
            
            # 获取当前域名
            current_domain = urlparse(self.driver.current_url).netloc
            logger.info(f"当前域名：{current_domain}")
            
            # 加载cookies
            with open(self.cookie_file, 'rb') as f:
                cookies = pickle.load(f)
            
            # 添加cookies到浏览器
            added_count = 0
            skipped_count = 0
            for cookie in cookies:
                try:
                    # 移除一些可能导致问题的字段
                    cookie.pop('expiry', None)
                    cookie.pop('sameSite', None)
                    
                    # 检查cookie的域名是否与当前域名匹配
                    cookie_domain = cookie.get('domain', '')
                    # 移除域名前的点号
                    cookie_domain_clean = cookie_domain.lstrip('.')
                    
                    # 只添加域名匹配的cookie
                    if cookie_domain_clean in current_domain or current_domain in cookie_domain_clean:
                        self.driver.add_cookie(cookie)
                        added_count += 1
                    else:
                        logger.debug(f"跳过Cookie '{cookie.get('name')}'：域名不匹配 ({cookie_domain} vs {current_domain})")
                        skipped_count += 1
                        
                except Exception as e:
                    logger.warning(f"添加Cookie失败：{cookie.get('name')}, 错误：{e}")
                    skipped_count += 1
            
            logger.info(f"成功加载 {added_count} 个Cookie，跳过 {skipped_count} 个")
            
            # 刷新页面以应用cookies
            logger.info("刷新页面以应用Cookie...")
            self.driver.refresh()
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"加载Cookie失败：{e}", exc_info=True)
            return False
    
    def update_cookies(self, url: Optional[str] = None):
        """
        更新cookies - 获取浏览器中的最新cookies并保存
        用于在操作过程中保持cookies同步
        
        Args:
            url: 需要访问的URL（用于设置Cookie的域）
        """
        if not self.driver:
            logger.warning("驱动未初始化，无法更新Cookie")
            return
        
        try:
            current_cookies = self.driver.get_cookies()
            if current_cookies:
                # 强制保存最新的cookies
                self.save_cookies(url, force_save=True)
                logger.debug(f"已更新 {len(current_cookies)} 个Cookie")
            else:
                logger.warning("浏览器中没有Cookie可更新")
        except Exception as e:
            logger.error(f"更新Cookie失败：{e}", exc_info=True)
    
    def clear_cookies(self):
        """清除保存的Cookie文件"""
        if self.cookie_file.exists():
            self.cookie_file.unlink()
            logger.info(f"已删除Cookie文件：{self.cookie_file}")
        else:
            logger.info("Cookie文件不存在，无需删除")
    
    def is_logged_in(self, check_element: tuple) -> bool:
        """
        检查是否已登录
        
        Args:
            check_element: 用于检查登录状态的元素定位符 (By, locator)
        
        Returns:
            bool: 是否已登录
        """
        if not self.driver:
            return False
        
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(check_element)
            )
            logger.info("检测到登录状态")
            return True
        except:
            logger.info("未检测到登录状态")
            return False
    
    def close(self):
        """关闭浏览器会话"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("浏览器会话已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器失败：{e}", exc_info=True)
            finally:
                self.driver = None

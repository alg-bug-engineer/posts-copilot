"""
知乎 发布器
用于自动发布文章到知乎平台
"""

import sys
import time
import pyperclip
from typing import Dict, Any
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.publisher.base_publisher import BasePublisher
from src.publisher.common_handler import wait_login, safe_click, safe_input, switch_to_new_tab
from src.core.logger import get_logger
from src.utils.file_utils import read_file_with_footer, parse_front_matter, download_image, convert_md_to_html
from src.utils.selenium_utils import get_html_web_content
from src.utils.yaml_file_utils import read_zhihu, read_common

logger = get_logger(__name__)


class ZhihuPublisher(BasePublisher):
    """知乎发布器"""
    
    PLATFORM_NAME = "zhihu"
    
    def __init__(self, common_config: Dict[str, Any] = None, platform_config: Dict[str, Any] = None):
        """
        初始化知乎发布器
        
        Args:
            common_config: 通用配置
            platform_config: 知乎平台配置
        """
        # 如果没有传入配置，从文件读取
        if common_config is None:
            common_config = read_common()
        if platform_config is None:
            platform_config = read_zhihu()
        
        super().__init__(common_config, platform_config)
        
        self.site_url = platform_config.get('site', 'https://zhuanlan.zhihu.com/write')
        self.auto_publish = platform_config.get('auto_publish', False) or common_config.get('auto_publish', False)
        self.use_column = platform_config.get('use_column', True)
        self.submit_to_question = platform_config.get('submit_to_question', False)
        self.topics = platform_config.get('topics', [])
        
        logger.info(f"知乎发布器初始化完成，站点：{self.site_url}")
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return self.PLATFORM_NAME
    
    def _check_login_status(self) -> bool:
        """
        检查是否已登录
        
        Returns:
            bool: 是否已登录
        """
        try:
            # 检查是否存在标题输入框（已登录的标志）
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//textarea[contains(@placeholder, "请输入标题")]'))
            )
            logger.info("✓ 检测到已登录状态")
            return True
        except:
            logger.info("⚠ 未检测到登录状态")
            return False
    
    def _wait_for_login(self, timeout: int = 300) -> bool:
        """
        等待用户登录
        
        Args:
            timeout: 超时时间（秒）
        
        Returns:
            bool: 是否登录成功
        """
        logger.info(f"等待用户登录（超时时间：{timeout}秒）...")
        logger.info("请在浏览器中完成登录操作")
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, '//textarea[contains(@placeholder, "请输入标题")]'))
            )
            logger.info("✓ 登录成功")
            return True
        except Exception as e:
            logger.error(f"✗ 等待登录超时：{e}")
            return False
    
    def _fill_title(self, front_matter: Dict[str, Any]) -> bool:
        """
        填写文章标题
        
        Args:
            front_matter: 文章元数据
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在填写标题...")
            title_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//textarea[contains(@placeholder, "请输入标题")]'))
            )
            
            title = front_matter.get('title', self.common_config.get('title', ''))
            if not title:
                logger.warning("未找到标题，使用默认值")
                title = "未命名文章"
            
            title_element.clear()
            title_element.send_keys(title)
            logger.info(f"✓ 标题已填写：{title}")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"✗ 填写标题失败：{e}", exc_info=True)
            return False
    
    def _fill_content(self, article_path: str) -> bool:
        """
        填写文章内容
        
        Args:
            article_path: 文章路径
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在填写文章内容...")
            
            # 转换 Markdown 到 HTML（注意：知乎不能识别某些代码块格式）
            content_file_html = convert_md_to_html(article_path)
            logger.info(f"已转换文章为HTML格式：{content_file_html}")
            
            # 通过辅助页面获取HTML内容到剪贴板
            get_html_web_content(self.driver, content_file_html)
            time.sleep(2)
            
            # 切换回知乎编辑页面
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(1)
            
            # 点击内容编辑区域
            content_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    '//div[@class="DraftEditor-editorContainer"]//div[@class="public-DraftStyleDefault-block public-DraftStyleDefault-ltr"]'
                ))
            )
            content_element.click()
            time.sleep(2)
            
            # 执行粘贴操作（使用 Command/Ctrl + V）
            cmd_ctrl = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL
            action_chains = ActionChains(self.driver)
            action_chains.key_down(cmd_ctrl).send_keys('v').key_up(cmd_ctrl).perform()
            
            logger.info("✓ 内容已粘贴，等待处理...")
            time.sleep(3)
            
            return True
        except Exception as e:
            logger.error(f"✗ 填写内容失败：{e}", exc_info=True)
            return False
    
    def _add_cover_image(self, front_matter: Dict[str, Any]) -> bool:
        """
        添加封面图片
        
        Args:
            front_matter: 文章元数据
        
        Returns:
            bool: 是否成功
        """
        try:
            if 'image' not in front_matter or not front_matter['image']:
                logger.info("未设置封面图片，跳过")
                return True
            
            logger.info("正在添加封面图片...")
            
            # 滚动页面，确保上传按钮可见
            ActionChains(self.driver).scroll_by_amount(0, 800).perform()
            time.sleep(1)
            
            # 查找文件上传输入框
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file' and @class='UploadPicture-input']"))
            )
            
            # 下载远程图片到本地
            local_image_path = download_image(front_matter['image'])
            logger.info(f"已下载封面图片：{local_image_path}")
            
            # 上传图片
            file_input.send_keys(local_image_path)
            logger.info("✓ 封面图片已上传")
            time.sleep(2)
            
            return True
        except Exception as e:
            logger.error(f"✗ 添加封面图片失败：{e}", exc_info=True)
            return False
    
    def _set_column(self) -> bool:
        """
        设置专栏收录
        
        Returns:
            bool: 是否成功
        """
        try:
            if not self.use_column:
                logger.info("未启用专栏收录，跳过")
                return True
            
            logger.info("正在设置专栏收录...")
            
            # 点击专栏收录标签
            publish_panel = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//label[@for="PublishPanel-columnLabel-1"]'))
            )
            ActionChains(self.driver).click(publish_panel).perform()
            
            logger.info("✓ 已选择专栏收录")
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"✗ 设置专栏收录失败：{e}", exc_info=True)
            return False
    
    def _publish_article(self) -> bool:
        """
        发布文章
        
        Returns:
            bool: 是否成功
        """
        try:
            if not self.auto_publish:
                logger.info("⚠ 自动发布未启用，文章将保存为草稿")
                logger.info("请手动检查并发布文章")
                time.sleep(5)
                return True
            
            logger.info("正在发布文章...")
            
            # 点击发布按钮
            publish_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "发布")]'))
            )
            publish_button.click()
            
            logger.info("✓ 文章发布成功")
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"✗ 发布文章失败：{e}", exc_info=True)
            return False
    
    def publish(self, article_path: str) -> bool:
        """
        发布文章到知乎
        
        Args:
            article_path: 文章文件路径
        
        Returns:
            bool: 是否发布成功
        """
        logger.info(f"=" * 60)
        logger.info(f"开始发布文章到知乎：{article_path}")
        logger.info(f"=" * 60)
        
        try:
            # 1. 设置驱动
            if not self.driver:
                self.setup_driver(use_existing=True)
            
            # 2. 打开新标签页
            switch_to_new_tab(self.driver, self.site_url)
            
            # 3. 尝试加载Cookie
            cookie_loaded = self.load_cookies_if_exists(self.site_url)
            if cookie_loaded:
                logger.info("✓ 成功加载已保存的登录状态")
                # 刷新页面以应用cookie
                self.driver.refresh()
                time.sleep(3)
            else:
                logger.info("⚠ 未找到保存的登录状态，需要手动登录")
            
            # 4. 等待登录（如果需要）
            if not self._check_login_status():
                logger.info("检测到未登录，等待用户登录...")
                if not self._wait_for_login():
                    logger.error("✗ 登录超时或失败")
                    return False
                
                # 登录成功后保存Cookie
                logger.info("✓ 登录成功，保存登录状态...")
                self.save_login_state(self.site_url)
            
            # 5. 解析文章元数据
            front_matter = self.parse_article_metadata(article_path)
            
            # 6. 填写标题
            if not self._fill_title(front_matter):
                logger.error("✗ 填写标题失败")
                return False
            
            # 7. 填写内容
            if not self._fill_content(article_path):
                logger.error("✗ 填写内容失败")
                return False
            
            # # 8. 添加封面图片
            # if not self._add_cover_image(front_matter):
            #     logger.warning("⚠ 添加封面图片失败，继续...")
            
            # # 9. 设置专栏收录
            # if not self._set_column():
            #     logger.warning("⚠ 设置专栏收录失败，继续...")
            
            # 10. 发布文章
            if not self._publish_article():
                logger.error("✗ 发布文章失败")
                return False
            
            logger.info("=" * 60)
            logger.info("✓ 文章发布成功！")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"✗ 发布过程中出现错误：{e}", exc_info=True)
            return False

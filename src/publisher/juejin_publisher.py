"""
掘金 发布器
用于自动发布文章到掘金平台
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
from src.utils.file_utils import read_file_with_footer, parse_front_matter, download_image
from src.utils.yaml_file_utils import read_juejin, read_common

logger = get_logger(__name__)


class JuejinPublisher(BasePublisher):
    """掘金发布器"""
    
    PLATFORM_NAME = "juejin"
    
    def __init__(self, common_config: Dict[str, Any] = None, platform_config: Dict[str, Any] = None):
        """
        初始化掘金发布器
        
        Args:
            common_config: 通用配置
            platform_config: 掘金平台配置
        """
        # 如果没有传入配置，从文件读取
        if common_config is None:
            common_config = read_common()
        if platform_config is None:
            platform_config = read_juejin()
        
        super().__init__(common_config, platform_config)
        
        self.site_url = platform_config.get('site', 'https://juejin.cn/creator/home')
        self.auto_publish = common_config.get('auto_publish', False)
        
        logger.info(f"掘金发布器初始化完成，站点：{self.site_url}")
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return self.PLATFORM_NAME
    
    def publish(self, article_path: str) -> bool:
        """
        发布文章到掘金
        
        Args:
            article_path: 文章文件路径
        
        Returns:
            bool: 是否发布成功
        """
        logger.info(f"=" * 60)
        logger.info(f"开始发布文章到掘金：{article_path}")
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
            
            # 6. 点击"写文章"按钮
            if not self._click_write_button():
                logger.error("✗ 无法点击写文章按钮")
                return False
            
            # 7. 切换到编辑器标签页
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(2)
            
            # 8. 等待编辑器加载
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="输入文章标题..."]')))
            logger.info("✓ 编辑器加载完成")
            
            # 9. 填充文章内容
            if not self._fill_article_content(article_path):
                logger.error("✗ 填充文章内容失败")
                return False
            
            # 10. 填充文章标题
            if not self._fill_article_title(front_matter):
                logger.error("✗ 填充文章标题失败")
                return False
            
            # 11. 点击发布按钮
            if not self._click_publish_button():
                logger.error("✗ 无法点击发布按钮")
                return False
            
            # 12. 填充发布设置
            if not self._fill_publish_settings(front_matter):
                logger.error("✗ 填充发布设置失败")
                return False
            
            # 13. 确认发布
            if self.auto_publish:
                if not self._confirm_publish():
                    logger.error("✗ 确认发布失败")
                    return False
                logger.info("✓ 文章发布成功！")
            else:
                logger.info("✓ 文章已准备好，等待手动确认发布")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ 发布过程中发生错误：{e}", exc_info=True)
            return False
    
    def _check_login_status(self) -> bool:
        """
        检查是否已登录
        
        Returns:
            bool: 是否已登录
        """
        try:
            # 检查是否存在"写文章"按钮
            self.driver.find_element(By.CLASS_NAME, 'send-button')
            logger.info("✓ 已登录掘金")
            return True
        except:
            logger.info("⚠ 未登录掘金")
            return False
    
    def _wait_for_login(self, timeout: int = 300) -> bool:
        """
        等待用户手动登录
        
        Args:
            timeout: 超时时间（秒）
        
        Returns:
            bool: 是否登录成功
        """
        wait_time = self.common_config.get('wait_login_time', timeout)
        logger.info(f"等待用户登录，超时时间：{wait_time}秒")
        logger.info("请在浏览器中完成登录操作...")
        
        # 使用轮询方式检测登录状态
        start_time = time.time()
        check_interval = 2  # 每2秒检查一次
        
        while (time.time() - start_time) < wait_time:
            try:
                # 尝试刷新页面
                if (time.time() - start_time) % 10 < check_interval:
                    self.driver.refresh()
                    time.sleep(2)
                
                # 检查是否存在"写文章"按钮
                write_btn = self.driver.find_element(By.CLASS_NAME, 'send-button')
                if write_btn:
                    logger.info("✓ 检测到登录成功！")
                    return True
            except:
                # 继续等待
                pass
            
            time.sleep(check_interval)
        
        logger.error(f"✗ 等待登录超时（{wait_time}秒）")
        return False
    
    def _click_write_button(self) -> bool:
        """
        点击"写文章"按钮
        
        Returns:
            bool: 是否成功
        """
        try:
            wait = WebDriverWait(self.driver, 10)
            write_btn = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'send-button'))
            )
            write_btn.click()
            logger.info("✓ 已点击写文章按钮")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"✗ 点击写文章按钮失败：{e}")
            return False
    
    def _fill_article_content(self, article_path: str) -> bool:
        """
        填充文章内容
        
        Args:
            article_path: 文章路径
        
        Returns:
            bool: 是否成功
        """
        try:
            # 读取文章内容
            file_content = read_file_with_footer(article_path)
            logger.info(f"✓ 读取文章内容，长度：{len(file_content)}")
            
            # 掘金使用复制粘贴的方式填充内容
            cmd_ctrl = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL
            
            # 将内容复制到剪贴板
            pyperclip.copy(file_content)
            
            # 定位到编辑器
            content_element = self.driver.find_element(
                By.XPATH, 
                '//div[@class="CodeMirror-code"]//span[@role="presentation"]'
            )
            content_element.click()
            time.sleep(1)
            
            # 执行粘贴操作
            action_chains = ActionChains(self.driver)
            action_chains.key_down(cmd_ctrl).send_keys('v').key_up(cmd_ctrl).perform()
            
            logger.info("✓ 已粘贴文章内容，等待图片解析...")
            time.sleep(15)  # 等待图片解析
            
            return True
        except Exception as e:
            logger.error(f"✗ 填充文章内容失败：{e}")
            return False
    
    def _fill_article_title(self, front_matter: Dict[str, Any]) -> bool:
        """
        填充文章标题
        
        Args:
            front_matter: 文章元数据
        
        Returns:
            bool: 是否成功
        """
        try:
            title_input = self.driver.find_element(
                By.XPATH, 
                '//input[@placeholder="输入文章标题..."]'
            )
            title_input.clear()
            
            # 优先使用front matter中的标题
            if 'title' in front_matter and front_matter['title']:
                title = front_matter['title']
            else:
                title = self.common_config.get('title', '未命名文章')
            
            title_input.send_keys(title)
            logger.info(f"✓ 已填充文章标题：{title}")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"✗ 填充文章标题失败：{e}")
            return False
    
    def _click_publish_button(self) -> bool:
        """
        点击发布按钮
        
        Returns:
            bool: 是否成功
        """
        try:
            publish_button = self.driver.find_element(
                By.XPATH, 
                '//button[contains(text(), "发布")]'
            )
            publish_button.click()
            logger.info("✓ 已点击发布按钮")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"✗ 点击发布按钮失败：{e}")
            return False
    
    def _fill_publish_settings(self, front_matter: Dict[str, Any]) -> bool:
        """
        填充发布设置
        
        Args:
            front_matter: 文章元数据
        
        Returns:
            bool: 是否成功
        """
        try:
            # 等待发布弹窗出现
            wait = WebDriverWait(self.driver, 10)
            title_label = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[contains(@class,"title") and contains(text(), "发布文章")]')
                )
            )
            logger.info("✓ 发布设置弹窗已显示")
            
            # 1. 选择分类
            self._select_category()
            
            # 2. 添加标签
            self._add_tags()
            
            # # 3. 上传封面图
            # self._upload_cover_image(front_matter)
            
            # 4. 收录至专栏
            self._add_to_collections()
            
            # # 5. 添加创作话题
            # self._add_topic()
            
            # # 6. 编辑摘要
            # self._fill_summary(front_matter)
            
            logger.info("✓ 发布设置填充完成")
            return True
        except Exception as e:
            logger.error(f"✗ 填充发布设置失败：{e}")
            return False
    
    def _select_category(self) -> bool:
        """选择文章分类"""
        try:
            category = self.platform_config.get('category')
            if not category:
                logger.info("⚠ 未配置分类，跳过")
                return True
            
            category_btn = self.driver.find_element(
                By.XPATH, 
                f'//div[@class="form-item-content category-list"]//div[contains(text(), "{category}")]'
            )
            category_btn.click()
            logger.info(f"✓ 已选择分类：{category}")
            time.sleep(1)
            return True
        except Exception as e:
            logger.warning(f"⚠ 选择分类失败：{e}")
            return True  # 非关键步骤，失败也继续
    
    def _add_tags(self) -> bool:
        """添加文章标签"""
        try:
            tags = self.platform_config.get('tags', [])
            if not tags:
                logger.info("⚠ 未配置标签，跳过")
                return True
            
            cmd_ctrl = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL
            
            # 点击标签输入框
            tag_btn = self.driver.find_element(
                By.XPATH, 
                '//div[contains(@class,"byte-select__placeholder") and contains(text(), "请搜索添加标签")]'
            )
            tag_btn.click()
            time.sleep(1)
            
            # 逐个添加标签
            for tag in tags:
                try:
                    # 使用复制粘贴的方式输入标签
                    pyperclip.copy(tag)
                    action_chains = ActionChains(self.driver)
                    action_chains.key_down(cmd_ctrl).send_keys('v').key_up(cmd_ctrl).perform()
                    time.sleep(1)
                    
                    # 从下拉框中选择对应的标签
                    tag_element = self.driver.find_element(
                        By.XPATH, 
                        f'//li[contains(@class,"byte-select-option") and contains(text(), "{tag}")]'
                    )
                    tag_element.click()
                    logger.info(f"✓ 已添加标签：{tag}")
                    time.sleep(1)
                except Exception as e:
                    logger.warning(f"⚠ 添加标签 {tag} 失败：{e}")
            
            # 点击其他位置关闭下拉框
            title_label = self.driver.find_element(
                By.XPATH, 
                '//div[contains(@class,"title") and contains(text(), "发布文章")]'
            )
            title_label.click()
            
            return True
        except Exception as e:
            logger.warning(f"⚠ 添加标签失败：{e}")
            return True  # 非关键步骤
    
    def _upload_cover_image(self, front_matter: Dict[str, Any]) -> bool:
        """上传封面图"""
        try:
            if 'image' not in front_matter or not front_matter['image']:
                logger.info("⚠ 未配置封面图，跳过")
                return True
            
            file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
            
            # 下载图片到本地
            image_path = download_image(front_matter['image'])
            file_input.send_keys(image_path)
            
            logger.info(f"✓ 已上传封面图：{front_matter['image']}")
            time.sleep(2)
            return True
        except Exception as e:
            logger.warning(f"⚠ 上传封面图失败：{e}")
            return True  # 非关键步骤
    
    def _add_to_collections(self) -> bool:
        """收录至专栏"""
        try:
            collections = self.platform_config.get('collections', [])
            if not collections:
                logger.info("⚠ 未配置专栏，跳过")
                return True
            
            cmd_ctrl = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL
            
            # 点击专栏输入框
            collection_button = self.driver.find_element(
                By.XPATH, 
                '//div[contains(@class,"byte-select__placeholder") and contains(text(), "请搜索添加专栏，同一篇文章最多添加三个专栏")]'
            )
            collection_button.click()
            time.sleep(1)
            
            # 逐个添加专栏
            for coll in collections:
                try:
                    # 使用复制粘贴的方式输入专栏名
                    pyperclip.copy(coll)
                    action_chains = ActionChains(self.driver)
                    action_chains.key_down(cmd_ctrl).send_keys('v').key_up(cmd_ctrl).perform()
                    time.sleep(1)
                    
                    # 从下拉框中选择对应的专栏
                    coll_element = self.driver.find_element(
                        By.XPATH, 
                        f'//li[contains(@class,"byte-select-option") and contains(text(), "{coll}")]'
                    )
                    coll_element.click()
                    logger.info(f"✓ 已添加到专栏：{coll}")
                    time.sleep(1)
                except Exception as e:
                    logger.warning(f"⚠ 添加专栏 {coll} 失败：{e}")
            
            # 点击其他位置关闭下拉框
            title_label = self.driver.find_element(
                By.XPATH, 
                '//div[contains(@class,"title") and contains(text(), "发布文章")]'
            )
            title_label.click()
            
            return True
        except Exception as e:
            logger.warning(f"⚠ 添加专栏失败：{e}")
            return True  # 非关键步骤
    
    def _add_topic(self) -> bool:
        """添加创作话题"""
        try:
            topic = self.platform_config.get('topic')
            if not topic:
                logger.info("⚠ 未配置创作话题，跳过")
                return True
            
            cmd_ctrl = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL
            
            # 点击话题输入框
            topic_btn = self.driver.find_element(
                By.XPATH, 
                '//div[contains(@class,"byte-select__placeholder") and contains(text(), "请搜索添加话题，最多添加1个话题")]'
            )
            topic_btn.click()
            time.sleep(1)
            
            # 使用复制粘贴的方式输入话题
            pyperclip.copy(topic)
            action_chains = ActionChains(self.driver)
            action_chains.key_down(cmd_ctrl).send_keys('v').key_up(cmd_ctrl).perform()
            time.sleep(1)
            
            # 从下拉框中选择对应的话题
            topic_element = self.driver.find_element(
                By.XPATH, 
                f'//li[@class="byte-select-option"]//span[contains(text(), "{topic}")]'
            )
            topic_element.click()
            logger.info(f"✓ 已添加创作话题：{topic}")
            time.sleep(1)
            
            # 点击其他位置关闭下拉框
            title_label = self.driver.find_element(
                By.XPATH, 
                '//div[contains(@class,"title") and contains(text(), "发布文章")]'
            )
            title_label.click()
            
            return True
        except Exception as e:
            logger.warning(f"⚠ 添加创作话题失败：{e}")
            return True  # 非关键步骤
    
    def _fill_summary(self, front_matter: Dict[str, Any]) -> bool:
        """编辑摘要"""
        try:
            # 优先使用front matter中的描述
            if 'description' in front_matter and front_matter['description']:
                summary = front_matter['description']
            else:
                summary = self.common_config.get('summary')
            
            if not summary:
                logger.info("⚠ 未配置摘要，跳过")
                return True
            
            summary_textarea = self.driver.find_element(
                By.XPATH, 
                '//textarea[@class="byte-input__textarea"]'
            )
            summary_textarea.clear()
            summary_textarea.send_keys(summary)
            
            logger.info(f"✓ 已填充摘要")
            time.sleep(2)
            return True
        except Exception as e:
            logger.warning(f"⚠ 填充摘要失败：{e}")
            return True  # 非关键步骤
    
    def _confirm_publish(self) -> bool:
        """确认并发布"""
        try:
            publish_button = self.driver.find_element(
                By.XPATH, 
                '//button[contains(text(), "确定并发布")]'
            )
            publish_button.click()
            logger.info("✓ 已点击确定并发布")
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"✗ 确认发布失败：{e}")
            return False

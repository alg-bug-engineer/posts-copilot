"""
今日头条发布器
用于自动发布文章到今日头条平台
"""

import sys
import time
from typing import Dict, Any
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.publisher.base_publisher import BasePublisher
from src.publisher.common_handler import wait_login
from src.core.logger import get_logger
from src.utils.file_utils import convert_md_to_html
from src.utils.selenium_utils import get_html_web_content
from src.utils.yaml_file_utils import read_toutiao, read_common

logger = get_logger(__name__)


class ToutiaoPublisher(BasePublisher):
    """今日头条发布器"""
    
    PLATFORM_NAME = "toutiao"
    
    def __init__(self, common_config: Dict[str, Any] = None, platform_config: Dict[str, Any] = None):
        """
        初始化今日头条发布器
        
        Args:
            common_config: 通用配置
            platform_config: 头条平台配置
        """
        # 如果没有传入配置，从文件读取
        if common_config is None:
            common_config = read_common()
        if platform_config is None:
            platform_config = read_toutiao()
        
        super().__init__(common_config, platform_config)
        
        self.site_url = platform_config.get('site', 'https://mp.toutiao.com/profile_v4/graphic/publish')
        self.auto_publish = common_config.get('auto_publish', False)
        
        logger.info(f"今日头条发布器初始化完成，站点：{self.site_url}")
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return self.PLATFORM_NAME
    
    def publish(self, article_path: str) -> bool:
        """
        发布文章到今日头条
        
        Args:
            article_path: 文章文件路径
        
        Returns:
            bool: 是否发布成功
        """
        logger.info(f"=" * 60)
        logger.info(f"开始发布文章到今日头条：{article_path}")
        logger.info(f"=" * 60)
        
        try:
            # 1. 设置驱动
            if not self.driver:
                self.setup_driver(use_existing=True)
            
            # 2. 打开新标签页（但不立即访问URL）
            self.driver.switch_to.new_window('tab')
            logger.info("✓ 已切换到新标签页")
            
            # 3. 尝试加载Cookie（这会访问URL）
            cookie_loaded = self.load_cookies_if_exists(self.site_url)
            if cookie_loaded:
                logger.info("✓ 成功加载已保存的登录状态")
                # load_cookies内部已经刷新过了，不需要再刷新
            else:
                logger.info("⚠ 未找到保存的登录状态，需要手动登录")
                # 如果没有Cookie，手动访问URL
                self.driver.get(self.site_url)
                time.sleep(2)
            
            # 4. 等待登录（如果需要）
            if not self._check_login_status():
                logger.info("检测到未登录，等待用户登录...")
                if not self._wait_for_login():
                    logger.error("✗ 登录超时或失败")
                    return False
                
                # 登录成功后保存Cookie
                logger.info("✓ 登录成功，保存登录状态...")
                self.save_login_state(self.site_url)
            else:
                # 如果已经登录，更新cookies以保持同步
                logger.debug("已登录状态，更新cookies...")
                self.update_cookies(self.site_url)
            
            # 5. 解析文章元数据
            front_matter = self.parse_article_metadata(article_path)
            
            # 6. 填充文章标题
            if not self._fill_title(front_matter):
                logger.error("✗ 填充标题失败")
                return False
            
            # 7. 填充文章内容
            if not self._fill_content(article_path):
                logger.error("✗ 填充内容失败")
                return False
            
            # 8. 点击编辑器空白位置获取焦点（重要！）
            if not self._click_editor_blank_area():
                logger.warning("⚠ 点击编辑器空白位置失败，继续执行")
            
            # 9. 点击下方表单区域（触发页面更新）
            if not self._click_form_area():
                logger.warning("⚠ 点击表单区域失败，继续执行")
            
            # 10. 选择无封面
            if not self._select_no_cover():
                logger.warning("⚠ 选择无封面失败，继续执行")
            
            # 13. 最终发布
            if self.auto_publish:
                if not self._final_publish():
                    logger.error("✗ 最终发布失败")
                    return False
                logger.info("✓ 文章发布成功！")
                
                # 发布成功后更新cookies
                logger.debug("发布成功，更新cookies...")
                self.update_cookies(self.site_url)
            else:
                logger.info("⚠ 未启用自动发布，请手动点击发布按钮")
            
            logger.info(f"=" * 60)
            logger.info("今日头条文章发布流程完成")
            logger.info(f"=" * 60)
            
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
            # 检查是否存在标题输入框（登录后才会出现）
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="publish-editor-title-inner"]//textarea[contains(@placeholder,"请输入文章标题")]'))
            )
            logger.info("✓ 检测到已登录状态")
            return True
        except:
            logger.info("⚠ 未检测到登录状态")
            return False
    
    def _wait_for_login(self) -> bool:
        """
        等待用户登录
        
        Returns:
            bool: 是否成功登录
        """
        wait_time = self.common_config.get('wait_login_time', 120)
        return wait_login(
            self.driver,
            By.XPATH,
            '//div[@class="publish-editor-title-inner"]//textarea[contains(@placeholder,"请输入文章标题")]',
            timeout=wait_time
        )
    
    def _fill_title(self, front_matter: Dict[str, Any]) -> bool:
        """
        填充文章标题
        
        Args:
            front_matter: 文章元数据
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在填充文章标题...")
            
            title_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="publish-editor-title-inner"]//textarea[contains(@placeholder,"请输入文章标题")]'))
            )
            
            title_element.clear()
            time.sleep(1)
            
            # 优先使用front matter中的标题
            title = front_matter.get('title') or self.common_config.get('title', '未命名文章')
            # 清理标题中的引号
            title = self.clean_title(title)
            title_element.send_keys(title)
            
            logger.info(f"✓ 标题填充完成：{title}")
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"✗ 填充标题失败：{e}", exc_info=True)
            return False
    
    def _fill_content(self, article_path: str) -> bool:
        """
        填充文章内容（使用HTML方式）
        
        Args:
            article_path: 文章文件路径
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在填充文章内容...")
            
            # 转换为HTML格式
            content_file_html = convert_md_to_html(article_path)
            logger.info(f"Markdown已转换为HTML：{content_file_html}")
            
            # 使用HTML内容填充（打开HTML文件并复制内容到剪贴板）
            get_html_web_content(self.driver, content_file_html)
            time.sleep(0.5)
            
            # 切换回编辑器标签页
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(1)
            
            # 定位到内容编辑器
            content_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="publish-editor"]//div[@class="ProseMirror"]'))
            )
            content_element.click()
            time.sleep(1)
            
            # 粘贴内容
            cmd_ctrl = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL
            action_chains = ActionChains(self.driver)
            action_chains.key_down(cmd_ctrl).send_keys('v').key_up(cmd_ctrl).perform()
            
            logger.info("✓ 内容填充完成")
            time.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"✗ 填充内容失败：{e}", exc_info=True)
            return False
    
    def _click_editor_blank_area(self) -> bool:
        """
        点击编辑器的空白位置，确保内容被正确识别
        这一步很关键，可以触发编辑器的内容更新和页面状态同步
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在点击编辑器空白位置获取焦点...")
            
            # 查找编辑器的 ProseMirror 容器
            editor_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="ProseMirror" and @contenteditable="true"]'))
            )
            
            # 点击编辑器的末尾位置
            # 使用JavaScript来确保点击生效
            self.driver.execute_script("arguments[0].focus();", editor_element)
            time.sleep(1)
            
            # 再次用鼠标点击确保获取焦点
            editor_element.click()
            time.sleep(1)
            
            logger.info("✓ 编辑器焦点获取完成")
            return True
            
        except Exception as e:
            logger.error(f"✗ 点击编辑器空白位置失败：{e}", exc_info=True)
            return False
    
    def _click_form_area(self) -> bool:
        """
        点击下方表单区域的空白位置，触发页面更新
        这一步可以让页面识别到内容已填充完成
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在点击表单区域空白位置...")

            # 方法2: 尝试点击整个表单容器
            try:
                form_container = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="edit-input"]'))
                )
                
                # 滚动到表单区域
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", form_container)
                time.sleep(1)
                
                # 点击表单区域
                form_container.click()
                logger.info("✓ 已点击表单容器空白位置")
                time.sleep(1)
                return True
            except:
                logger.info("方法2失败")
            
            logger.warning("⚠ 所有点击表单区域的方法都失败了")
            return False
            
        except Exception as e:
            logger.error(f"✗ 点击表单区域失败：{e}", exc_info=True)
            return False
    
    def _select_no_cover(self) -> bool:
        """
        选择无封面选项
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在选择无封面...")
            
            # 等待封面选项区域加载完成
            time.sleep(2)
            
            # 方法1: 通过文本定位
            try:
                no_cover_text = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//span[@class="byte-radio-inner-text" and text()="无封面"]'))
                )
                
                # 滚动到元素可见
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", no_cover_text)
                time.sleep(1)
                
                # 获取父级label元素（实际的radio按钮）
                no_cover_radio = no_cover_text.find_element(By.XPATH, './ancestor::label[@class="byte-radio"]')
                
                # 检查是否已经选中
                try:
                    checked = no_cover_radio.find_element(By.XPATH, './/div[contains(@class,"byte-radio-inner") and contains(@class,"checked")]')
                    logger.info("✓ 无封面已经是选中状态")
                    return True
                except:
                    # 未选中，则点击
                    no_cover_radio.click()
                    logger.info("✓ 已点击选择无封面")
                    time.sleep(2)
                    return True
                    
            except Exception as e1:
                logger.warning(f"方法1失败：{e1}，尝试方法2...")
                
                # 方法2: 通过value属性定位
                try:
                    no_cover_radio = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//label[@class="byte-radio"]//input[@type="radio" and @value="1"]/..'))
                    )
                    
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", no_cover_radio)
                    time.sleep(1)
                    
                    # 使用JavaScript点击（更可靠）
                    self.driver.execute_script("arguments[0].click();", no_cover_radio)
                    logger.info("✓ 已通过方法2选择无封面")
                    time.sleep(2)
                    return True
                    
                except Exception as e2:
                    logger.error(f"方法2也失败：{e2}")
                    return False
            
        except Exception as e:
            logger.error(f"✗ 选择无封面失败：{e}", exc_info=True)
            return False
    
    def _final_publish(self) -> bool:
        """
        最终发布文章
        包含以下步骤：
        1. 点击"预览并发布"按钮
        2. 等待页面加载
        3. 点击"确认发布"按钮
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("=" * 50)
            logger.info("开始最终发布流程...")
            logger.info("=" * 50)
            
            # 第一步：滚动到页面底部，确保发布按钮可见
            logger.info("步骤0: 滚动到页面底部...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 第一步：点击"预览并发布"按钮
            logger.info("步骤1: 查找并点击'预览并发布'按钮...")
            
            # 尝试多种定位方式
            preview_publish_button = None
            
            # 方法1: 通过按钮文本定位
            try:
                preview_publish_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(@class,"publish-btn-last") and .//span[text()="预览并发布"]]'))
                )
                logger.info("✓ 方法1: 通过文本定位到'预览并发布'按钮")
            except:
                logger.info("方法1失败，尝试方法2...")
                
                # 方法2: 通过class定位
                try:
                    preview_publish_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[contains(@class,"publish-btn-last")]'))
                    )
                    logger.info("✓ 方法2: 通过class定位到发布按钮")
                except:
                    logger.error("✗ 无法定位到'预览并发布'按钮")
                    return False
            
            # 滚动到按钮位置并高亮显示（便于调试）
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'}); "
                "arguments[0].style.border='3px solid red';",
                preview_publish_button
            )
            time.sleep(1)
            
            # 点击按钮
            try:
                preview_publish_button.click()
                logger.info("✓ 已点击'预览并发布'按钮")
            except:
                # 如果普通点击失败，使用JavaScript点击
                logger.info("普通点击失败，使用JavaScript点击...")
                self.driver.execute_script("arguments[0].click();", preview_publish_button)
                logger.info("✓ 已通过JavaScript点击'预览并发布'按钮")
            
            time.sleep(5)  # 等待页面跳转或弹窗加载
            
            # 第二步：等待并点击"确认发布"按钮
            logger.info("步骤2: 等待预览页面加载...")
            logger.info("步骤3: 查找并点击'确认发布'按钮...")
            
            # 尝试多种定位方式
            confirm_button = None
            
            # 方法1: 通过按钮文本定位
            try:
                confirm_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(@class,"publish-btn-last") and .//span[text()="确认发布"]]'))
                )
                logger.info("✓ 方法1: 通过文本定位到'确认发布'按钮")
            except:
                logger.info("方法1失败，尝试方法2...")
                
                # 方法2: 更宽松的定位
                try:
                    confirm_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[.//span[contains(text(),"确认发布")]]'))
                    )
                    logger.info("✓ 方法2: 通过contains文本定位到'确认发布'按钮")
                except:
                    logger.error("✗ 无法定位到'确认发布'按钮")
                    logger.info("尝试截图保存当前页面状态...")
                    try:
                        screenshot_path = f"/tmp/toutiao_publish_error_{int(time.time())}.png"
                        self.driver.save_screenshot(screenshot_path)
                        logger.info(f"截图已保存到: {screenshot_path}")
                    except:
                        pass
                    return False
            
            # 滚动到按钮位置并高亮显示
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'}); "
                "arguments[0].style.border='3px solid green';",
                confirm_button
            )
            time.sleep(1)
            
            # 点击确认发布按钮
            try:
                confirm_button.click()
                logger.info("✓ 已点击'确认发布'按钮")
            except:
                # 如果普通点击失败，使用JavaScript点击
                logger.info("普通点击失败，使用JavaScript点击...")
                self.driver.execute_script("arguments[0].click();", confirm_button)
                logger.info("✓ 已通过JavaScript点击'确认发布'按钮")
            
            time.sleep(5)  # 等待发布完成
            
            logger.info("=" * 50)
            logger.info("✓ 文章发布流程完成！")
            logger.info("=" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"✗ 发布文章失败：{e}", exc_info=True)
            
            # 尝试截图保存错误状态
            try:
                screenshot_path = f"/tmp/toutiao_publish_error_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.error(f"错误截图已保存到: {screenshot_path}")
            except:
                pass
            
            return False

"""
微信公众号 发布器
用于自动发布文章到微信公众平台
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
from src.utils.file_utils import read_file_with_footer, parse_front_matter, convert_md_to_html
from src.utils.selenium_utils import get_html_web_content
from src.utils.yaml_file_utils import read_mpweixin, read_common

logger = get_logger(__name__)


class WechatPublisher(BasePublisher):
    """微信公众号发布器"""
    
    PLATFORM_NAME = "wechat"
    
    def __init__(self, common_config: Dict[str, Any] = None, platform_config: Dict[str, Any] = None):
        """
        初始化微信公众号发布器
        
        Args:
            common_config: 通用配置
            platform_config: 微信平台配置
        """
        # 如果没有传入配置，从文件读取
        if common_config is None:
            common_config = read_common()
        if platform_config is None:
            platform_config = read_mpweixin()
        
        super().__init__(common_config, platform_config)
        
        self.site_url = platform_config.get('site', 'https://mp.weixin.qq.com/')
        self.auto_publish = common_config.get('auto_publish', False)
        self.author = platform_config.get('author', '')
        self.original = platform_config.get('original', True)
        
        logger.info(f"微信公众号发布器初始化完成，站点：{self.site_url}")
    
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
            # 多种方式检测登录状态
            current_url = self.driver.current_url
            logger.info(f"当前URL: {current_url}")
            
            # 1. 检查URL是否包含登录页面特征
            if 'bizlogin' in current_url or 'acct/login' in current_url:
                logger.info("⚠ 检测到登录页面，未登录")
                return False
            
            # 2. 检查是否存在文章按钮（已登录的标志）
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, 
                    '.new-creation__menu-content'
                )
                logger.info("✓ 检测到已登录状态（找到创作按钮）")
                return True
            except:
                pass
            
            # 也检查旧版图文消息按钮（兼容性）
            try:
                self.driver.find_element(
                    By.XPATH, 
                    '//div[@class="new-creation__menu-item"]//div[@class="new-creation__menu-title" and contains(text(), "图文消息")]'
                )
                logger.info("✓ 检测到已登录状态（找到图文消息按钮）")
                return True
            except:
                pass
            
            # 3. 检查是否有用户信息元素（多种方式）
            try:
                # 方式1: 检查用户头像图片
                self.driver.find_element(By.CLASS_NAME, 'weui-desktop-account__img')
                logger.info("✓ 检测到已登录状态（找到用户头像）")
                return True
            except:
                pass
            
            # 4. 检查用户名元素
            try:
                self.driver.find_element(By.CLASS_NAME, 'weui-desktop_name')
                logger.info("✓ 检测到已登录状态（找到用户名）")
                return True
            except:
                pass
            
            # 5. 检查个人信息容器
            try:
                self.driver.find_element(By.CLASS_NAME, 'weui-desktop-person_info')
                logger.info("✓ 检测到已登录状态（找到个人信息区域）")
                return True
            except:
                pass
            
            # 6. 通过XPath检查用户信息区域
            try:
                self.driver.find_element(
                    By.XPATH,
                    '//div[@class="weui-desktop-person_info"]//div[@class="weui-desktop_name"]'
                )
                logger.info("✓ 检测到已登录状态（通过XPath找到用户信息）")
                return True
            except:
                pass
            
            logger.warning("⚠ 未检测到明确的登录状态")
            logger.info("尝试获取页面源码片段进行调试...")
            try:
                # 输出页面部分源码用于调试
                page_source = self.driver.page_source
                if 'weui-desktop' in page_source:
                    logger.info("页面包含 weui-desktop 相关内容，可能已登录但元素定位需要调整")
                if '图文消息' in page_source:
                    logger.info("页面包含'图文消息'文本，可能已登录")
            except:
                pass
            
            return False
            
        except Exception as e:
            logger.warning(f"检查登录状态时出错：{e}")
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
        logger.info("请在浏览器中完成登录操作（扫码登录）")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                current_url = self.driver.current_url
                
                # 检查是否已经不在登录页面
                if 'bizlogin' not in current_url and 'acct/login' not in current_url:
                    # 等待页面加载完成
                    time.sleep(2)
                    
                    # 检查是否能找到文章按钮或用户信息
                    try:
                        # 尝试找到文章按钮（新版）
                        element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((
                                By.CSS_SELECTOR, 
                                '.new-creation__menu-content'
                            ))
                        )
                        logger.info("✓ 登录成功，已进入主页面（检测到创作按钮）")
                        time.sleep(2)  # 额外等待确保页面完全加载
                        return True
                    except:
                        pass
                    
                    # 尝试找到图文消息按钮（旧版，兼容性）
                    try:
                        element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((
                                By.XPATH, 
                                '//div[@class="new-creation__menu-item"]//div[@class="new-creation__menu-title" and contains(text(), "图文消息")]'
                            ))
                        )
                        logger.info("✓ 登录成功，已进入主页面")
                        time.sleep(2)  # 额外等待确保页面完全加载
                        return True
                    except:
                        pass
                    
                    # 尝试多种方式检测用户信息
                    login_detected = False
                    
                    # 方式1: 检查用户头像
                    try:
                        self.driver.find_element(By.CLASS_NAME, 'weui-desktop-account__img')
                        logger.info("✓ 登录成功，检测到用户头像")
                        login_detected = True
                    except:
                        pass
                    
                    # 方式2: 检查用户名
                    if not login_detected:
                        try:
                            self.driver.find_element(By.CLASS_NAME, 'weui-desktop_name')
                            logger.info("✓ 登录成功，检测到用户名")
                            login_detected = True
                        except:
                            pass
                    
                    # 方式3: 检查个人信息容器
                    if not login_detected:
                        try:
                            self.driver.find_element(By.CLASS_NAME, 'weui-desktop-person_info')
                            logger.info("✓ 登录成功，检测到个人信息区域")
                            login_detected = True
                        except:
                            pass
                    
                    if login_detected:
                        time.sleep(2)
                        return True
                
                # 短暂等待后继续检查
                time.sleep(2)
                
            except Exception as e:
                logger.debug(f"等待登录检查中：{e}")
                time.sleep(2)
        
        logger.error("✗ 等待登录超时")
        return False
    
    def _click_article_button(self) -> bool:
        """
        点击文章按钮（新版UI）
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在寻找文章按钮...")
            
            # 确保页面已完全加载
            time.sleep(2)
            
            # 尝试多次查找并点击（应对页面加载延迟）
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"尝试点击文章按钮（第 {attempt + 1}/{max_retries} 次）...")
                    
                    # 方式1：新版UI - 查找包含"文章"文本的按钮
                    try:
                        article_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((
                                By.XPATH,
                                '//div[@class="new-creation__menu-content" and contains(., "文章")]'
                            ))
                        )
                        
                        # 滚动到元素可见
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", article_button)
                        time.sleep(1)
                        
                        # 点击按钮
                        article_button.click()
                        logger.info("✓ 成功点击文章按钮（新版UI）")
                        time.sleep(3)
                        
                    except Exception as e1:
                        # 方式2：旧版UI - 查找"图文消息"按钮
                        logger.info("新版按钮未找到，尝试旧版图文消息按钮...")
                        article_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((
                                By.XPATH,
                                '//div[@class="new-creation__menu-item"]//div[@class="new-creation__menu-title" and contains(text(), "图文消息")]'
                            ))
                        )
                        
                        # 滚动到元素可见
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", article_button)
                        time.sleep(1)
                        
                        # 点击按钮
                        article_button.click()
                        logger.info("✓ 成功点击图文消息按钮（旧版UI）")
                        time.sleep(3)
                    
                    # 切换到新打开的编辑页面
                    if len(self.driver.window_handles) > 1:
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        logger.info("✓ 已切换到编辑页面")
                        time.sleep(2)
                        
                        # 验证是否成功进入编辑页面
                        current_url = self.driver.current_url
                        if 'appmsg' in current_url or 'operate' in current_url:
                            logger.info("✓ 成功进入文章编辑页面")
                            return True
                    
                    # 如果没有新窗口，可能是在同一页面
                    time.sleep(2)
                    return True
                    
                except Exception as e:
                    logger.warning(f"第 {attempt + 1} 次点击失败：{e}")
                    if attempt < max_retries - 1:
                        logger.info("等待后重试...")
                        time.sleep(3)
                    else:
                        raise
            
            return False
            
        except Exception as e:
            logger.error(f"✗ 点击文章按钮失败：{e}", exc_info=True)
            # 输出当前页面信息用于调试
            try:
                logger.error(f"当前URL: {self.driver.current_url}")
                logger.error(f"窗口数量: {len(self.driver.window_handles)}")
            except:
                pass
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
                EC.presence_of_element_located((By.ID, 'title'))
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
    
    def _fill_author(self, front_matter: Dict[str, Any]) -> bool:
        """
        填写文章作者
        
        Args:
            front_matter: 文章元数据
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在填写作者...")
            author_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'author'))
            )
            
            # 优先使用front matter中的作者信息
            author = front_matter.get('authors', self.author)
            if not author:
                author = self.author
            
            author_element.clear()
            author_element.send_keys(author)
            logger.info(f"✓ 作者已填写：{author}")
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"✗ 填写作者失败：{e}", exc_info=True)
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
            
            # 转换 Markdown 到 HTML（不转换代码块格式）
            content_file_html = convert_md_to_html(article_path, False)
            logger.info(f"已转换文章为HTML格式：{content_file_html}")
            
            # 通过辅助页面获取HTML内容到剪贴板
            get_html_web_content(self.driver, content_file_html)
            time.sleep(2)
            
            # 切换回微信编辑页面
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(1)
            
            # 尝试新版编辑器：.ProseMirror[contenteditable='true']
            try:
                logger.info("尝试定位新版编辑器（ProseMirror）...")
                content_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        '.ProseMirror[contenteditable="true"]'
                    ))
                )
                logger.info("✓ 找到新版编辑器")
            except:
                # 尝试旧版编辑器
                logger.info("新版编辑器未找到，尝试旧版编辑器...")
                content_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'edui1_contentplaceholder'))
                )
                logger.info("✓ 找到旧版编辑器")
            
            # 点击内容编辑区域
            ActionChains(self.driver).click(content_element).perform()
            time.sleep(1)
            
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
    
    def _set_original_statement(self) -> bool:
        """
        设置原创声明
        
        Returns:
            bool: 是否成功
        """
        try:
            if not self.original:
                logger.info("未启用原创声明，跳过")
                return True
            
            logger.info("正在设置原创声明...")
            
            # 步骤1: 点击"未声明"按钮
            try:
                original_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((
                        By.CSS_SELECTOR,
                        '.js_unset_original_title'
                    ))
                )
                logger.info("找到原创声明按钮，准备点击...")
                original_button.click()
                time.sleep(2)
                logger.info("✓ 成功点击原创声明按钮")
            except Exception as e:
                logger.warning(f"点击原创声明按钮失败（可能已经设置过）：{e}")
                # 尝试旧版按钮ID
                try:
                    original_statement = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.ID, 'js_original'))
                    )
                    original_statement.click()
                    time.sleep(2)
                    logger.info("✓ 使用旧版按钮成功点击")
                except:
                    logger.warning("未找到原创声明按钮，可能已经声明过")
                    return True
            
            # 步骤2: 检查并勾选协议复选框
            try:
                logger.info("正在检查协议复选框...")
                
                # 查找复选框元素
                checkbox = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        '//label[@class="weui-desktop-form__check-label"]//input[@type="checkbox" and @class="weui-desktop-form__checkbox"]'
                    ))
                )
                
                # 检查是否已经勾选
                is_checked = checkbox.is_selected() or checkbox.get_attribute('checked')
                
                if is_checked:
                    logger.info("✓ 协议复选框已勾选，跳过")
                else:
                    logger.info("协议复选框未勾选，准备点击...")
                    
                    # 点击label元素（更可靠）
                    label = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((
                            By.CSS_SELECTOR,
                            'label.weui-desktop-form__check-label'
                        ))
                    )
                    label.click()
                    time.sleep(1)
                    logger.info("✓ 已勾选原创声明协议")
                    
            except Exception as e:
                logger.warning(f"检查/勾选协议复选框时出错：{e}")
                logger.info("尝试继续执行...")
            
            # 步骤3: 点击确定按钮
            try:
                logger.info("正在查找确定按钮...")
                confirm_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '//button[@type="button" and contains(@class, "weui-desktop-btn_primary") and text()="确定"]'
                    ))
                )
                logger.info("找到确定按钮，准备点击...")
                confirm_button.click()
                time.sleep(2)
                logger.info("✓ 原创声明已设置")
                return True
                
            except Exception as e1:
                # 尝试备用定位方式
                logger.info("尝试备用定位方式查找确定按钮...")
                try:
                    confirm_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            '//div[@class="weui-desktop-dialog"]//div[@class="weui-desktop-btn_wrp"]//button[contains(text(), "确定")]'
                        ))
                    )
                    confirm_button.click()
                    time.sleep(2)
                    logger.info("✓ 原创声明已设置（使用备用方法）")
                    return True
                except Exception as e2:
                    logger.error(f"✗ 点击确定按钮失败：{e1}, 备用方法也失败：{e2}")
                    return False
            
        except Exception as e:
            logger.error(f"✗ 设置原创声明失败：{e}", exc_info=True)
            return False

    def _save_as_draft(self) -> bool:
        """
        保存文章为草稿
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在保存为草稿...")
            
            # 方式1：新版UI - 使用 #js_submit button
            try:
                draft_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((
                        By.CSS_SELECTOR, 
                        '#js_submit button'
                    ))
                )
                draft_button.click()
                time.sleep(2)
                
                logger.info("✓ 文章已保存为草稿（新版UI）")
                logger.info("💡 您可以稍后在微信公众平台的草稿箱中找到该文章")
                return True
                
            except Exception as e1:
                logger.info(f"新版保存按钮未找到，尝试旧版...")
                
                # 方式2：旧版UI - 查找"保存为草稿"按钮
                try:
                    draft_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((
                            By.XPATH, 
                            '//button[@type="button"]//span[@class="send_wording" and text()="保存为草稿"]'
                        ))
                    )
                    draft_button.click()
                    time.sleep(2)
                    
                    logger.info("✓ 文章已保存为草稿（旧版UI）")
                    logger.info("💡 您可以稍后在微信公众平台的草稿箱中找到该文章")
                    return True
                    
                except Exception as e2:
                    # 方式3：通过文本定位
                    logger.info("尝试通过文本定位保存按钮...")
                    draft_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((
                            By.XPATH, 
                            '//button[contains(., "保存") or contains(., "草稿")]'
                        ))
                    )
                    draft_button.click()
                    time.sleep(2)
                    
                    logger.info("✓ 文章已保存（使用备用方法）")
                    return True
                    
        except Exception as e:
            logger.error(f"✗ 保存草稿失败：{e}", exc_info=True)
            logger.info("⚠ 请手动点击'保存为草稿'或'保存'按钮")
            return False
    
    def publish(self, article_path: str) -> bool:
        """
        发布文章到微信公众号（保存为草稿）
        
        Args:
            article_path: 文章文件路径
        
        Returns:
            bool: 是否发布成功
        
        Note:
            此方法会将文章保存为草稿，不会直接发布。
            您可以稍后在微信公众平台的草稿箱中找到并发布文章。
        """
        logger.info(f"=" * 60)
        logger.info(f"开始发布文章到微信公众号：{article_path}")
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
            
            # 5. 点击图文消息按钮
            if not self._click_article_button():
                logger.error("✗ 无法进入编辑页面")
                return False
            
            # 6. 解析文章元数据
            front_matter = self.parse_article_metadata(article_path)
            
            # 7. 填充文章标题
            if not self._fill_title(front_matter):
                logger.error("✗ 填写标题失败")
                return False
            
            # 8. 填充文章作者
            if not self._fill_author(front_matter):
                logger.error("✗ 填写作者失败")
                return False
            
            # 9. 填充文章内容
            if not self._fill_content(article_path):
                logger.error("✗ 填写内容失败")
                return False
            
            # 10. 设置原创声明
            self._set_original_statement()
            
            # 13. 保存为草稿
            if not self._save_as_draft():
                logger.error("✗ 保存草稿失败")
                return False
            
            logger.info(f"=" * 60)
            logger.info("✓ 微信公众号文章已保存为草稿")
            logger.info(f"=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"✗ 发布过程中发生错误：{e}", exc_info=True)
            return False
        finally:
            # 注意：不要在这里关闭driver，因为可能还要发布到其他平台
            pass

"""
51CTO 发布器
用于自动发布文章到 51CTO 平台
"""

import time
from typing import Dict, Any
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.publisher.base_publisher import BasePublisher
from src.publisher.common_handler import wait_login, safe_click, safe_input, switch_to_new_tab
from src.core.logger import get_logger
from src.utils.file_utils import read_file_with_footer, parse_front_matter
from src.utils.yaml_file_utils import read_cto51, read_common

logger = get_logger(__name__)


class CTO51Publisher(BasePublisher):
    """51CTO 发布器"""
    
    PLATFORM_NAME = "cto51"
    
    def __init__(self, common_config: Dict[str, Any] = None, platform_config: Dict[str, Any] = None):
        """
        初始化51CTO发布器
        
        Args:
            common_config: 通用配置
            platform_config: 51CTO平台配置
        """
        # 如果没有传入配置，从文件读取
        if common_config is None:
            common_config = read_common()
        if platform_config is None:
            platform_config = read_cto51()
        
        super().__init__(common_config, platform_config)
        
        self.site_url = platform_config.get('site', 'https://blog.51cto.com/posting')
        self.auto_publish = common_config.get('auto_publish', False)
        
        logger.info(f"51CTO发布器初始化完成，站点：{self.site_url}")
    
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
            # 检查页面是否有标题输入框（登录后才有）
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "title"))
            )
            logger.info("✓ 检测到已登录")
            return True
        except:
            logger.info("✗ 检测到未登录")
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
        try:
            # 等待标题输入框出现
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, "title"))
            )
            logger.info("✓ 用户登录成功")
            return True
        except Exception as e:
            logger.error(f"✗ 等待登录超时：{e}")
            return False
    
    def publish(self, article_path: str) -> bool:
        """
        发布文章到51CTO
        
        Args:
            article_path: 文章文件路径
        
        Returns:
            bool: 是否发布成功
        """
        logger.info(f"=" * 60)
        logger.info(f"开始发布文章到51CTO：{article_path}")
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
            else:
                # 如果已经登录，更新cookies以保持同步
                logger.debug("已登录状态，更新cookies...")
                self.update_cookies(self.site_url)
            
            # 5. 解析文章元数据
            front_matter = self.parse_article_metadata(article_path)
            
            # 6. 填充文章标题
            self._fill_title(front_matter)
            
            # 7. 填充文章内容
            self._fill_content(article_path)
            
            # 8. 点击发布按钮（进入发布设置页面）
            self._click_publish_button()
            
            # 9. 填充发布设置
            self._fill_publish_settings(front_matter)
            
            # 10. 最终发布
            if self.auto_publish:
                self._final_publish()
                logger.info("✓ 文章已成功发布到51CTO")
                
                # 发布成功后更新cookies
                logger.debug("发布成功，更新cookies...")
                self.update_cookies(self.site_url)
            else:
                logger.info("⚠ 自动发布未启用，请手动点击发布按钮")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ 发布文章时发生错误：{e}", exc_info=True)
            return False
    
    def _fill_title(self, front_matter: Dict[str, Any]):
        """填充文章标题"""
        logger.info("填充文章标题...")
        try:
            # 等待标题输入框出现
            title_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'title'))
            )
            
            # 清空并填充标题
            title_element.clear()
            
            # 优先使用front matter中的标题
            if 'title' in front_matter and front_matter['title']:
                title = front_matter['title']
            else:
                title = self.common_config.get('title', '未命名文章')
            
            # 清理标题中的引号
            title = self.clean_title(title)
            
            # 标题最多100个字符
            if len(title) > 100:
                title = title[:100]
                logger.warning("⚠ 标题超过100字符，已截断")
            
            title_element.send_keys(title)
            logger.info(f"✓ 标题已填充：{title}")
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"✗ 填充标题失败：{e}")
            raise
    
    def _fill_content(self, article_path: str):
        """填充文章内容"""
        logger.info("填充文章内容...")
        try:
            # 读取文章内容
            file_content = read_file_with_footer(article_path)
            
            # 等待内容输入框出现并可交互
            content_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea.auto-textarea-input.write-area'))
            )
            
            # 滚动到元素可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", content_element)
            time.sleep(0.5)
            
            # 清空并填充内容
            content_element.clear()
            time.sleep(0.3)
            content_element.send_keys(file_content)
            
            logger.info(f"✓ 内容已填充，长度：{len(file_content)}")
            logger.info("等待5秒，让平台处理图片解析...")
            time.sleep(5)  # 等待图片解析
            
        except Exception as e:
            logger.error(f"✗ 填充内容失败：{e}")
            raise
    
    def _click_publish_button(self):
        """点击发布按钮（进入发布设置页面）"""
        logger.info("点击发布按钮...")
        try:
            # 使用更精确的选择器：button.edit-submit
            send_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.edit-submit'))
            )
            ActionChains(self.driver).click(send_button).perform()
            logger.info("✓ 已点击发布按钮")
            time.sleep(5)  # 等待发布设置页面加载
        except Exception as e:
            logger.error(f"✗ 点击发布按钮失败：{e}")
            raise
    
    def _fill_publish_settings(self, front_matter: Dict[str, Any]):
        """填充发布设置"""
        logger.info("填充发布设置...")
        
        # 只填充标签，跳过其他设置
        self._fill_tags(front_matter)
        
        logger.info("✓ 发布设置已填充完成")
    
    def _select_article_type(self):
        """选择文章分类（一级和二级分类）"""
        try:
            article_type = self.platform_config.get('type')
            article_subtype = self.platform_config.get('subtype')  # 二级分类
            
            if not article_type:
                logger.warning("⚠ 未配置文章分类，跳过")
                return
            
            logger.info(f"选择文章分类：{article_type}")
            
            # 选择一级分类 - 使用 div.select_item
            type_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//div[@class="types_content"]//div[contains(@class, "select_item")]/span[text()="{article_type}"]/..'))
            )
            type_button.click()
            logger.info(f"✓ 已选择一级分类：{article_type}")
            time.sleep(2)
            
            # 如果有二级分类配置，则选择二级分类
            if article_subtype:
                logger.info(f"选择二级分类：{article_subtype}")
                subtype_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f'//div[@class="second-types-content"]//div[contains(@class, "second-types-item")]/span[text()="{article_subtype}"]/..'))
                )
                subtype_button.click()
                logger.info(f"✓ 已选择二级分类：{article_subtype}")
                time.sleep(2)
            
        except Exception as e:
            logger.warning(f"⚠ 选择文章分类失败：{e}")
            logger.warning(f"⚠ 选择文章分类失败：{e}")
    
    def _select_personal_type(self):
        """选择个人分类"""
        try:
            personal_type = self.platform_config.get('personal_type')
            if not personal_type:
                logger.warning("⚠ 未配置个人分类，跳过")
                return
            
            logger.info(f"选择个人分类：{personal_type}")
            
            # 点击个人分类下拉框 - 使用 CSS 选择器
            personal_type_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.el-input__inner.pull-down[id="selfType"]'))
            )
            personal_type_input.click()
            time.sleep(1)
            
            # 选择分类
            personal_type_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//li[@class="el-select-dropdown__item"]/span[text()="{personal_type}"]'))
            )
            personal_type_element.click()
            logger.info(f"✓ 已选择个人分类：{personal_type}")
            time.sleep(1)
        except Exception as e:
            logger.warning(f"⚠ 选择个人分类失败：{e}")
    
    def _fill_tags(self, front_matter: Dict[str, Any]):
        """填充标签（使用 Enter 键分隔）"""
        try:
            # 优先使用front matter中的标签
            if 'tags' in front_matter and front_matter['tags']:
                tags = front_matter['tags']
            else:
                tags = self.platform_config.get('tags', [])
            
            if not tags:
                logger.warning("⚠ 未配置标签，跳过")
                return
            
            # 限制标签数量为5个
            if len(tags) > 5:
                logger.warning(f"⚠ 标签数量超过5个，只使用前5个")
                tags = tags[:5]
            
            logger.info(f"填充标签：{tags}")
            
            # 等待标签输入框出现并可交互
            tag_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'tag-input'))
            )
            
            # 滚动到元素可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", tag_input)
            time.sleep(0.5)
            
            # 点击输入框确保焦点
            tag_input.click()
            time.sleep(0.5)
            
            # 逐个添加标签
            for i, tag in enumerate(tags):
                # 每个标签最多20个字符
                if len(tag) > 20:
                    tag = tag[:20]
                    logger.warning(f"⚠ 标签 '{tag}' 长度超过20字符，已截断")
                
                # 清空输入框
                tag_input.clear()
                time.sleep(0.3)
                
                # 输入标签内容
                tag_input.send_keys(tag)
                time.sleep(0.3)
                
                # 按 Enter 键确认
                tag_input.send_keys(Keys.ENTER)
                logger.info(f"  ✓ 已添加标签 {i+1}/{len(tags)}：{tag}")
                time.sleep(0.5)
            
            logger.info(f"✓ 成功填充 {len(tags)} 个标签")
            
        except Exception as e:
            logger.warning(f"⚠ 填充标签失败：{e}")
            # 非关键步骤，失败也继续
    
    def _fill_summary(self, front_matter: Dict[str, Any]):
        """填充摘要"""
        try:
            # 优先使用front matter中的摘要
            if 'description' in front_matter and front_matter['description']:
                summary = front_matter['description']
            else:
                summary = self.common_config.get('summary')
            
            if not summary:
                logger.warning("⚠ 未配置摘要，跳过")
                return
            
            # 摘要最多500字
            if len(summary) > 500:
                summary = summary[:500]
                logger.warning("⚠ 摘要超过500字，已截断")
            
            logger.info("填充摘要...")
            summary_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[id="abstractData"]'))
            )
            summary_input.clear()
            summary_input.send_keys(summary)
            logger.info(f"✓ 已填充摘要：{summary[:50]}...")
        except Exception as e:
            logger.warning(f"⚠ 填充摘要失败：{e}")
    
    def _select_topic(self):
        """选择话题"""
        try:
            topic = self.platform_config.get('topic')
            if not topic:
                logger.warning("⚠ 未配置话题，跳过")
                return
            
            logger.info(f"选择话题：{topic}")
            
            # 点击话题下拉框
            topic_input = self.driver.find_element(By.ID, 'subjuct')
            topic_input.click()
            time.sleep(1)
            
            # 选择话题
            list_item_list = self.driver.find_element(By.ID, 'listItemList')
            list_item_list.find_element(By.XPATH, f'//li[contains(text(),"{topic}")]').click()
            logger.info(f"✓ 已选择话题：{topic}")
        except Exception as e:
            logger.warning(f"⚠ 选择话题失败：{e}")
    
    def _final_publish(self):
        """最终发布"""
        logger.info("执行最终发布...")
        try:
            # 等待页面加载完成
            time.sleep(2)
            
            # 尝试多种方式定位发布按钮
            publish_button = None
            
            try:
                # 方式1: 通过 ID
                publish_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, 'submitForm'))
                )
                logger.info("✓ 通过 ID 找到发布按钮")
            except:
                try:
                    # 方式2: 通过 class name
                    publish_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'release'))
                    )
                    logger.info("✓ 通过 class name 找到发布按钮")
                except:
                    try:
                        # 方式3: 通过 XPath 文本
                        publish_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "发布")]'))
                        )
                        logger.info("✓ 通过 XPath 找到发布按钮")
                    except:
                        logger.error("✗ 无法找到发布按钮")
                        raise Exception("无法定位发布按钮")
            
            if publish_button:
                # 滚动到按钮可见
                self.driver.execute_script("arguments[0].scrollIntoView(true);", publish_button)
                time.sleep(0.5)
                
                # 点击发布
                publish_button.click()
                logger.info("✓ 已点击最终发布按钮")
                time.sleep(3)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"✗ 最终发布失败：{e}")
            raise

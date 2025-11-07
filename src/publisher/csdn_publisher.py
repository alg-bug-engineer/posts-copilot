"""
CSDN 发布器
用于自动发布文章到 CSDN 平台
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
from src.utils.yaml_file_utils import read_csdn, read_common

logger = get_logger(__name__)


class CSDNPublisher(BasePublisher):
    """CSDN 发布器"""
    
    PLATFORM_NAME = "csdn"
    
    def __init__(self, common_config: Dict[str, Any] = None, platform_config: Dict[str, Any] = None):
        """
        初始化CSDN发布器
        
        Args:
            common_config: 通用配置
            platform_config: CSDN平台配置
        """
        # 如果没有传入配置，从文件读取
        if common_config is None:
            common_config = read_common()
        if platform_config is None:
            platform_config = read_csdn()
        
        super().__init__(common_config, platform_config)
        
        self.site_url = platform_config.get('site', 'https://editor.csdn.net/md/')
        self.auto_publish = common_config.get('auto_publish', False)
        
        logger.info(f"CSDN发布器初始化完成，站点：{self.site_url}")
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return self.PLATFORM_NAME
    
    def publish(self, article_path: str) -> bool:
        """
        发布文章到CSDN
        
        Args:
            article_path: 文章文件路径
        
        Returns:
            bool: 是否发布成功
        """
        logger.info(f"=" * 60)
        logger.info(f"开始发布文章到CSDN：{article_path}")
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
            
            # 6. 填充文章标题
            if not self._fill_title(front_matter):
                logger.error("✗ 填充标题失败")
                return False
            
            # 7. 填充文章内容
            if not self._fill_content(article_path):
                logger.error("✗ 填充内容失败")
                return False
            
            # 8. 点击发布按钮
            if not self._click_publish_button():
                logger.error("✗ 点击发布按钮失败")
                return False
            
            # 9. 填充发布设置
            if not self._fill_publish_settings(front_matter):
                logger.error("✗ 填充发布设置失败")
                return False
            
            # 10. 最终发布
            if self.auto_publish:
                if not self._final_publish():
                    logger.error("✗ 最终发布失败")
                    return False
                logger.info("✓ 文章发布成功！")
            else:
                logger.info("⚠ 未启用自动发布，请手动点击发布按钮")
            
            logger.info(f"=" * 60)
            logger.info("CSDN 文章发布流程完成")
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
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"article-bar")]//input[contains(@placeholder,"请输入文章标题")]'))
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
            '//div[contains(@class,"article-bar")]//input[contains(@placeholder,"请输入文章标题")]',
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
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"article-bar")]//input[contains(@placeholder,"请输入文章标题")]'))
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
        填充文章内容
        
        Args:
            article_path: 文章文件路径
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在填充文章内容...")
            
            # 读取文章内容
            file_content = read_file_with_footer(article_path)
            logger.info(f"文章内容长度：{len(file_content)} 字符")
            
            # 复制内容到剪贴板
            pyperclip.copy(file_content)
            logger.debug("内容已复制到剪贴板")
            
            # 定位编辑器
            content_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="editor"]//div[@class="cledit-section"]'))
            )
            content_element.click()
            time.sleep(2)
            
            # 粘贴内容
            cmd_ctrl = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL
            action_chains = ActionChains(self.driver)
            action_chains.key_down(cmd_ctrl).send_keys('v').key_up(cmd_ctrl).perform()
            
            logger.info("✓ 内容填充完成")
            time.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"✗ 填充内容失败：{e}", exc_info=True)
            return False
    
    def _click_publish_button(self) -> bool:
        """
        点击发布文章按钮
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在点击发布按钮...")
            
            send_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "btn-publish") and contains(text(),"发布文章")]'))
            )
            send_button.click()
            
            logger.info("✓ 发布按钮点击完成")
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"✗ 点击发布按钮失败：{e}", exc_info=True)
            return False
    
    def _fill_publish_settings(self, front_matter: Dict[str, Any]) -> bool:
        """
        填充发布设置（标签、分类、封面、摘要等）
        
        Args:
            front_matter: 文章元数据
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在填充发布设置...")
            
            # 填充标签
            self._fill_tags(front_matter)
            
            # 填充封面
            self._fill_cover(front_matter)
            
            # 填充摘要
            self._fill_summary(front_matter)
            
            # 填充分类专栏
            self._fill_categories()
            
            # 设置可见范围
            self._set_visibility()
            
            logger.info("✓ 发布设置填充完成")
            return True
            
        except Exception as e:
            logger.error(f"✗ 填充发布设置失败：{e}", exc_info=True)
            return False
    
    def _fill_tags(self, front_matter: Dict[str, Any]):
        """填充文章标签"""
        try:
            tags = front_matter.get('tags') or self.platform_config.get('tags', [])
            
            if not tags:
                logger.info("⚠ 未配置标签，跳过")
                return
            
            logger.info(f"正在添加标签：{tags}")
            
            # 点击添加标签按钮
            add_tag_btn = self.driver.find_element(By.XPATH,
                '//div[@class="mark_selection"]//button[@class="tag__btn-tag" and contains(text(),"添加文章标签")]')
            add_tag_btn.click()
            time.sleep(1)
            
            # 输入标签
            tag_input = self.driver.find_element(By.XPATH,
                '//div[@class="mark_selection_box"]//input[contains(@placeholder,"请输入文字搜索")]')
            
            for tag in tags:
                tag_input.clear()
                tag_input.send_keys(tag)
                time.sleep(2)
                tag_input.send_keys(Keys.ENTER)
                time.sleep(1)
                logger.debug(f"  ✓ 添加标签：{tag}")
            
            # 关闭标签选择框
            close_btn = self.driver.find_element(By.XPATH,
                '//div[@class="mark_selection_box"]//button[@title="关闭"]')
            close_btn.click()
            time.sleep(1)
            
            logger.info(f"✓ 标签添加完成，共 {len(tags)} 个")
            
        except Exception as e:
            logger.warning(f"⚠ 添加标签时出错：{e}")
    
    def _fill_cover(self, front_matter: Dict[str, Any]):
        """填充文章封面"""
        try:
            image_url = front_matter.get('image')
            
            if not image_url:
                logger.info("⚠ 未配置封面图片，跳过")
                return
            
            logger.info(f"正在上传封面：{image_url}")
            
            file_input = self.driver.find_element(By.XPATH,
                "//input[@class='el-upload__input' and @type='file']")
            
            # 下载图片到本地
            local_image_path = download_image(image_url)
            file_input.send_keys(local_image_path)
            
            logger.info("✓ 封面上传完成")
            time.sleep(2)
            
        except Exception as e:
            logger.warning(f"⚠ 上传封面时出错：{e}")
    
    def _fill_summary(self, front_matter: Dict[str, Any]):
        """填充文章摘要"""
        try:
            summary = front_matter.get('description') or self.common_config.get('summary', '')
            
            if not summary:
                logger.info("⚠ 未配置摘要，跳过")
                return
            
            logger.info("正在填充摘要...")
            
            summary_input = self.driver.find_element(By.XPATH,
                '//div[@class="desc-box"]//textarea[contains(@placeholder,"摘要：会在推荐、列表等场景外露")]')
            summary_input.clear()
            summary_input.send_keys(summary)
            
            logger.info("✓ 摘要填充完成")
            time.sleep(2)
            
        except Exception as e:
            logger.warning(f"⚠ 填充摘要时出错：{e}")
    
    def _fill_categories(self):
        """填充分类专栏"""
        try:
            categories = self.platform_config.get('categories', [])
            
            if not categories:
                logger.info("⚠ 未配置分类专栏，跳过")
                return
            
            logger.info(f"正在选择分类专栏：{categories}")
            
            # 点击新建分类专栏按钮
            add_category_btn = self.driver.find_element(By.XPATH,
                '//div[@id="tagList"]//button[@class="tag__btn-tag" and contains(text(),"新建分类专栏")]')
            add_category_btn.click()
            time.sleep(1)
            
            # 选择分类
            for category in categories:
                try:
                    category_checkbox = self.driver.find_element(By.XPATH,
                        f'//input[@type="checkbox" and @value="{category}"]/..')
                    category_checkbox.click()
                    time.sleep(1)
                    logger.debug(f"  ✓ 选择分类：{category}")
                except:
                    logger.warning(f"  ⚠ 分类不存在：{category}")
            
            # 关闭分类选择框
            close_btn = self.driver.find_element(By.XPATH,
                '//div[@class="tag__options-content"]//button[@class="modal__close-button button" and @title="关闭"]')
            close_btn.click()
            time.sleep(1)
            
            logger.info(f"✓ 分类专栏选择完成")
            
        except Exception as e:
            logger.warning(f"⚠ 选择分类专栏时出错：{e}")
    
    def _set_visibility(self):
        """设置可见范围"""
        try:
            visibility = self.platform_config.get('visibility', '全部可见')
            
            logger.info(f"正在设置可见范围：{visibility}")
            
            visibility_label = self.driver.find_element(By.XPATH,
                f'//div[@class="switch-box"]//label[contains(text(),"{visibility}")]')
            parent_element = visibility_label.find_element(By.XPATH, '..')
            parent_element.click()
            
            logger.info("✓ 可见范围设置完成")
            time.sleep(1)
            
        except Exception as e:
            logger.warning(f"⚠ 设置可见范围时出错：{e}")
    
    def _final_publish(self) -> bool:
        """
        最终发布文章
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在执行最终发布...")
            
            publish_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                    '//div[@class="modal__button-bar"]//button[contains(text(),"发布文章")]'))
            )
            publish_button.click()
            
            logger.info("✓ 最终发布按钮已点击")
            time.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"✗ 最终发布失败：{e}", exc_info=True)
            return False


# 提供旧接口的兼容函数
def csdn_publisher(driver, content=None):
    """
    兼容旧版本的发布函数
    
    Args:
        driver: WebDriver实例
        content: 文章文件路径
    """
    logger.warning("使用了已废弃的 csdn_publisher 函数，建议使用 CSDNPublisher 类")
    
    common_config = read_common()
    if content:
        common_config['content'] = content
    
    publisher = CSDNPublisher(common_config=common_config)
    publisher.driver = driver
    
    article_path = content or common_config.get('content')
    return publisher.publish(article_path)


if __name__ == "__main__":
    # 测试代码
    from src.utils.yaml_file_utils import read_common, read_csdn
    
    common_config = read_common()
    csdn_config = read_csdn()
    
    with CSDNPublisher(common_config, csdn_config) as publisher:
        article_path = common_config.get('content')
        success = publisher.publish(article_path)
        print(f"发布{'成功' if success else '失败'}")

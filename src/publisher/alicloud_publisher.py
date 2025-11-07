"""
阿里云开发者社区 发布器
用于自动发布文章到阿里云开发者社区平台
"""

import sys
import time
import random
from typing import Dict, Any
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.publisher.base_publisher import BasePublisher
from src.publisher.common_handler import wait_login, safe_click, safe_input, switch_to_new_tab
from src.core.logger import get_logger
from src.utils.file_utils import read_file_with_footer, parse_front_matter
from src.utils.yaml_file_utils import read_alcloud, read_common

logger = get_logger(__name__)


class AlicloudPublisher(BasePublisher):
    """阿里云开发者社区发布器"""
    
    PLATFORM_NAME = "alicloud"
    
    def __init__(self, common_config: Dict[str, Any] = None, platform_config: Dict[str, Any] = None):
        """
        初始化阿里云发布器
        
        Args:
            common_config: 通用配置
            platform_config: 阿里云平台配置
        """
        # 如果没有传入配置，从文件读取
        if common_config is None:
            common_config = read_common()
        if platform_config is None:
            platform_config = read_alcloud()
        
        super().__init__(common_config, platform_config)
        
        self.site_url = platform_config.get('site', 'https://developer.aliyun.com/article/new')
        self.auto_publish = platform_config.get('auto_publish', False) or common_config.get('auto_publish', False)
        self.auto_summary = platform_config.get('auto_summary', True)
        self.community = platform_config.get('community', '')
        self.tags = platform_config.get('tags', [])
        
        logger.info(f"阿里云发布器初始化完成，站点：{self.site_url}")
    
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
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="请填写标题"]'))
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
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="请填写标题"]'))
            )
            logger.info("✓ 登录成功")
            return True
        except Exception as e:
            logger.error(f"✗ 等待登录超时：{e}")
            return False
    
    def _handle_slider_verification(self, max_retry: int = 3) -> bool:
        """
        处理滑块验证
        
        Args:
            max_retry: 最大重试次数
        
        Returns:
            bool: 是否验证成功
        """
        for attempt in range(max_retry):
            try:
                # 检查是否存在滑块验证
                slider_text = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '//span[@class="nc-lang-cnt"]'))
                )
                
                if "请按住滑块，拖动到最右边" in slider_text.text:
                    logger.info(f"⚠ 检测到滑块验证（第 {attempt + 1}/{max_retry} 次尝试）")
                    
                    # 查找滑块按钮
                    slider_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//span[@id="nc_1_n1z" and contains(@class, "btn_slide")]'))
                    )
                    
                    # 获取滑块的位置和大小
                    slider_size = slider_button.size
                    slider_location = slider_button.location
                    
                    logger.info(f"滑块位置: {slider_location}, 大小: {slider_size}")
                    
                    # 获取滑块轨道的宽度（通常是父元素的宽度）
                    slider_track = self.driver.find_element(By.XPATH, '//span[@id="nc_1_n1z"]/parent::*')
                    track_width = slider_track.size['width']
                    
                    # 计算需要拖动的距离（轨道宽度 - 滑块宽度 + 额外补偿）
                    # 加上20像素确保拖动到最右边
                    drag_distance = track_width - slider_size['width'] + 20
                    
                    logger.info(f"轨道宽度: {track_width}px, 滑块宽度: {slider_size['width']}px")
                    logger.info(f"计算拖动距离: {drag_distance}px")
                    
                    # 创建 ActionChains 对象
                    action = ActionChains(self.driver)
                    
                    # 模拟人类拖拽行为：先快速拖动大部分距离，然后缓慢拖动到底
                    action.click_and_hold(slider_button).perform()
                    time.sleep(0.2)  # 按住后短暂停顿
                    
                    # 第一阶段：快速拖动80%的距离
                    first_move = int(drag_distance * 0.8)
                    logger.info(f"第一阶段：拖动 {first_move}px")
                    action.move_by_offset(first_move, 0).perform()
                    time.sleep(0.1)
                    
                    # 第二阶段：分段拖动剩余20%的距离，模拟人类微调
                    remaining_distance = drag_distance - first_move
                    segments = 3  # 分3段完成剩余距离
                    segment_distance = remaining_distance / segments
                    
                    logger.info(f"第二阶段：分{segments}段拖动剩余 {remaining_distance}px")
                    for i in range(segments):
                        # 确保每段都是正数，并且有小幅随机偏移
                        offset = segment_distance + random.uniform(0, 2)  # 只用正数偏移
                        action.move_by_offset(offset, random.uniform(-1, 1)).perform()
                        time.sleep(random.uniform(0.08, 0.15))  # 随机停顿
                    
                    # 最后再多拖一点，确保到达最右边
                    logger.info(f"最后补偿：额外拖动 5px")
                    action.move_by_offset(5, 0).perform()
                    time.sleep(0.3)  # 到达最右边后停顿
                    
                    # 释放滑块
                    action.release().perform()
                    logger.info("✓ 滑块拖动完成，已释放")
                    time.sleep(1)  # 等待验证
                    
                    # 检查是否需要点击确认按钮
                    try:
                        confirm_button = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((
                                By.XPATH, 
                                '//button[contains(@class, "next-btn-primary") and contains(text(), "确认")]'
                            ))
                        )
                        logger.info("找到确认按钮，准备点击...")
                        confirm_button.click()
                        logger.info("✓ 已点击确认按钮")
                        time.sleep(2)
                    except TimeoutException:
                        logger.info("未找到确认按钮，可能已自动通过验证")
                    
                    # 验证是否成功
                    time.sleep(2)
                    try:
                        # 检查滑块是否消失
                        self.driver.find_element(By.XPATH, '//span[@class="nc-lang-cnt"]')
                        logger.warning("⚠ 滑块验证可能失败，滑块仍然存在")
                        continue
                    except NoSuchElementException:
                        logger.info("✓ 滑块验证成功")
                        return True
                else:
                    logger.info("未检测到滑块验证")
                    return True
                    
            except TimeoutException:
                # 没有找到滑块，说明不需要验证或已经通过
                logger.info("未检测到滑块验证（可能不需要验证）")
                return True
            except Exception as e:
                logger.error(f"✗ 处理滑块验证时出错（第 {attempt + 1} 次）：{e}", exc_info=True)
                if attempt < max_retry - 1:
                    logger.info(f"等待 2 秒后重试...")
                    time.sleep(2)
                    continue
        
        logger.error(f"✗ 滑块验证失败，已重试 {max_retry} 次")
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
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="请填写标题"]'))
            )
            
            title = front_matter.get('title', self.common_config.get('title', ''))
            if not title:
                logger.warning("未找到标题，使用默认值")
                title = "未命名文章"
            
            # 清理标题中的引号
            title = self.clean_title(title)
            
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
        填写文章内容（Markdown 格式）
        
        Args:
            article_path: 文章路径
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info("正在填写文章内容...")
            
            # 读取 Markdown 内容（包含页脚）
            file_content = read_file_with_footer(article_path)
            logger.info(f"已读取文章内容，长度：{len(file_content)}")
            
            # 查找内容编辑区域（阿里云使用 textarea）
            content_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    '//div[@class="editor"]//textarea[@class="textarea"]'
                ))
            )
            
            # 填充内容
            content_element.clear()
            content_element.send_keys(file_content)
            
            logger.info("✓ 内容已填写")
            time.sleep(3)
            
            return True
        except Exception as e:
            logger.error(f"✗ 填写内容失败：{e}", exc_info=True)
            return False
    
    def _fill_summary(self, front_matter: Dict[str, Any]) -> bool:
        """
        填写文章摘要
        
        Args:
            front_matter: 文章元数据
        
        Returns:
            bool: 是否成功
        """
        try:
            if not self.auto_summary:
                logger.info("未启用自动摘要，跳过")
                return True
            
            logger.info("正在填写摘要...")
            
            # 从 front matter 或通用配置获取摘要
            summary = front_matter.get('description', self.common_config.get('summary', ''))
            
            if not summary:
                logger.info("未设置摘要，跳过")
                return True
            
            # 查找摘要输入框
            summary_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    '//div[@class="abstractContent-box"]//textarea[@placeholder="请填写摘要"]'
                ))
            )
            
            summary_element.clear()
            summary_element.send_keys(summary)
            
            logger.info(f"✓ 摘要已填写：{summary[:50]}...")
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"✗ 填写摘要失败：{e}", exc_info=True)
            return False
    
    def _select_community(self) -> bool:
        """
        选择子社区
        
        Returns:
            bool: 是否成功
        """
        try:
            if not self.community:
                logger.info("未设置子社区，跳过")
                return True
            
            logger.info(f"正在选择子社区：{self.community}")
            
            # TODO: 实现子社区选择逻辑
            # 阿里云的子社区选择需要根据实际页面结构来实现
            logger.warning("⚠ 子社区选择功能待实现")
            
            return True
        except Exception as e:
            logger.error(f"✗ 选择子社区失败：{e}", exc_info=True)
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
                EC.element_to_be_clickable((
                    By.XPATH, 
                    '//div[@class="publish-fixed-box-btn"]/button[contains(text(),"发布文章")]'
                ))
            )
            publish_button.click()
            
            logger.info("已点击发布按钮，等待响应...")
            time.sleep(2)
            
            # 发布时可能再次出现滑块验证
            logger.info("检查发布时是否需要滑块验证...")
            if not self._handle_slider_verification():
                logger.error("✗ 发布时滑块验证失败")
                return False
            
            logger.info("✓ 文章发布成功")
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"✗ 发布文章失败：{e}", exc_info=True)
            return False
    
    def publish(self, article_path: str) -> bool:
        """
        发布文章到阿里云开发者社区
        
        Args:
            article_path: 文章文件路径
        
        Returns:
            bool: 是否发布成功
        """
        logger.info(f"=" * 60)
        logger.info(f"开始发布文章到阿里云开发者社区：{article_path}")
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
            
            # 5. 处理滑块验证（如果存在）
            logger.info("检查是否需要滑块验证...")
            if not self._handle_slider_verification():
                logger.error("✗ 滑块验证失败")
                logger.info("提示：请手动完成滑块验证后重试")
                return False
            
            # 6. 解析文章元数据
            front_matter = self.parse_article_metadata(article_path)
            
            # 7. 填写标题
            if not self._fill_title(front_matter):
                logger.error("✗ 填写标题失败")
                return False
            
            # 8. 填写内容
            if not self._fill_content(article_path):
                logger.error("✗ 填写内容失败")
                return False
            
            # 9. 填写摘要
            if not self._fill_summary(front_matter):
                logger.warning("⚠ 填写摘要失败，继续...")
            
            # 10. 选择子社区
            if not self._select_community():
                logger.warning("⚠ 选择子社区失败，继续...")
            
            # 11. 发布文章（可能再次出现滑块验证）
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

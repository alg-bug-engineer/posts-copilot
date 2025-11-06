"""
通用处理器模块
提供各平台发布器共用的通用功能
"""

import time
from typing import Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.core.logger import get_logger

logger = get_logger(__name__)


def wait_login(driver: WebDriver, by: str, locator: str, timeout: int = 120) -> bool:
    """
    等待用户登录，通过检测特定元素是否出现来判断
    
    Args:
        driver: WebDriver实例
        by: 元素定位方式（如 By.XPATH, By.ID 等）
        locator: 元素定位符
        timeout: 超时时间（秒），默认120秒
    
    Returns:
        bool: 是否成功登录
    """
    logger.info(f"等待用户登录，超时时间：{timeout}秒")
    logger.info(f"检测元素：{by}={locator}")
    
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
        logger.info("✓ 检测到登录成功！")
        return True
    except TimeoutException:
        logger.error(f"✗ 等待登录超时（{timeout}秒）")
        return False
    except Exception as e:
        logger.error(f"✗ 等待登录时发生错误：{e}", exc_info=True)
        return False


def safe_click(driver: WebDriver, by: str, locator: str, wait_time: float = 2.0, 
               timeout: int = 10) -> bool:
    """
    安全地点击元素，包含等待和异常处理
    
    Args:
        driver: WebDriver实例
        by: 元素定位方式
        locator: 元素定位符
        wait_time: 点击后等待时间（秒）
        timeout: 查找元素超时时间（秒）
    
    Returns:
        bool: 是否成功点击
    """
    try:
        logger.debug(f"尝试点击元素：{by}={locator}")
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, locator))
        )
        element.click()
        logger.debug(f"✓ 成功点击元素")
        time.sleep(wait_time)
        return True
    except TimeoutException:
        logger.warning(f"✗ 查找元素超时：{by}={locator}")
        return False
    except Exception as e:
        logger.warning(f"✗ 点击元素失败：{e}")
        return False


def safe_input(driver: WebDriver, by: str, locator: str, text: str, 
               clear_first: bool = True, wait_time: float = 1.0, 
               timeout: int = 10) -> bool:
    """
    安全地输入文本，包含等待和异常处理
    
    Args:
        driver: WebDriver实例
        by: 元素定位方式
        locator: 元素定位符
        text: 要输入的文本
        clear_first: 是否先清空输入框
        wait_time: 输入后等待时间（秒）
        timeout: 查找元素超时时间（秒）
    
    Returns:
        bool: 是否成功输入
    """
    try:
        logger.debug(f"尝试输入文本到：{by}={locator}")
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
        
        if clear_first:
            element.clear()
            time.sleep(0.5)
        
        element.send_keys(text)
        logger.debug(f"✓ 成功输入文本（长度：{len(text)}）")
        time.sleep(wait_time)
        return True
    except TimeoutException:
        logger.warning(f"✗ 查找输入框超时：{by}={locator}")
        return False
    except Exception as e:
        logger.warning(f"✗ 输入文本失败：{e}")
        return False


def check_element_exists(driver: WebDriver, by: str, locator: str, 
                         timeout: int = 5) -> bool:
    """
    检查元素是否存在
    
    Args:
        driver: WebDriver实例
        by: 元素定位方式
        locator: 元素定位符
        timeout: 超时时间（秒）
    
    Returns:
        bool: 元素是否存在
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
        return True
    except:
        return False


def scroll_to_element(driver: WebDriver, element):
    """
    滚动到指定元素
    
    Args:
        driver: WebDriver实例
        element: 要滚动到的元素
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
        logger.debug("✓ 已滚动到元素位置")
    except Exception as e:
        logger.warning(f"✗ 滚动到元素失败：{e}")


def retry_on_failure(func, max_retries: int = 3, delay: float = 2.0):
    """
    失败重试装饰器
    
    Args:
        func: 要执行的函数
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
    
    Returns:
        函数执行结果
    """
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"第 {attempt + 1} 次尝试失败，{delay}秒后重试：{e}")
                    time.sleep(delay)
                else:
                    logger.error(f"重试 {max_retries} 次后仍然失败：{e}")
                    raise
    return wrapper


def switch_to_new_tab(driver: WebDriver, url: str = None):
    """
    打开新标签页并切换
    
    Args:
        driver: WebDriver实例
        url: 要打开的URL（可选）
    """
    try:
        driver.switch_to.new_window('tab')
        logger.debug("✓ 已切换到新标签页")
        
        if url:
            driver.get(url)
            logger.debug(f"✓ 已打开URL：{url}")
            time.sleep(2)
    except Exception as e:
        logger.error(f"✗ 切换标签页失败：{e}", exc_info=True)


def close_current_tab(driver: WebDriver):
    """
    关闭当前标签页并切换到上一个标签页
    
    Args:
        driver: WebDriver实例
    """
    try:
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        logger.debug("✓ 已关闭当前标签页")
    except Exception as e:
        logger.error(f"✗ 关闭标签页失败：{e}", exc_info=True)

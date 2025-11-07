"""
主发布脚本
支持交互式发布文章到各个平台
"""

import os
import sys
import traceback
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logger import setup_logger, get_logger
from src.core.session_manager import SessionManager
from src.utils.file_utils import list_files, write_to_file, read_head
from src.utils.yaml_file_utils import read_common

# 初始化日志
logger = setup_logger('publish_script')

# 配置文件
LAST_PUBLISHED_FILE = project_root / 'data' / 'last_published.txt'

# 支持的平台列表
ALL_PLATFORMS = [
    'csdn',
    # 'jianshu',
    'juejin',
    # 'segmentfault',
    # 'oschina',
    # 'cnblogs',
    'zhihu',
    'cto51',
    # 'infoq',
    # 'txcloud',
    'alicloud',
    'toutiao',
    # 'wechat',  # 微信公众号（也支持 mpweixin）
]


def get_publisher(platform: str):
    """
    根据平台名称获取发布器实例
    
    Args:
        platform: 平台名称
    
    Returns:
        发布器实例
    """
    if platform == 'csdn':
        from src.publisher.csdn_publisher import CSDNPublisher
        return CSDNPublisher()
    elif platform == 'cto51':
        from src.publisher.cto51_publisher import CTO51Publisher
        return CTO51Publisher()
    elif platform == 'toutiao':
        from src.publisher.toutiao_publisher import ToutiaoPublisher
        return ToutiaoPublisher()
    elif platform == 'juejin':
        from src.publisher.juejin_publisher import JuejinPublisher
        return JuejinPublisher()
    elif platform == 'zhihu':
        from src.publisher.zhihu_publisher import ZhihuPublisher
        return ZhihuPublisher()
    elif platform == 'alicloud':
        from src.publisher.alicloud_publisher import AlicloudPublisher
        return AlicloudPublisher()
    elif platform == 'wechat' or platform == 'mpweixin':
        from src.publisher.wechat_publisher import WechatPublisher
        return WechatPublisher()
    # TODO: 添加其他平台的发布器
    else:
        logger.warning(f"平台 {platform} 的发布器尚未实现")
        return None


def publish_to_platform(platform: str, article_path: str, session_manager: SessionManager) -> bool:
    """
    发布到指定平台
    
    Args:
        platform: 平台名称
        article_path: 文章路径
        session_manager: 会话管理器
    
    Returns:
        bool: 是否成功
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"开始发布到平台：{platform.upper()}")
    logger.info(f"文章名称：{os.path.basename(article_path)}")
    logger.info(f"文章路径：{article_path}")
    logger.info(f"{'='*60}\n")
    
    try:
        publisher = get_publisher(platform)
        if not publisher:
            logger.error(f"无法获取 {platform} 的发布器")
            return False
        
        # 设置驱动（复用会话管理器）
        publisher.session_manager = session_manager
        publisher.driver = session_manager.driver
        
        # 执行发布
        success = publisher.publish(article_path)
        
        if success:
            logger.info(f"✓ {platform.upper()} 发布成功！")
            save_last_published_file(os.path.basename(article_path))
        else:
            logger.error(f"✗ {platform.upper()} 发布失败")
        
        return success
        
    except Exception as e:
        logger.error(f"✗ {platform.upper()} 发布过程中发生错误：{e}", exc_info=True)
        traceback.print_exc()
        return False


def publish_to_all_platforms(article_path: str, session_manager: SessionManager):
    """
    发布到所有已启用的平台
    
    Args:
        article_path: 文章路径
        session_manager: 会话管理器
    """
    common_config = read_common()
    enabled_platforms = common_config.get('enable', {})
    
    success_count = 0
    fail_count = 0
    
    for platform in ALL_PLATFORMS:
        if enabled_platforms.get(platform, False):
            logger.info(f"\n准备发布到：{platform}")
            if publish_to_platform(platform, article_path, session_manager):
                success_count += 1
            else:
                fail_count += 1
        else:
            logger.debug(f"平台 {platform} 未启用，跳过")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"发布完成！成功：{success_count}，失败：{fail_count}")
    logger.info(f"{'='*60}\n")


def save_last_published_file(filename: str):
    """保存最后发布的文件名"""
    LAST_PUBLISHED_FILE.parent.mkdir(parents=True, exist_ok=True)
    write_to_file(filename, str(LAST_PUBLISHED_FILE))
    logger.debug(f"已保存最后发布的文件：{filename}")


def get_last_published_file() -> str:
    """获取最后发布的文件名"""
    if LAST_PUBLISHED_FILE.exists():
        return read_head(str(LAST_PUBLISHED_FILE)).strip()
    return "无"


def select_article() -> str:
    """
    选择要发布的文章
    
    Returns:
        str: 文章路径
    """
    common_config = read_common()
    content_dir = common_config.get('content_dir')
    
    if not content_dir or not os.path.exists(content_dir):
        logger.error(f"文章目录不存在：{content_dir}")
        return None
    
    file_list = list_files(content_dir, ".md")
    
    if not file_list:
        logger.error(f"目录中没有找到 Markdown 文件：{content_dir}")
        return None
    
    print("\n" + "="*60)
    print("请选择要发布的文章：")
    print("="*60)
    
    for index, file_path in enumerate(file_list):
        filename = os.path.basename(file_path)
        # 标记上次发布的文章
        marker = " 👈 上次发布" if filename == get_last_published_file() else ""
        print(f"{index}. {filename}{marker}")
    
    print("="*60)
    
    try:
        choice = input("\n请输入文章序号：").strip()
        index = int(choice)
        
        if 0 <= index < len(file_list):
            selected_file = file_list[index]
            selected_filename = os.path.basename(selected_file)
            print(f"✓ 已选择：[{index}] {selected_filename}")
            logger.info(f"已选择文章：[{index}] {selected_filename}")
            logger.info(f"文章路径：{selected_file}")
            return selected_file
        else:
            logger.error("无效的序号")
            return None
            
    except ValueError:
        logger.error("请输入有效的数字")
        return None
    except KeyboardInterrupt:
        logger.info("\n用户取消操作")
        return None


def select_platform(current_article: str = None) -> str:
    """
    选择发布平台
    
    Args:
        current_article: 当前选择的文章路径（用于显示）
    
    Returns:
        str: 平台名称，'all' 表示所有平台，'back' 表示返回上一级，'quit' 表示退出程序
    """
    print("\n" + "="*60)
    print("请选择发布平台：")
    print("="*60)
    
    # 显示当前选择的文章
    if current_article:
        print(f"📄 当前文章：{os.path.basename(current_article)}")
        print("="*60)
    
    print("1.  全部平台")
    print("2.  CSDN")
    # print("3.  简书")
    print("3.  掘金")
    # print("5.  SegmentFault")
    # print("6.  开源中国")
    # print("7.  博客园")
    print("4.  知乎")
    print("5.  51CTO")
    # print("10. InfoQ")
    # print("11. 腾讯云")
    print("6. 阿里云")
    print("7. 今日头条")
    # print("8. 微信公众号")
    print("0.  返回上一级（重新选择文章）")
    print("q.  退出程序")
    print("="*60)
    
    platform_map = {
        '1': 'all',
        '2': 'csdn',
        # '3': 'jianshu',
        '3': 'juejin',
        # '5': 'segmentfault',
        # '6': 'oschina',
        # '7': 'cnblogs',
        '4': 'zhihu',
        '5': 'cto51',
        # '10': 'infoq',
        # '11': 'txcloud',
        '6': 'alicloud',
        '7': 'toutiao',
        # '8': 'mpweixin',
        '0': 'back',
        'q': 'quit',
        'Q': 'quit'
    }
    
    try:
        choice = input("\n请选择：").strip()
        platform = platform_map.get(choice)
        
        if platform:
            if platform == 'back':
                logger.info("返回上一级")
                return 'back'
            elif platform == 'quit':
                logger.info("退出程序")
                return 'quit'
            else:
                logger.info(f"已选择平台：{platform}")
                return platform
        else:
            logger.error("无效的选择")
            return select_platform()
            
    except KeyboardInterrupt:
        logger.info("\n用户取消操作")
        return 'quit'


def main():
    """主函数"""
    logger.info("="*60)
    logger.info("博客自动发布工具 v2.0")
    logger.info("="*60)
    
    try:
        # 读取配置
        common_config = read_common()
        
        # 创建会话管理器
        session_manager = SessionManager('common', common_config)
        
        try:
            session_manager.create_driver(use_existing=True)
        except Exception as e:
            error_msg = str(e)
            logger.error(f"连接Chrome失败，错误类型：{type(e).__name__}, 错误信息：{error_msg}")
            logger.error(f"完整错误堆栈：", exc_info=True)
            
            if 'cannot connect to chrome' in error_msg.lower() or 'unable to discover open pages' in error_msg.lower():
                logger.error("=" * 60)
                logger.error("⚠️  无法连接到 Chrome 调试模式")
                logger.error("=" * 60)
                logger.error("")
                logger.error("可能的原因：")
                logger.error("1. Chrome 调试模式未启动")
                logger.error("2. Chrome 已启动但没有打开任何页面")
                logger.error("")
                logger.error("解决方案：")
                logger.error("")
                logger.error("方案1：使用脚本启动 Chrome（推荐）")
                logger.error("  bash scripts/start_chrome.sh")
                logger.error("")
                logger.error("方案2：手动启动 Chrome 调试模式")
                logger.error("  macOS:")
                logger.error('  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\')
                logger.error('    --remote-debugging-port=9222 \\')
                logger.error('    --user-data-dir="/tmp/chrome_dev" \\')
                logger.error('    about:blank')
                logger.error("")
                logger.error("方案3：在已运行的 Chrome 中打开一个新标签页")
                logger.error("  确保 Chrome 至少有一个打开的标签页")
                logger.error("")
                logger.error("=" * 60)
                return
            else:
                raise
        
        logger.info("✓ 浏览器驱动初始化完成")
        
        # 主循环
        should_exit = False
        current_article_path = None  # 记录当前选择的文章
        
        while not should_exit:
            # 选择文章
            article_path = select_article()
            if not article_path:
                continue
            
            # 更新当前文章路径并记录日志
            current_article_path = article_path
            logger.info(f"✓ 当前选择的文章：{os.path.basename(current_article_path)}")
            logger.info(f"   完整路径：{current_article_path}")
            
            # 内部循环 - 选择平台
            while True:
                platform = select_platform(current_article_path)
                
                if platform == 'back':
                    # 返回上一级（重新选择文章）
                    logger.info("返回上一级，将重新选择文章")
                    break
                elif platform == 'quit':
                    # 退出程序
                    should_exit = True
                    break
                elif platform == 'all':
                    # 发布到所有平台
                    logger.info(f"准备将文章发布到所有平台：{os.path.basename(current_article_path)}")
                    publish_to_all_platforms(current_article_path, session_manager)
                    # 发布完成后继续循环，可以选择继续发布或退出
                else:
                    # 发布到指定平台
                    logger.info(f"准备将文章发布到 {platform.upper()}：{os.path.basename(current_article_path)}")
                    publish_to_platform(platform, current_article_path, session_manager)
                    # 发布完成后继续循环，可以选择继续发布或退出
        
    except KeyboardInterrupt:
        logger.info("\n\n用户中断程序")
    except Exception as e:
        logger.error(f"程序发生错误：{e}", exc_info=True)
    finally:
        # 清理资源
        if 'session_manager' in locals():
            session_manager.close()
        logger.info("程序退出")


if __name__ == '__main__':
    main()

"""
测试掘金发布器
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logger import setup_logger, get_logger
from src.publisher.juejin_publisher import JuejinPublisher
from src.utils.yaml_file_utils import read_common

# 初始化日志
logger = setup_logger('test_juejin')


def test_juejin_publisher():
    """测试掘金发布器"""
    logger.info("=" * 60)
    logger.info("开始测试掘金发布器")
    logger.info("=" * 60)
    
    try:
        # 1. 读取配置
        common_config = read_common()
        article_path = common_config.get('content', '')
        
        if not article_path:
            logger.error("未配置文章路径")
            return False
        
        logger.info(f"文章路径：{article_path}")
        
        # 2. 创建发布器实例
        publisher = JuejinPublisher()
        logger.info("✓ 掘金发布器实例创建成功")
        
        # 3. 测试发布
        success = publisher.publish(article_path)
        
        if success:
            logger.info("=" * 60)
            logger.info("✓ 掘金发布器测试成功！")
            logger.info("=" * 60)
        else:
            logger.error("=" * 60)
            logger.error("✗ 掘金发布器测试失败")
            logger.error("=" * 60)
        
        return success
        
    except Exception as e:
        logger.error(f"✗ 测试过程中发生错误：{e}", exc_info=True)
        return False
    finally:
        # 清理资源
        if 'publisher' in locals():
            publisher.cleanup()


if __name__ == "__main__":
    test_juejin_publisher()

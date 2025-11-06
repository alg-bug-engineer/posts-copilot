"""
测试今日头条发布器
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.publisher.toutiao_publisher import ToutiaoPublisher
from src.core.logger import setup_logger, get_logger
from src.utils.yaml_file_utils import read_common

# 初始化日志
logger = setup_logger('test_toutiao')


def test_toutiao_publisher():
    """测试今日头条发布器"""
    
    logger.info("="*60)
    logger.info("开始测试今日头条发布器")
    logger.info("="*60)
    
    try:
        # 读取配置
        common_config = read_common()
        
        # 获取测试文章路径
        content_dir = common_config.get('content_dir')
        test_article = Path(content_dir) / "RAG模型革命：大模型时代的问答系统最佳实践揭秘.md"
        
        if not test_article.exists():
            logger.error(f"测试文章不存在：{test_article}")
            return False
        
        logger.info(f"测试文章：{test_article}")
        
        # 创建发布器
        publisher = ToutiaoPublisher()
        
        # 设置驱动
        publisher.setup_driver(use_existing=True)
        
        # 发布文章
        success = publisher.publish(str(test_article))
        
        if success:
            logger.info("✓ 测试成功！")
        else:
            logger.error("✗ 测试失败！")
        
        # 清理资源
        input("\n按回车键关闭浏览器并退出...")
        publisher.cleanup()
        
        return success
        
    except Exception as e:
        logger.error(f"测试过程中发生错误：{e}", exc_info=True)
        return False


if __name__ == "__main__":
    test_toutiao_publisher()

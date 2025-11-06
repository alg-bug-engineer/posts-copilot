"""
知乎发布器测试脚本
用于测试知乎发布器的功能
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logger import setup_logger, get_logger
from src.publisher.zhihu_publisher import ZhihuPublisher

# 初始化日志
logger = setup_logger('test_zhihu')


def test_zhihu_publisher():
    """测试知乎发布器"""
    logger.info("=" * 60)
    logger.info("开始测试知乎发布器")
    logger.info("=" * 60)
    
    try:
        # 1. 创建发布器实例
        logger.info("步骤 1: 创建知乎发布器实例")
        publisher = ZhihuPublisher()
        logger.info("✓ 发布器实例创建成功")
        
        # 2. 设置驱动
        logger.info("\n步骤 2: 设置浏览器驱动")
        publisher.setup_driver(use_existing=True)
        logger.info("✓ 浏览器驱动设置成功")
        
        # 3. 选择测试文章
        posts_dir = project_root / 'posts'
        articles = list(posts_dir.glob('*.md'))
        
        if not articles:
            logger.error("✗ 未找到测试文章")
            return False
        
        # 排除HTML文件，只选择.md文件
        articles = [a for a in articles if a.suffix == '.md']
        
        if not articles:
            logger.error("✗ 未找到.md格式的测试文章")
            return False
        
        logger.info(f"\n找到 {len(articles)} 篇文章：")
        for i, article in enumerate(articles, 1):
            logger.info(f"{i}. {article.name}")
        
        # 使用第一篇文章进行测试
        test_article = str(articles[0])
        logger.info(f"\n步骤 3: 使用文章进行测试：{articles[0].name}")
        
        # 4. 发布文章
        logger.info("\n步骤 4: 开始发布文章")
        success = publisher.publish(test_article)
        
        if success:
            logger.info("\n" + "=" * 60)
            logger.info("✓ 测试成功！文章已发布到知乎")
            logger.info("=" * 60)
            return True
        else:
            logger.error("\n" + "=" * 60)
            logger.error("✗ 测试失败！文章发布失败")
            logger.error("=" * 60)
            return False
            
    except Exception as e:
        logger.error(f"✗ 测试过程中出现错误：{e}", exc_info=True)
        return False
    finally:
        # 清理资源
        if 'publisher' in locals():
            logger.info("\n清理资源...")
            # 注意：不要关闭浏览器，因为可能还在使用
            # publisher.cleanup()


if __name__ == "__main__":
    logger.info("知乎发布器测试脚本启动")
    logger.info(f"项目根目录：{project_root}")
    
    success = test_zhihu_publisher()
    
    if success:
        logger.info("\n✓ 所有测试通过")
        sys.exit(0)
    else:
        logger.error("\n✗ 测试失败")
        sys.exit(1)

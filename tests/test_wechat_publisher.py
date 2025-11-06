"""
微信公众号发布器测试
测试微信公众号发布功能的集成
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logger import setup_logger, get_logger
from src.publisher.wechat_publisher import WechatPublisher
from src.utils.yaml_file_utils import read_common, read_mpweixin

# 初始化日志
logger = setup_logger('test_wechat_publisher')


def test_wechat_publisher_init():
    """测试微信发布器初始化"""
    logger.info("="*60)
    logger.info("测试1: 微信发布器初始化")
    logger.info("="*60)
    
    try:
        publisher = WechatPublisher()
        logger.info(f"✓ 发布器初始化成功")
        logger.info(f"  平台名称: {publisher.get_platform_name()}")
        logger.info(f"  站点URL: {publisher.site_url}")
        logger.info(f"  作者: {publisher.author}")
        logger.info(f"  原创标记: {publisher.original}")
        logger.info(f"  自动发布: {publisher.auto_publish}")
        return True
    except Exception as e:
        logger.error(f"✗ 发布器初始化失败: {e}", exc_info=True)
        return False


def test_wechat_config():
    """测试微信配置读取"""
    logger.info("\n" + "="*60)
    logger.info("测试2: 微信配置读取")
    logger.info("="*60)
    
    try:
        common_config = read_common()
        wechat_config = read_mpweixin()
        
        logger.info("✓ 配置读取成功")
        logger.info(f"  通用配置: {list(common_config.keys())}")
        logger.info(f"  微信配置: {wechat_config}")
        
        # 检查微信是否在启用列表中
        enabled = common_config.get('enable', {})
        wechat_enabled = enabled.get('wechat', False) or enabled.get('mpweixin', False)
        logger.info(f"  微信发布状态: {'启用' if wechat_enabled else '未启用'}")
        
        return True
    except Exception as e:
        logger.error(f"✗ 配置读取失败: {e}", exc_info=True)
        return False


def test_wechat_publish_dry_run():
    """测试微信发布器（不实际发布）"""
    logger.info("\n" + "="*60)
    logger.info("测试3: 微信发布器功能测试（模拟）")
    logger.info("="*60)
    
    try:
        # 获取测试文章
        posts_dir = project_root / 'posts'
        test_articles = list(posts_dir.glob('*.md'))
        
        if not test_articles:
            logger.warning("⚠ 未找到测试文章")
            return True
        
        test_article = str(test_articles[0])
        logger.info(f"使用测试文章: {test_article}")
        
        # 初始化发布器
        publisher = WechatPublisher()
        
        # 测试元数据解析
        front_matter = publisher.parse_article_metadata(test_article)
        logger.info(f"✓ 元数据解析成功: {front_matter.get('title', '无标题')}")
        
        # 测试内容读取
        content = publisher.read_article_content(test_article, include_footer=False)
        logger.info(f"✓ 内容读取成功，长度: {len(content)} 字符")
        
        logger.info("✓ 微信发布器功能测试通过")
        logger.info("⚠ 注意: 这是模拟测试，未实际连接浏览器")
        
        return True
    except Exception as e:
        logger.error(f"✗ 功能测试失败: {e}", exc_info=True)
        return False


def main():
    """运行所有测试"""
    logger.info("开始微信公众号发布器集成测试\n")
    
    results = []
    
    # 运行测试
    results.append(("初始化测试", test_wechat_publisher_init()))
    results.append(("配置读取测试", test_wechat_config()))
    results.append(("功能测试", test_wechat_publish_dry_run()))
    
    # 输出测试结果
    logger.info("\n" + "="*60)
    logger.info("测试结果汇总")
    logger.info("="*60)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{test_name}: {status}")
    
    # 统计
    passed = sum(1 for _, result in results if result)
    total = len(results)
    logger.info(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        logger.info("\n✓ 所有测试通过！微信发布器集成成功！")
        return True
    else:
        logger.error(f"\n✗ 有 {total - passed} 个测试失败")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

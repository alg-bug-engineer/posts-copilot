"""
51CTO 发布器集成测试
测试 51CTO 发布器是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.publisher.cto51_publisher import CTO51Publisher
from src.utils.yaml_file_utils import read_common, read_cto51
from src.core.logger import setup_logger, get_logger

# 初始化日志
logger = setup_logger('test_cto51')


def test_config_loading():
    """测试配置文件加载"""
    logger.info("=" * 60)
    logger.info("测试 1: 配置文件加载")
    logger.info("=" * 60)
    
    try:
        common_config = read_common()
        cto51_config = read_cto51()
        
        logger.info("✓ 通用配置加载成功")
        logger.info(f"  - content_dir: {common_config.get('content_dir')}")
        logger.info(f"  - auto_publish: {common_config.get('auto_publish')}")
        logger.info(f"  - cto51 启用状态: {common_config.get('enable', {}).get('cto51')}")
        
        logger.info("✓ 51CTO 配置加载成功")
        logger.info(f"  - site: {cto51_config.get('site')}")
        logger.info(f"  - type: {cto51_config.get('type')}")
        logger.info(f"  - personal_type: {cto51_config.get('personal_type')}")
        logger.info(f"  - tags: {cto51_config.get('tags')}")
        logger.info(f"  - topic: {cto51_config.get('topic')}")
        
        return True
    except Exception as e:
        logger.error(f"✗ 配置加载失败: {e}", exc_info=True)
        return False


def test_publisher_init():
    """测试发布器初始化"""
    logger.info("\n" + "=" * 60)
    logger.info("测试 2: 发布器初始化")
    logger.info("=" * 60)
    
    try:
        publisher = CTO51Publisher()
        
        logger.info("✓ 发布器创建成功")
        logger.info(f"  - 平台名称: {publisher.get_platform_name()}")
        logger.info(f"  - 站点 URL: {publisher.site_url}")
        logger.info(f"  - 自动发布: {publisher.auto_publish}")
        
        return True
    except Exception as e:
        logger.error(f"✗ 发布器初始化失败: {e}", exc_info=True)
        return False


def test_article_parsing():
    """测试文章解析"""
    logger.info("\n" + "=" * 60)
    logger.info("测试 3: 文章解析")
    logger.info("=" * 60)
    
    try:
        publisher = CTO51Publisher()
        
        # 查找测试文章
        posts_dir = project_root / "posts"
        if not posts_dir.exists():
            logger.warning("⚠ posts 目录不存在，跳过测试")
            return True
        
        md_files = list(posts_dir.glob("*.md"))
        if not md_files:
            logger.warning("⚠ 没有找到测试文章，跳过测试")
            return True
        
        test_article = str(md_files[0])
        logger.info(f"使用测试文章: {test_article}")
        
        # 解析元数据
        front_matter = publisher.parse_article_metadata(test_article)
        logger.info("✓ 元数据解析成功")
        if front_matter:
            logger.info(f"  - title: {front_matter.get('title', 'N/A')}")
            logger.info(f"  - tags: {front_matter.get('tags', 'N/A')}")
            logger.info(f"  - description: {front_matter.get('description', 'N/A')[:50]}...")
        else:
            logger.info("  - 未找到 Front Matter")
        
        # 读取内容
        content = publisher.read_article_content(test_article)
        logger.info("✓ 文章内容读取成功")
        logger.info(f"  - 内容长度: {len(content)} 字符")
        
        return True
    except Exception as e:
        logger.error(f"✗ 文章解析失败: {e}", exc_info=True)
        return False


def test_cookie_path():
    """测试 Cookie 路径"""
    logger.info("\n" + "=" * 60)
    logger.info("测试 4: Cookie 管理")
    logger.info("=" * 60)
    
    try:
        publisher = CTO51Publisher()
        
        # Cookie 文件路径
        cookie_file = project_root / "data" / "cookies" / "cto51_cookies.json"
        
        logger.info(f"Cookie 文件路径: {cookie_file}")
        if cookie_file.exists():
            logger.info("✓ 已存在保存的 Cookie")
            logger.info(f"  - 文件大小: {cookie_file.stat().st_size} 字节")
        else:
            logger.info("⚠ 未找到保存的 Cookie（首次使用正常）")
        
        return True
    except Exception as e:
        logger.error(f"✗ Cookie 路径检查失败: {e}", exc_info=True)
        return False


def main():
    """运行所有测试"""
    logger.info("开始 51CTO 发布器集成测试\n")
    
    tests = [
        ("配置文件加载", test_config_loading),
        ("发布器初始化", test_publisher_init),
        ("文章解析", test_article_parsing),
        ("Cookie 管理", test_cookie_path),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"测试 '{test_name}' 执行异常: {e}", exc_info=True)
            results.append((test_name, False))
    
    # 输出测试结果
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info("=" * 60)
    logger.info(f"总计: {len(results)} 个测试, {passed} 通过, {failed} 失败")
    logger.info("=" * 60)
    
    if failed == 0:
        logger.info("\n🎉 所有测试通过！51CTO 发布器已准备就绪。")
        logger.info("\n下一步:")
        logger.info("1. 启动 Chrome: bash scripts/start_chrome.sh")
        logger.info("2. 运行发布: python publish.py")
        logger.info("3. 选择文章和平台: 9. 51CTO")
    else:
        logger.error(f"\n⚠️ {failed} 个测试失败，请检查配置和代码。")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

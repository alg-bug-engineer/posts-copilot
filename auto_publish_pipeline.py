#!/usr/bin/env python3
"""
auto_publish_pipeline.py

完整的内容生成和发布闭环流水线
1. 自动生成内容
2. 自动发布到所有平台（双层循环：文章×平台）
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from generate.auto_content_pipeline import AutoContentPipeline
from src.core.logger import setup_logger
from src.core.session_manager import SessionManager
from src.utils.yaml_file_utils import read_common

# 初始化日志
logger = setup_logger('auto_publish_pipeline')


class AutoPublishPipeline:
    """完整的内容生成和发布流水线"""
    
    # 支持的发布平台列表
    PLATFORMS = ['csdn', 'juejin', 'zhihu', 'cto51', 'alicloud', 'toutiao']
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化流水线
        
        Args:
            api_key: 智谱AI API密钥
        """
        self.api_key = api_key or os.environ.get("ZHIPUAI_API_KEY")
        if not self.api_key:
            raise ValueError("请提供智谱AI API Key或设置环境变量 ZHIPUAI_API_KEY")
        
        # 读取配置
        self.common_config = read_common()
        self.session_manager = None
        
        # 统计信息
        self.stats = {
            'generated_articles': 0,
            'total_publishes': 0,
            'success_publishes': 0,
            'failed_publishes': 0,
            'publish_details': []
        }
    
    def get_publisher(self, platform: str):
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
        else:
            logger.warning(f"平台 {platform} 的发布器尚未实现")
            return None
    
    def get_enabled_platforms(self) -> List[str]:
        """
        获取已启用的平台列表
        
        Returns:
            已启用的平台名称列表
        """
        enabled_platforms = self.common_config.get('enable', {})
        return [p for p in self.PLATFORMS if enabled_platforms.get(p, False)]
    
    def publish_article_to_platform(
        self,
        article_path: str,
        platform: str,
        article_index: int,
        total_articles: int,
        platform_index: int,
        total_platforms: int
    ) -> bool:
        """
        发布单篇文章到指定平台
        
        Args:
            article_path: 文章路径
            platform: 平台名称
            article_index: 当前文章索引（从1开始）
            total_articles: 文章总数
            platform_index: 当前平台索引（从1开始）
            total_platforms: 平台总数
        
        Returns:
            bool: 是否发布成功
        """
        article_name = os.path.basename(article_path)
        
        logger.info("\n" + "="*80)
        logger.info(f"📄 文章 [{article_index}/{total_articles}]: {article_name}")
        logger.info(f"🚀 平台 [{platform_index}/{total_platforms}]: {platform.upper()}")
        logger.info("="*80)
        
        try:
            publisher = self.get_publisher(platform)
            if not publisher:
                logger.error(f"❌ 无法获取 {platform} 的发布器")
                return False
            
            # 设置驱动（复用会话管理器）
            publisher.session_manager = self.session_manager
            publisher.driver = self.session_manager.driver
            
            # 执行发布
            logger.info(f"⏳ 开始发布到 {platform.upper()}...")
            success = publisher.publish(article_path)
            
            if success:
                logger.info(f"✅ {platform.upper()} 发布成功！")
            else:
                logger.error(f"❌ {platform.upper()} 发布失败")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ {platform.upper()} 发布过程中发生错误：{e}", exc_info=True)
            return False
    
    def publish_all_articles(
        self,
        article_paths: List[str],
        platforms: List[str],
        delay_between_publishes: float = 3.0
    ):
        """
        发布所有文章到所有平台（双层循环）
        
        Args:
            article_paths: 文章路径列表
            platforms: 平台名称列表
            delay_between_publishes: 发布之间的延迟（秒）
        """
        total_articles = len(article_paths)
        total_platforms = len(platforms)
        total_tasks = total_articles * total_platforms
        
        logger.info("\n" + "="*80)
        logger.info("🚀 开始批量发布流程")
        logger.info("="*80)
        logger.info(f"📊 文章数量: {total_articles}")
        logger.info(f"📊 平台数量: {total_platforms}")
        logger.info(f"📊 总发布任务: {total_tasks}")
        logger.info(f"⏱️  预计耗时: 约 {(total_tasks * delay_between_publishes) / 60:.1f} 分钟")
        logger.info("="*80 + "\n")
        
        current_task = 0
        
        # 外层循环：遍历每篇文章
        for article_idx, article_path in enumerate(article_paths, 1):
            article_name = os.path.basename(article_path)
            
            logger.info("\n" + "🔹"*40)
            logger.info(f"📝 开始发布文章 [{article_idx}/{total_articles}]: {article_name}")
            logger.info("🔹"*40 + "\n")
            
            article_success_count = 0
            article_fail_count = 0
            
            # 内层循环：遍历每个平台
            for platform_idx, platform in enumerate(platforms, 1):
                current_task += 1
                
                logger.info(f"\n进度: [{current_task}/{total_tasks}] 正在发布...")
                
                # 发布到平台
                success = self.publish_article_to_platform(
                    article_path=article_path,
                    platform=platform,
                    article_index=article_idx,
                    total_articles=total_articles,
                    platform_index=platform_idx,
                    total_platforms=total_platforms
                )
                
                # 更新统计
                self.stats['total_publishes'] += 1
                if success:
                    self.stats['success_publishes'] += 1
                    article_success_count += 1
                else:
                    self.stats['failed_publishes'] += 1
                    article_fail_count += 1
                
                # 记录详情
                self.stats['publish_details'].append({
                    'article': article_name,
                    'platform': platform,
                    'success': success
                })
                
                # 延迟（避免请求过快）
                if current_task < total_tasks:
                    logger.info(f"⏳ 等待 {delay_between_publishes} 秒后继续...")
                    time.sleep(delay_between_publishes)
            
            # 文章发布完成统计
            logger.info("\n" + "🔹"*40)
            logger.info(f"✅ 文章 [{article_idx}/{total_articles}] 发布完成")
            logger.info(f"   成功: {article_success_count}/{total_platforms}")
            logger.info(f"   失败: {article_fail_count}/{total_platforms}")
            logger.info("🔹"*40 + "\n")
        
        # 最终统计
        self._print_final_report()
    
    def _print_final_report(self):
        """打印最终发布报告"""
        logger.info("\n" + "="*80)
        logger.info("📊 批量发布完成 - 总体报告")
        logger.info("="*80)
        logger.info(f"总发布任务: {self.stats['total_publishes']}")
        logger.info(f"成功: {self.stats['success_publishes']}")
        logger.info(f"失败: {self.stats['failed_publishes']}")
        
        if self.stats['total_publishes'] > 0:
            success_rate = (self.stats['success_publishes'] / self.stats['total_publishes']) * 100
            logger.info(f"成功率: {success_rate:.1f}%")
        
        logger.info("\n" + "-"*80)
        logger.info("📋 详细发布记录:")
        logger.info("-"*80)
        
        # 按文章分组显示
        from collections import defaultdict
        by_article = defaultdict(list)
        for detail in self.stats['publish_details']:
            by_article[detail['article']].append(detail)
        
        for article_name, details in by_article.items():
            logger.info(f"\n📄 {article_name}")
            for detail in details:
                status = "✅" if detail['success'] else "❌"
                logger.info(f"   {status} {detail['platform'].upper()}")
        
        logger.info("\n" + "="*80 + "\n")
    
    def initialize_browser(self):
        """初始化浏览器"""
        logger.info("🌐 初始化浏览器...")
        
        try:
            self.session_manager = SessionManager('common', self.common_config)
            self.session_manager.create_driver(use_existing=True)
            logger.info("✅ 浏览器驱动初始化完成")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ 连接Chrome失败：{error_msg}")
            
            if 'cannot connect to chrome' in error_msg.lower() or 'unable to discover open pages' in error_msg.lower():
                logger.error("\n" + "="*80)
                logger.error("⚠️  无法连接到 Chrome 调试模式")
                logger.error("="*80)
                logger.error("\n请先启动 Chrome 调试模式：")
                logger.error("\n方法1：使用脚本启动（推荐）")
                logger.error("  bash scripts/start_chrome.sh")
                logger.error("\n方法2：手动启动")
                logger.error("  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\")
                logger.error("    --remote-debugging-port=9222 \\")
                logger.error("    --user-data-dir=\"/tmp/chrome_dev\" \\")
                logger.error("    about:blank")
                logger.error("\n" + "="*80 + "\n")
            
            return False
    
    def run(
        self,
        news_limit: int = 10,
        article_limit: int = 5,
        search_depth: str = "quick",
        delay: float = 2.0,
        publish_delay: float = 3.0,
        skip_generation: bool = False
    ):
        """
        运行完整流水线
        
        Args:
            news_limit: 抓取的新闻数量
            article_limit: 生成的文章数量
            search_depth: 搜索深度 "quick" 或 "deep"
            delay: 内容生成时的API请求延迟
            publish_delay: 发布时的延迟
            skip_generation: 是否跳过内容生成（直接发布已有文章）
        """
        logger.info("\n" + "="*80)
        logger.info("🚀 自动化内容生成与发布流水线")
        logger.info("="*80 + "\n")
        
        article_paths = []
        
        try:
            # 步骤1：生成内容
            if not skip_generation:
                logger.info("📝 [阶段 1/2] 内容生成")
                logger.info("-"*80 + "\n")
                
                content_pipeline = AutoContentPipeline(
                    api_key=self.api_key,
                    output_dir="posts",
                    data_dir="data/generated"
                )
                
                stats = content_pipeline.run(
                    news_limit=news_limit,
                    article_limit=article_limit,
                    search_depth=search_depth,
                    request_delay=delay,
                    save_intermediate=True
                )
                
                self.stats['generated_articles'] = stats['generated_articles']
                
                if stats['generated_articles'] == 0:
                    logger.error("❌ 没有成功生成任何文章，流水线终止")
                    return
                
                # 获取生成的文章路径
                import json
                generated_file = Path("data/generated/03_generated_articles.json")
                if generated_file.exists():
                    with open(generated_file, 'r', encoding='utf-8') as f:
                        generated_articles = json.load(f)
                        article_paths = [article['file_path'] for article in generated_articles]
                
                logger.info(f"\n✅ 内容生成完成，共生成 {len(article_paths)} 篇文章\n")
            
            else:
                # 跳过生成，使用现有文章
                logger.info("⏭️  跳过内容生成，使用现有文章")
                posts_dir = Path("posts")
                if posts_dir.exists():
                    article_paths = [str(f) for f in posts_dir.glob("*.md")]
                    logger.info(f"✅ 找到 {len(article_paths)} 篇现有文章\n")
                else:
                    logger.error("❌ posts 目录不存在，无文章可发布")
                    return
            
            if not article_paths:
                logger.error("❌ 没有可发布的文章")
                return
            
            # 步骤2：初始化浏览器
            logger.info("\n" + "="*80)
            logger.info("🌐 [阶段 2/3] 初始化浏览器")
            logger.info("-"*80 + "\n")
            
            if not self.initialize_browser():
                logger.error("❌ 浏览器初始化失败，无法继续发布")
                return
            
            # 步骤3：批量发布
            logger.info("\n" + "="*80)
            logger.info("📤 [阶段 3/3] 批量发布")
            logger.info("-"*80 + "\n")
            
            # 获取启用的平台
            enabled_platforms = self.get_enabled_platforms()
            
            if not enabled_platforms:
                logger.error("❌ 没有启用任何发布平台，请检查配置文件")
                logger.info("   配置文件路径: config/common.yaml")
                logger.info("   请在 enable 部分启用需要的平台")
                return
            
            logger.info(f"📋 启用的平台: {', '.join(p.upper() for p in enabled_platforms)}")
            
            # 执行批量发布
            self.publish_all_articles(
                article_paths=article_paths,
                platforms=enabled_platforms,
                delay_between_publishes=publish_delay
            )
            
            logger.info("\n🎉 流水线执行完成！")
            
        except KeyboardInterrupt:
            logger.info("\n\n⚠️  用户中断流水线")
        except Exception as e:
            logger.error(f"\n\n❌ 流水线执行失败: {e}", exc_info=True)
        finally:
            # 清理资源
            if self.session_manager:
                self.session_manager.close()
            logger.info("\n👋 程序退出\n")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='完整的内容生成和发布闭环流水线'
    )
    
    parser.add_argument(
        '--news-limit',
        type=int,
        default=10,
        help='抓取的新闻数量（默认: 10）'
    )
    
    parser.add_argument(
        '--article-limit',
        type=int,
        default=1,
        help='生成的文章数量（默认: 1）'
    )
    
    parser.add_argument(
        '--search-depth',
        choices=['quick', 'deep'],
        default='quick',
        help='搜索深度：quick=快速, deep=深度（默认: quick）'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='内容生成时的API请求间隔秒数（默认: 2.0）'
    )
    
    parser.add_argument(
        '--publish-delay',
        type=float,
        default=3.0,
        help='发布时的延迟秒数（默认: 3.0）'
    )
    
    parser.add_argument(
        '--skip-generation',
        action='store_true',
        help='跳过内容生成，直接发布已有文章'
    )
    
    parser.add_argument(
        '--api-key',
        help='智谱AI API密钥（可通过环境变量ZHIPUAI_API_KEY设置）'
    )
    
    args = parser.parse_args()
    
    try:
        # 创建流水线
        pipeline = AutoPublishPipeline(api_key=args.api_key)
        
        # 运行流水线
        pipeline.run(
            news_limit=args.news_limit,
            article_limit=args.article_limit,
            search_depth=args.search_depth,
            delay=args.delay,
            publish_delay=args.publish_delay,
            skip_generation=args.skip_generation
        )
        
    except Exception as e:
        logger.error(f"\n❌ 执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

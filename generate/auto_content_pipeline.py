#!/usr/bin/env python3
"""
auto_content_pipeline.py

自动化内容生成流水线
从抓取热点 -> 搜索资料 -> 生成文章 -> 保存发布的完整流程
"""

import os
import sys
import json
import time
import argparse
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate.qbitai_crawler import QbitAICrawler
from generate.aibase_crawler import AIBaseCrawler
from generate.reference_searcher import ReferenceSearcher
from generate.enhanced_content_generator import EnhancedContentGenerator


class AutoContentPipeline:
    """自动化内容生成流水线"""
    
    # 新闻源映射
    CRAWLER_MAP = {
        'qbitai': QbitAICrawler,
        'aibase': AIBaseCrawler
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        output_dir: str = "posts",
        data_dir: str = "data/generated",
        news_sources: Optional[str] = None
    ):
        """
        初始化流水线
        
        Args:
            api_key: 智谱AI API密钥
            output_dir: 文章输出目录
            data_dir: 中间数据保存目录
            news_sources: 新闻源配置，逗号分隔（如 "aibase,qbitai"），为空则从配置文件读取
        """
        self.api_key = api_key or os.environ.get("ZHIPUAI_API_KEY")
        if not self.api_key:
            raise ValueError("请提供智谱AI API Key或设置环境变量 ZHIPUAI_API_KEY")
        
        self.output_dir = output_dir
        self.data_dir = data_dir
        
        # 确保目录存在
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        # 加载新闻源配置
        self.news_sources = self._load_news_sources(news_sources)
        
        # 初始化爬虫列表
        self.crawlers = self._init_crawlers()
        
        # 初始化其他组件
        self.searcher = ReferenceSearcher(api_key=self.api_key)
        self.generator = EnhancedContentGenerator(api_key=self.api_key)
        
        # 统计信息
        self.stats = {
            'crawled_news': 0,
            'searched_references': 0,
            'generated_articles': 0,
            'failed_articles': 0,
            'start_time': None,
            'end_time': None,
            'news_sources': self.news_sources
        }
    
    def _load_news_sources(self, news_sources: Optional[str]) -> List[str]:
        """
        加载新闻源配置
        
        Args:
            news_sources: 命令行指定的新闻源
            
        Returns:
            新闻源列表
        """
        # 如果命令行指定了新闻源，使用命令行的
        if news_sources:
            sources = [s.strip().lower() for s in news_sources.split(',')]
        else:
            # 否则从配置文件读取
            try:
                config_path = Path(__file__).parent.parent / "config" / "common.yaml"
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    sources_str = config.get('news_sources', 'aibase')
                    sources = [s.strip().lower() for s in sources_str.split(',')]
            except Exception as e:
                print(f"⚠️ 读取配置文件失败: {e}，使用默认新闻源: aibase")
                sources = ['aibase']
        
        # 验证新闻源是否支持
        valid_sources = []
        for source in sources:
            if source in self.CRAWLER_MAP:
                valid_sources.append(source)
            else:
                print(f"⚠️ 不支持的新闻源: {source}，已跳过")
        
        if not valid_sources:
            print("⚠️ 没有有效的新闻源，使用默认: aibase")
            valid_sources = ['aibase']
        
        return valid_sources
    
    def _init_crawlers(self) -> List:
        """
        初始化爬虫实例
        
        Returns:
            爬虫实例列表
        """
        crawlers = []
        for source in self.news_sources:
            crawler_class = self.CRAWLER_MAP.get(source)
            if crawler_class:
                crawlers.append({
                    'name': source,
                    'instance': crawler_class()
                })
        return crawlers
    
    def run(
        self,
        news_limit: int = 10,
        article_limit: int = 5,
        search_depth: str = "quick",
        request_delay: float = 2.0,
        save_intermediate: bool = True
    ) -> Dict[str, any]:
        """
        运行完整流水线
        
        Args:
            news_limit: 每个新闻源抓取的新闻数量
            article_limit: 生成的文章数量（从所有抓取的新闻中选取）
            search_depth: 搜索深度 "quick" 或 "deep"
            request_delay: API请求间隔（秒）
            save_intermediate: 是否保存中间结果
            
        Returns:
            包含统计信息的字典
        """
        self.stats['start_time'] = datetime.now()
        
        print("\n" + "="*80)
        print("🚀 自动化内容生成流水线启动")
        print("="*80)
        print(f"新闻源: {', '.join(self.news_sources)}")
        print(f"每个源抓取新闻数: {news_limit}")
        print(f"生成文章数: {article_limit}")
        print(f"搜索深度: {search_depth}")
        print(f"输出目录: {self.output_dir}")
        print("="*80 + "\n")
        
        try:
            # 第一步：从多个新闻源抓取热点新闻
            print("\n" + "="*80)
            print("📡 [步骤 1/4] 抓取热点新闻")
            print("="*80 + "\n")
            
            all_news = []
            for crawler_info in self.crawlers:
                source_name = crawler_info['name']
                crawler = crawler_info['instance']
                
                print(f"\n📰 正在抓取 {source_name.upper()} 新闻源...")
                news_list = crawler.fetch_top_news(limit=news_limit)
                
                # 为每条新闻添加来源标记
                for news in news_list:
                    news['news_source'] = source_name
                
                all_news.extend(news_list)
                print(f"✅ {source_name.upper()}: 成功抓取 {len(news_list)} 条新闻")
            
            self.stats['crawled_news'] = len(all_news)
            
            if not all_news:
                print("❌ 未抓取到任何新闻，流水线终止")
                return self.stats
            
            if save_intermediate:
                self._save_json(all_news, "01_crawled_news.json")
            
            print(f"\n✅ 总计抓取 {len(all_news)} 条新闻")
            print(f"   来源分布: {self._count_by_source(all_news)}\n")
            
            # 选择要生成文章的新闻（取前 article_limit 条）
            selected_news = all_news[:article_limit]
            print(f"📌 选择前 {len(selected_news)} 条新闻生成文章\n")
            
            # 第二步：搜索参考资料
            print("\n" + "="*80)
            print("🔍 [步骤 2/4] 搜索参考资料")
            print("="*80 + "\n")
            
            all_references = []
            for idx, news in enumerate(selected_news, 1):
                print(f"\n--- [{idx}/{len(selected_news)}] 搜索: {news['title'][:50]}... ---")
                
                try:
                    references = self.searcher.search_topic_references(
                        topic=news['title'],
                        original_summary=news.get('summary', ''),
                        search_depth=search_depth
                    )
                    all_references.append(references)
                    self.stats['searched_references'] += 1
                    
                    # API请求限流
                    if idx < len(selected_news):
                        print(f"\n⏳ 等待 {request_delay} 秒...")
                        time.sleep(request_delay)
                        
                except Exception as e:
                    print(f"❌ 搜索失败: {e}")
                    all_references.append({
                        'topic': news['title'],
                        'error': str(e)
                    })
            
            if save_intermediate:
                self._save_json(all_references, "02_search_references.json")
            
            print(f"\n✅ 完成 {len(all_references)} 个话题的资料搜索\n")
            
            # 第三步：生成文章
            print("\n" + "="*80)
            print("✍️  [步骤 3/4] 生成文章")
            print("="*80 + "\n")
            
            generated_articles = []
            for idx, (news, references) in enumerate(zip(selected_news, all_references), 1):
                print(f"\n--- [{idx}/{len(selected_news)}] 生成文章 ---")
                
                try:
                    # 检查是否有搜索错误
                    if 'error' in references:
                        print(f"⚠️ 跳过（搜索失败）: {news['title'][:50]}...")
                        self.stats['failed_articles'] += 1
                        continue
                    
                    article = self.generator.generate_article_from_news(
                        news_item=news,
                        references=references,
                        style="qbitai",
                        output_dir=self.output_dir
                    )
                    
                    generated_articles.append({
                        'title': article['title'],
                        'file_path': article['file_path'],
                        'tags': article['tags'],
                        'original_title': news['title']
                    })
                    
                    self.stats['generated_articles'] += 1
                    
                    # API请求限流
                    if idx < len(selected_news):
                        print(f"\n⏳ 等待 {request_delay} 秒...")
                        time.sleep(request_delay)
                    
                except Exception as e:
                    print(f"❌ 文章生成失败: {e}")
                    self.stats['failed_articles'] += 1
            
            if save_intermediate:
                self._save_json(generated_articles, "03_generated_articles.json")
            
            # 第四步：生成报告
            print("\n" + "="*80)
            print("📊 [步骤 4/4] 生成运行报告")
            print("="*80 + "\n")
            
            self.stats['end_time'] = datetime.now()
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            self.stats['duration_seconds'] = duration
            
            report = self._generate_report(generated_articles)
            
            if save_intermediate:
                self._save_text(report, "04_pipeline_report.txt")
            
            print(report)
            
            return self.stats
            
        except KeyboardInterrupt:
            print("\n\n⚠️ 用户中断流水线")
            return self.stats
        except Exception as e:
            print(f"\n\n❌ 流水线执行失败: {e}")
            import traceback
            traceback.print_exc()
            return self.stats
    
    def _save_json(self, data: any, filename: str):
        """保存JSON数据"""
        file_path = Path(self.data_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 中间数据已保存: {file_path}")
    
    def _save_text(self, text: str, filename: str):
        """保存文本数据"""
        file_path = Path(self.data_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"💾 报告已保存: {file_path}")
    
    def _count_by_source(self, news_list: List[Dict]) -> str:
        """
        统计各新闻源的新闻数量
        
        Args:
            news_list: 新闻列表
            
        Returns:
            格式化的统计字符串
        """
        counts = {}
        for news in news_list:
            source = news.get('news_source', 'unknown')
            counts[source] = counts.get(source, 0) + 1
        
        return ', '.join([f"{k}={v}" for k, v in counts.items()])
    
    def _generate_report(self, articles: List[Dict]) -> str:
        """生成运行报告"""
        duration_minutes = self.stats['duration_seconds'] / 60
        
        report = f"""
{'='*80}
📊 内容生成流水线运行报告
{'='*80}

⏰ 运行时间
   开始时间: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}
   结束时间: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}
   总耗时: {duration_minutes:.2f} 分钟

🌐 新闻源配置
   使用的新闻源: {', '.join(self.stats['news_sources'])}

📈 统计信息
   抓取新闻: {self.stats['crawled_news']} 条
   搜索资料: {self.stats['searched_references']} 个话题
   成功生成: {self.stats['generated_articles']} 篇文章
   失败数量: {self.stats['failed_articles']} 篇
   成功率: {self.stats['generated_articles']/(self.stats['generated_articles']+self.stats['failed_articles'])*100 if (self.stats['generated_articles']+self.stats['failed_articles'])>0 else 0:.1f}%

📝 生成的文章列表
"""
        
        if articles:
            for idx, article in enumerate(articles, 1):
                report += f"""
   [{idx}] {article['title']}
       原标题: {article['original_title']}
       标签: {', '.join(article['tags'])}
       文件: {article['file_path']}
"""
        else:
            report += "   （无）\n"
        
        report += f"""
{'='*80}
✅ 报告生成完成
{'='*80}
"""
        
        return report


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='自动化内容生成流水线：抓取 -> 搜索 -> 生成 -> 发布'
    )
    
    parser.add_argument(
        '--news-limit',
        type=int,
        default=10,
        help='每个新闻源抓取的新闻数量（默认: 10）'
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
        help='API请求间隔秒数（默认: 2.0）'
    )
    
    parser.add_argument(
        '--output-dir',
        default='posts',
        help='文章输出目录（默认: posts）'
    )
    
    parser.add_argument(
        '--data-dir',
        default='data/generated',
        help='中间数据目录（默认: data/generated）'
    )
    
    parser.add_argument(
        '--api-key',
        help='智谱AI API密钥（可通过环境变量ZHIPUAI_API_KEY设置）'
    )
    
    parser.add_argument(
        '--news-sources',
        help='新闻源，逗号分隔（如: aibase,qbitai）。不指定则从配置文件读取'
    )
    
    args = parser.parse_args()
    
    try:
        # 创建流水线
        pipeline = AutoContentPipeline(
            api_key=args.api_key,
            output_dir=args.output_dir,
            data_dir=args.data_dir,
            news_sources=args.news_sources
        )
        
        # 运行流水线
        stats = pipeline.run(
            news_limit=args.news_limit,
            article_limit=args.article_limit,
            search_depth=args.search_depth,
            request_delay=args.delay,
            save_intermediate=True
        )
        
        # 输出最终统计
        print("\n" + "="*80)
        print("🎉 流水线执行完成")
        print("="*80)
        print(f"成功生成 {stats['generated_articles']} 篇文章")
        print(f"输出目录: {args.output_dir}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

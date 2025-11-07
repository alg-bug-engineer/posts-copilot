#!/usr/bin/env python3
"""
test_news_sources.py

测试多新闻源功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate.aibase_crawler import AIBaseCrawler
from generate.qbitai_crawler import QbitAICrawler


def test_crawler(crawler_name, crawler_class, limit=5):
    """测试单个爬虫"""
    print(f"\n{'='*80}")
    print(f"🧪 测试 {crawler_name} 爬虫")
    print(f"{'='*80}\n")
    
    try:
        crawler = crawler_class()
        news_list = crawler.fetch_top_news(limit=limit)
        
        if news_list:
            print(f"\n✅ {crawler_name} 测试成功！")
            print(f"   抓取了 {len(news_list)} 条新闻")
            print(f"\n   示例新闻：")
            for idx, news in enumerate(news_list[:3], 1):
                print(f"   [{idx}] {news['title'][:60]}...")
                print(f"       链接: {news['url']}")
                print(f"       时间: {news.get('time', 'N/A')}")
        else:
            print(f"❌ {crawler_name} 测试失败：未抓取到新闻")
            
    except Exception as e:
        print(f"❌ {crawler_name} 测试失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("🚀 多新闻源功能测试")
    print("="*80)
    
    # 测试 AIBase 爬虫
    test_crawler("AIBase", AIBaseCrawler, limit=5)
    
    # 测试量子位爬虫
    test_crawler("量子位", QbitAICrawler, limit=5)
    
    print("\n" + "="*80)
    print("✅ 所有测试完成")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

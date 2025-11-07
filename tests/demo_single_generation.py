#!/usr/bin/env python3
"""
demo_single_generation.py

生成单篇文章进行测试
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generate.qbitai_crawler import QbitAICrawler
from generate.reference_searcher import ReferenceSearcher
from generate.enhanced_content_generator import EnhancedContentGenerator


def main():
    print("🚀 开始生成测试文章...\n")
    
    # 1. 爬取一条新闻
    print("📰 爬取qbitai新闻...")
    crawler = QbitAICrawler()
    news_list = crawler.fetch_top_news(max_count=1)
    
    if not news_list:
        print("❌ 未获取到新闻")
        return
    
    news = news_list[0]
    print(f"✅ 获取新闻: {news['title']}\n")
    
    # 2. 搜索参考资料
    print("🔍 搜索参考资料...")
    searcher = ReferenceSearcher()
    references = searcher.search_topic_references(
        topic=news['title'],
        quick_mode=False  # 使用深度模式
    )
    print(f"✅ 获取 {len(references)} 条参考资料\n")
    
    # 3. 生成文章
    print("✍️ 生成文章...")
    generator = EnhancedContentGenerator()
    
    result = generator.generate_article(
        topic=news['title'],
        original_content={
            'title': news['title'],
            'url': news['url'],
            'summary': news['summary'],
            'tags': news['tags']
        },
        references=references
    )
    
    if result['success']:
        print(f"✅ 文章生成成功！")
        print(f"📄 文件路径: {result['file_path']}")
        print(f"📝 标题: {result['title']}")
        print(f"📊 字数: {result['word_count']}")
        
        # 读取并显示部分内容
        with open(result['file_path'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除Front Matter
        import re
        content_body = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
        
        print(f"\n{'='*80}")
        print("📖 文章预览（前500字符）:")
        print(f"{'='*80}")
        print(content_body[:500])
        print("...")
        print(f"{'='*80}\n")
        
        # 运行质量测试
        print("🧪 运行质量测试...\n")
        os.system(f"python3 tests/test_content_quality.py '{result['file_path']}'")
        
    else:
        print(f"❌ 文章生成失败: {result['error']}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
test_content_generation.py

内容生成模块的集成测试
测试各个组件的基本功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_crawler():
    """测试量子位爬虫"""
    print("\n" + "="*70)
    print("🧪 测试 1: 量子位新闻爬虫")
    print("="*70 + "\n")
    
    try:
        from generate.qbitai_crawler import QbitAICrawler
        
        crawler = QbitAICrawler()
        news_list = crawler.fetch_top_news(limit=3)
        
        assert len(news_list) > 0, "未抓取到任何新闻"
        assert 'title' in news_list[0], "新闻缺少标题字段"
        assert 'url' in news_list[0], "新闻缺少URL字段"
        
        print(f"✅ 测试通过: 成功抓取 {len(news_list)} 条新闻")
        print(f"   示例: {news_list[0]['title'][:50]}...")
        
        return True, news_list
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False, []


def test_reference_searcher(news_list):
    """测试参考资料搜索"""
    print("\n" + "="*70)
    print("🧪 测试 2: 参考资料搜索")
    print("="*70 + "\n")
    
    if not news_list:
        print("⚠️ 跳过测试: 没有可用的新闻数据")
        return False, None
    
    # 检查API密钥
    api_key = os.environ.get("ZHIPUAI_API_KEY")
    if not api_key:
        print("⚠️ 跳过测试: 未设置 ZHIPUAI_API_KEY 环境变量")
        return False, None
    
    try:
        from generate.reference_searcher import ReferenceSearcher
        
        searcher = ReferenceSearcher()
        
        test_news = news_list[0]
        print(f"测试话题: {test_news['title'][:50]}...")
        
        references = searcher.search_topic_references(
            topic=test_news['title'],
            original_summary=test_news.get('summary', ''),
            search_depth="quick"
        )
        
        assert references is not None, "搜索返回空结果"
        assert 'topic' in references, "搜索结果缺少topic字段"
        
        print(f"✅ 测试通过: 成功搜索参考资料")
        print(f"   技术背景长度: {len(references.get('technical_background', ''))} 字符")
        print(f"   关键创新点: {len(references.get('key_innovations', []))} 个")
        
        return True, references
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_content_generator(news_list, references):
    """测试内容生成器"""
    print("\n" + "="*70)
    print("🧪 测试 3: 内容生成器")
    print("="*70 + "\n")
    
    if not news_list or not references:
        print("⚠️ 跳过测试: 没有可用的新闻或参考资料")
        return False, None
    
    # 检查API密钥
    api_key = os.environ.get("ZHIPUAI_API_KEY")
    if not api_key:
        print("⚠️ 跳过测试: 未设置 ZHIPUAI_API_KEY 环境变量")
        return False, None
    
    try:
        from generate.enhanced_content_generator import EnhancedContentGenerator
        
        generator = EnhancedContentGenerator()
        
        test_news = news_list[0]
        print(f"生成文章: {test_news['title'][:50]}...")
        
        # 使用测试输出目录
        test_output_dir = "data/test_posts"
        Path(test_output_dir).mkdir(parents=True, exist_ok=True)
        
        article = generator.generate_article_from_news(
            news_item=test_news,
            references=references,
            style="qbitai",
            output_dir=test_output_dir
        )
        
        assert article is not None, "生成返回空结果"
        assert 'title' in article, "生成结果缺少title字段"
        assert 'content' in article, "生成结果缺少content字段"
        assert 'file_path' in article, "生成结果缺少file_path字段"
        
        # 验证文件存在
        assert Path(article['file_path']).exists(), "生成的文件不存在"
        
        print(f"✅ 测试通过: 成功生成文章")
        print(f"   新标题: {article['title'][:50]}...")
        print(f"   标签: {', '.join(article['tags'][:3])}")
        print(f"   文件: {article['file_path']}")
        
        return True, article
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_pipeline():
    """测试完整流水线"""
    print("\n" + "="*70)
    print("🧪 测试 4: 完整流水线（轻量级）")
    print("="*70 + "\n")
    
    # 检查API密钥
    api_key = os.environ.get("ZHIPUAI_API_KEY")
    if not api_key:
        print("⚠️ 跳过测试: 未设置 ZHIPUAI_API_KEY 环境变量")
        return False
    
    try:
        from generate.auto_content_pipeline import AutoContentPipeline
        
        pipeline = AutoContentPipeline(
            output_dir="data/test_posts",
            data_dir="data/test_generated"
        )
        
        print("运行轻量级流水线（1条新闻 -> 1篇文章）...")
        
        stats = pipeline.run(
            news_limit=3,
            article_limit=1,
            search_depth="quick",
            request_delay=1.0,
            save_intermediate=True
        )
        
        assert stats['crawled_news'] > 0, "未抓取到新闻"
        
        print(f"✅ 测试通过: 流水线执行完成")
        print(f"   抓取新闻: {stats['crawled_news']} 条")
        print(f"   生成文章: {stats['generated_articles']} 篇")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("🚀 内容生成模块集成测试")
    print("="*80)
    
    results = []
    
    # 测试1: 爬虫
    success, news_list = test_crawler()
    results.append(("爬虫测试", success))
    
    # 测试2: 搜索
    success, references = test_reference_searcher(news_list)
    results.append(("搜索测试", success))
    
    # 测试3: 生成器
    success, article = test_content_generator(news_list, references)
    results.append(("生成器测试", success))
    
    # 测试4: 流水线
    success = test_pipeline()
    results.append(("流水线测试", success))
    
    # 汇总结果
    print("\n" + "="*80)
    print("📊 测试结果汇总")
    print("="*80 + "\n")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}  {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

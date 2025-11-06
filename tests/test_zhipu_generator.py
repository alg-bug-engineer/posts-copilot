#!/usr/bin/env python3
"""
测试智谱内容生成器
"""

from generate.zhipu_content_generator import ZhipuContentGenerator
from pathlib import Path


def test_generate_article():
    """测试生成文章"""
    print("\n" + "="*60)
    print("智谱AI内容生成器测试")
    print("="*60 + "\n")
    
    # 测试关键词
    test_keywords = ["RAG", "大模型微调", "Prompt工程"]
    
    try:
        # 初始化生成器
        print("正在初始化生成器...")
        generator = ZhipuContentGenerator()
        print("✓ 生成器初始化成功\n")
        
        # 选择关键词
        print("可选关键词：")
        for i, keyword in enumerate(test_keywords, 1):
            print(f"{i}. {keyword}")
        
        choice = input("\n请选择关键词序号（直接回车使用第1个）: ").strip()
        
        if choice and choice.isdigit() and 1 <= int(choice) <= len(test_keywords):
            keyword = test_keywords[int(choice) - 1]
        else:
            keyword = test_keywords[0]
        
        print(f"\n已选择关键词: {keyword}\n")
        
        # 生成文章
        result = generator.generate_article_with_keyword(
            keyword=keyword,
            auto_generate_title=True,
            min_words=1500,
            max_words=2500
        )
        
        # 保存文章
        output_dir = Path.cwd() / "posts"
        filepath = generator.save_article_to_file(
            content=result['content'],
            title=result['title'],
            output_dir=output_dir
        )
        
        # 输出结果
        print("\n" + "="*60)
        print("✅ 测试成功！")
        print("="*60)
        print(f"\n📄 标题: {result['title']}")
        print(f"\n📝 描述: {result['description']}")
        print(f"\n🏷️  标签:")
        for tag in result['tags']:
            print(f"   - {tag}")
        print(f"\n💾 文件: {filepath}")
        print(f"\n📊 内容长度: {len(result['content_without_frontmatter'])} 字符")
        print("\n" + "="*60 + "\n")
        
        # 预览前200个字符
        print("📖 内容预览（前200字符）:")
        print("-" * 60)
        preview = result['content_without_frontmatter'][:200]
        print(preview + "...")
        print("-" * 60 + "\n")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断测试")
        return False
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generate_titles():
    """测试生成标题"""
    print("\n" + "="*60)
    print("测试标题生成功能")
    print("="*60 + "\n")
    
    try:
        generator = ZhipuContentGenerator()
        
        keyword = input("请输入关键词（直接回车使用 'AI'）: ").strip() or "AI"
        
        print(f"\n正在生成关于 '{keyword}' 的标题...\n")
        
        titles = generator.generate_titles(keyword=keyword, count=5)
        
        print("✓ 标题生成成功：\n")
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
        
        print(f"\n{'='*60}\n")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n欢迎使用智谱AI内容生成器测试工具\n")
    print("请选择测试项目：")
    print("1. 测试完整文章生成（包含Front Matter）")
    print("2. 测试标题生成")
    print("0. 退出")
    
    choice = input("\n请选择: ").strip()
    
    if choice == "1":
        test_generate_article()
    elif choice == "2":
        test_generate_titles()
    elif choice == "0":
        print("再见！")
    else:
        print("无效选择")


if __name__ == "__main__":
    main()

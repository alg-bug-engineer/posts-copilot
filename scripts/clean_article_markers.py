#!/usr/bin/env python3
"""
clean_article_markers.py

清理文章中的AI生成标记
清理【文章标题】、【主体内容】、【开篇部分】等标记
"""

import os
import re
import sys
from pathlib import Path


def clean_markers(content: str) -> str:
    """
    清理内容中的标记
    
    Args:
        content: 原始内容
        
    Returns:
        清理后的内容
    """
    # 定义需要清理的标记模式
    markers_to_remove = [
        r'【文章标题】\s*\n*',
        r'【开篇部分】\s*\n*',
        r'【主体内容】\s*\n*',
        r'【结尾部分】\s*\n*',
        r'【正文】\s*\n*',
        r'【内容】\s*\n*',
        r'【标题】\s*\n*',
        r'【摘要】\s*\n*',
        r'【导语】\s*\n*',
        r'【核心内容】\s*\n*',
        r'【技术分析】\s*\n*',
        r'【市场影响】\s*\n*',
        r'【结语】\s*\n*',
        r'【总结】\s*\n*',
    ]
    
    # 逐个清理标记
    for pattern in markers_to_remove:
        content = re.sub(pattern, '', content)
    
    # 清理连续的多个空行，最多保留一个空行
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # 清理开头和结尾的多余空白
    content = content.strip()
    
    return content


def clean_article_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    清理单个文章文件
    
    Args:
        file_path: 文件路径
        dry_run: 是否只检查不修改
        
    Returns:
        是否有修改
    """
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 清理标记
        cleaned_content = clean_markers(original_content)
        
        # 检查是否有变化
        if original_content == cleaned_content:
            print(f"  ✓ {file_path.name} - 无需清理")
            return False
        
        if dry_run:
            print(f"  🔍 {file_path.name} - 发现需要清理的标记（预览模式）")
            return True
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"  ✅ {file_path.name} - 已清理")
        return True
        
    except Exception as e:
        print(f"  ❌ {file_path.name} - 清理失败: {e}")
        return False


def clean_directory(directory: str, dry_run: bool = False):
    """
    清理目录下所有markdown文件
    
    Args:
        directory: 目录路径
        dry_run: 是否只检查不修改
    """
    posts_dir = Path(directory)
    
    if not posts_dir.exists():
        print(f"❌ 目录不存在: {directory}")
        return
    
    # 查找所有markdown文件
    md_files = list(posts_dir.glob("*.md"))
    
    if not md_files:
        print(f"📁 目录中没有找到markdown文件: {directory}")
        return
    
    print(f"\n{'='*70}")
    print(f"🧹 清理文章标记")
    print(f"{'='*70}")
    print(f"目录: {directory}")
    print(f"文件数: {len(md_files)}")
    print(f"模式: {'预览模式（不会修改文件）' if dry_run else '清理模式'}")
    print(f"{'='*70}\n")
    
    modified_count = 0
    
    for md_file in md_files:
        if clean_article_file(md_file, dry_run=dry_run):
            modified_count += 1
    
    print(f"\n{'='*70}")
    if dry_run:
        print(f"📊 预览结果: {modified_count}/{len(md_files)} 个文件需要清理")
        print(f"💡 使用 --apply 参数执行实际清理")
    else:
        print(f"📊 清理完成: {modified_count}/{len(md_files)} 个文件已清理")
    print(f"{'='*70}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='清理文章中的AI生成标记',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览需要清理的文件（不会修改）
  python scripts/clean_article_markers.py
  
  # 执行实际清理
  python scripts/clean_article_markers.py --apply
  
  # 清理指定目录
  python scripts/clean_article_markers.py --dir posts --apply
  
  # 清理单个文件
  python scripts/clean_article_markers.py --file posts/example.md --apply
"""
    )
    
    parser.add_argument(
        '--dir',
        default='posts',
        help='要清理的目录（默认: posts）'
    )
    
    parser.add_argument(
        '--file',
        help='清理单个文件'
    )
    
    parser.add_argument(
        '--apply',
        action='store_true',
        help='执行实际清理（默认只预览）'
    )
    
    args = parser.parse_args()
    
    try:
        if args.file:
            # 清理单个文件
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"❌ 文件不存在: {args.file}")
                sys.exit(1)
            
            print(f"\n🧹 清理文件: {args.file}")
            print(f"模式: {'清理模式' if args.apply else '预览模式'}\n")
            
            if clean_article_file(file_path, dry_run=not args.apply):
                if args.apply:
                    print(f"\n✅ 文件已清理")
                else:
                    print(f"\n💡 使用 --apply 参数执行实际清理")
            else:
                print(f"\n✓ 文件无需清理")
        else:
            # 清理整个目录
            clean_directory(args.dir, dry_run=not args.apply)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
教程系列自动生成系统 - 主控程序
功能：整合 Topic 探索、大纲生成、文章写作三大模块，实现全自动教程生成
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# 导入各模块
from topic_explorer import TopicExplorer
from curriculum_generator import CurriculumGenerator
from article_generator import ArticleGenerator


class TutorialAutoGenerator:
    """教程自动生成系统主控制器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化系统"""
        print("\n" + "="*70)
        print("🚀 教程系列自动生成系统")
        print("="*70 + "\n")
        
        # 加载配置
        if config_path is None:
            config_path = Path(__file__).parent / "tutorial_config.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        print(f"✓ 配置已加载: {config_path}\n")
        
        # 初始化各模块
        print("📦 初始化模块...")
        self.topic_explorer = TopicExplorer(config_path)
        self.curriculum_generator = CurriculumGenerator(config_path)
        self.article_generator = ArticleGenerator(config_path)
        print("✓ 所有模块已就绪\n")
    
    def generate_full_tutorial(
        self, 
        main_topic: str,
        chapter_range: Optional[tuple] = None,
        verbose: bool = True
    ):
        """
        完整流程：从主题探索到生成所有文章
        
        Args:
            main_topic: 主题名称，如 "强化学习"
            chapter_range: 生成的章节范围，如 (1, 3) 表示只生成前3章
            verbose: 是否显示详细过程
        """
        print(f"\n{'='*70}")
        print(f"🎯 开始生成完整教程系列")
        print(f"   主题: {main_topic}")
        if chapter_range:
            print(f"   章节范围: 第{chapter_range[0]}-{chapter_range[1]}章")
        print(f"{'='*70}\n")
        
        try:
            # 步骤1: 探索主题
            print("【步骤 1/3】🔍 探索主题，发现子主题")
            print("-" * 70)
            
            # 检查是否已探索
            existing_topic = self.topic_explorer.get_topic_by_name(main_topic)
            if existing_topic:
                print(f"✓ 主题已探索，跳过此步骤")
                print(f"  子主题数: {len(existing_topic.get('subtopics', []))}\n")
            else:
                self.topic_explorer.explore_topic(main_topic, verbose=verbose)
                # 重新加载数据库，确保其他模块能看到新探索的主题
                self.curriculum_generator.topics_db = self.curriculum_generator._load_json(
                    self.curriculum_generator.topics_db_path
                )
            
            # 步骤2: 生成教程大纲
            print("\n【步骤 2/3】📖 生成教程大纲")
            print("-" * 70)
            
            # 检查是否已生成大纲
            existing_curriculum = self.curriculum_generator.get_curriculum_by_topic(main_topic)
            if existing_curriculum:
                print(f"✓ 教程大纲已存在，跳过此步骤")
                print(f"  章节数: {existing_curriculum.get('total_chapters', 0)}\n")
                curriculum = existing_curriculum
            else:
                curriculum = self.curriculum_generator.generate_curriculum(
                    main_topic, 
                    verbose=verbose
                )
            
            # 步骤3: 生成文章
            print("\n【步骤 3/3】✍️  生成文章")
            print("-" * 70)
            
            # 确保文章生成器有最新的大纲数据
            self.article_generator.curriculum_db = self.article_generator._load_json(
                self.article_generator.curriculum_db_path
            )
            
            if chapter_range:
                results = self.article_generator.generate_series(
                    main_topic,
                    chapter_range=chapter_range,
                    verbose=verbose
                )
            else:
                # 询问是否生成所有章节
                total_chapters = curriculum.get('total_chapters', 0)
                print(f"\n共 {total_chapters} 章，是否全部生成？")
                choice = input("输入 'y' 全部生成，或输入范围如 '1-3'，或 'n' 跳过: ").strip().lower()
                
                if choice == 'y':
                    results = self.article_generator.generate_series(
                        main_topic,
                        verbose=verbose
                    )
                elif '-' in choice:
                    start, end = map(int, choice.split('-'))
                    results = self.article_generator.generate_series(
                        main_topic,
                        chapter_range=(start, end),
                        verbose=verbose
                    )
                else:
                    print("跳过文章生成")
                    results = []
            
            # 完成总结
            print(f"\n{'='*70}")
            print("🎉 教程系列生成完成！")
            print(f"{'='*70}")
            print(f"✓ 主题探索: 完成")
            print(f"✓ 大纲生成: 完成")
            print(f"✓ 文章生成: {len(results)} 篇")
            print(f"\n📁 输出目录: {Path(self.config['storage']['articles_output']).resolve()}")
            print(f"{'='*70}\n")
            
            return {
                "topic": main_topic,
                "curriculum": curriculum,
                "articles": results,
                "success": True
            }
            
        except Exception as e:
            print(f"\n❌ 生成过程出错: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def explore_only(self, topics: list, verbose: bool = True):
        """仅探索主题"""
        print(f"\n{'='*70}")
        print(f"🔍 主题探索模式")
        print(f"{'='*70}\n")
        
        if len(topics) == 1:
            return self.topic_explorer.explore_topic(topics[0], verbose=verbose)
        else:
            return self.topic_explorer.batch_explore(topics, verbose=verbose)
    
    def generate_curriculum_only(self, topic: str, verbose: bool = True):
        """仅生成教程大纲"""
        print(f"\n{'='*70}")
        print(f"📖 大纲生成模式")
        print(f"{'='*70}\n")
        
        curriculum = self.curriculum_generator.generate_curriculum(topic, verbose=verbose)
        
        # 询问是否导出Markdown
        export = input("\n是否导出大纲为Markdown？(y/n): ").strip().lower()
        if export in ['y', 'yes']:
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in topic)
            output_path = Path(f"../posts/curriculum_{safe_name}.md")
            self.curriculum_generator.export_curriculum_markdown(curriculum, output_path)
        
        return curriculum
    
    def generate_articles_only(
        self, 
        topic: str, 
        chapter_range: Optional[tuple] = None,
        verbose: bool = True
    ):
        """仅生成文章"""
        print(f"\n{'='*70}")
        print(f"✍️  文章生成模式")
        print(f"{'='*70}\n")
        
        return self.article_generator.generate_series(
            topic,
            chapter_range=chapter_range,
            verbose=verbose
        )
    
    def list_status(self):
        """显示系统状态"""
        print(f"\n{'='*70}")
        print("📊 系统状态")
        print(f"{'='*70}\n")
        
        # 主题库状态
        topics = self.topic_explorer.get_all_topics()
        print(f"📚 已探索主题: {len(topics)} 个")
        for i, topic in enumerate(topics[:5], 1):
            print(f"   {i}. {topic['main_topic']} ({len(topic.get('subtopics', []))} 个子主题)")
        if len(topics) > 5:
            print(f"   ... 还有 {len(topics) - 5} 个")
        print()
        
        # 大纲库状态
        curriculums = self.curriculum_generator.get_all_curriculums()
        print(f"📖 已生成大纲: {len(curriculums)} 个")
        for i, curr in enumerate(curriculums[:5], 1):
            print(f"   {i}. {curr.get('curriculum_name', 'N/A')} ({curr.get('total_chapters', 0)} 章)")
        if len(curriculums) > 5:
            print(f"   ... 还有 {len(curriculums) - 5} 个")
        print()
        
        # 文章生成历史
        history = self.article_generator.history_db.get("generations", [])
        print(f"✍️  已生成文章: {len(history)} 篇")
        
        # 按主题统计
        topic_stats = {}
        for gen in history:
            topic = gen.get('topic', 'Unknown')
            topic_stats[topic] = topic_stats.get(topic, 0) + 1
        
        for topic, count in list(topic_stats.items())[:5]:
            print(f"   {topic}: {count} 篇")
        print()
    
    def close(self):
        """关闭系统"""
        self.article_generator.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='教程系列自动生成系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:

  # 完整流程：探索 -> 大纲 -> 生成所有文章
  python tutorial_auto_generator.py -t "强化学习" --full
  
  # 完整流程但只生成前3章
  python tutorial_auto_generator.py -t "强化学习" --full -r 1-3
  
  # 仅探索主题
  python tutorial_auto_generator.py -t "Vision Language Action Model" --explore-only
  
  # 仅生成大纲
  python tutorial_auto_generator.py -t "强化学习" --curriculum-only
  
  # 仅生成文章（需要已有大纲）
  python tutorial_auto_generator.py -t "强化学习" --articles-only -r 1-5
  
  # 查看系统状态
  python tutorial_auto_generator.py --status
  
  # 交互模式
  python tutorial_auto_generator.py
        """
    )
    
    parser.add_argument('-t', '--topic', type=str, help='主题名称')
    parser.add_argument('--full', action='store_true', help='完整流程：探索+大纲+文章')
    parser.add_argument('--explore-only', action='store_true', help='仅探索主题')
    parser.add_argument('--curriculum-only', action='store_true', help='仅生成大纲')
    parser.add_argument('--articles-only', action='store_true', help='仅生成文章')
    parser.add_argument('-r', '--range', type=str, help='章节范围，如 1-5')
    parser.add_argument('--status', action='store_true', help='显示系统状态')
    parser.add_argument('-c', '--config', type=str, help='配置文件路径')
    parser.add_argument('-q', '--quiet', action='store_true', help='静默模式')
    
    args = parser.parse_args()
    
    try:
        # 创建系统实例
        system = TutorialAutoGenerator(config_path=args.config)
        
        # 解析章节范围
        chapter_range = None
        if args.range:
            start, end = map(int, args.range.split('-'))
            chapter_range = (start, end)
        
        verbose = not args.quiet
        
        # 根据参数执行对应功能
        if args.status:
            system.list_status()
        
        elif args.explore_only:
            if not args.topic:
                print("❌ 请指定主题名称 (-t)")
                return
            system.explore_only([args.topic], verbose=verbose)
        
        elif args.curriculum_only:
            if not args.topic:
                print("❌ 请指定主题名称 (-t)")
                return
            system.generate_curriculum_only(args.topic, verbose=verbose)
        
        elif args.articles_only:
            if not args.topic:
                print("❌ 请指定主题名称 (-t)")
                return
            system.generate_articles_only(args.topic, chapter_range, verbose=verbose)
        
        elif args.full:
            if not args.topic:
                print("❌ 请指定主题名称 (-t)")
                return
            system.generate_full_tutorial(args.topic, chapter_range, verbose=verbose)
        
        else:
            # 交互模式
            while True:
                print("\n" + "="*70)
                print("教程系列自动生成系统 - 交互模式")
                print("="*70)
                print("\n选择功能:")
                print("  1. 完整流程（探索 -> 大纲 -> 文章）")
                print("  2. 仅探索主题")
                print("  3. 仅生成大纲")
                print("  4. 仅生成文章")
                print("  5. 查看系统状态")
                print("  0. 退出")
                
                choice = input("\n请选择 (0-5): ").strip()
                
                if choice == '0':
                    break
                
                elif choice == '1':
                    topic = input("请输入主题名称: ").strip()
                    if topic:
                        range_input = input("章节范围 (留空=全部，如 1-3): ").strip()
                        chapter_range = None
                        if range_input and '-' in range_input:
                            start, end = map(int, range_input.split('-'))
                            chapter_range = (start, end)
                        system.generate_full_tutorial(topic, chapter_range, verbose=True)
                
                elif choice == '2':
                    topic = input("请输入主题名称: ").strip()
                    if topic:
                        system.explore_only([topic], verbose=True)
                
                elif choice == '3':
                    topic = input("请输入主题名称: ").strip()
                    if topic:
                        system.generate_curriculum_only(topic, verbose=True)
                
                elif choice == '4':
                    topic = input("请输入主题名称: ").strip()
                    if topic:
                        range_input = input("章节范围 (留空=全部，如 1-3): ").strip()
                        chapter_range = None
                        if range_input and '-' in range_input:
                            start, end = map(int, range_input.split('-'))
                            chapter_range = (start, end)
                        system.generate_articles_only(topic, chapter_range, verbose=True)
                
                elif choice == '5':
                    system.list_status()
                
                else:
                    print("无效选择")
                
                input("\n按回车继续...")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
    finally:
        if 'system' in locals():
            system.close()
        print("\n👋 感谢使用！\n")


if __name__ == "__main__":
    main()

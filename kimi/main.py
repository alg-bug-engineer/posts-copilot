#!/usr/bin/env python3
"""
Kimi 内容自动生成系统 - 统一入口
功能：主题探索 -> 大纲生成 -> 文章写作的完整自动化流程
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

from topic_explorer import TopicExplorer
from curriculum_generator import CurriculumGenerator
from article_generator import ArticleGenerator


class ContentGenerationPipeline:
    """内容自动生成流水线"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化流水线"""
        self._check_environment()
        
        if config_path is None:
            config_path = Path(__file__).parent / "tutorial_config.yaml"
        
        print("\n" + "="*80)
        print(" 🚀 Kimi 内容自动生成系统")
        print("="*80 + "\n")
        
        # 初始化各模块
        print("📦 初始化模块...")
        self.topic_explorer = TopicExplorer(config_path)
        self.curriculum_generator = CurriculumGenerator(config_path)
        self.article_generator = ArticleGenerator(config_path)
        print("✓ 所有模块已就绪\n")
    
    def _check_environment(self):
        """检查环境配置"""
        api_key = os.getenv("MOONSHOT_API_KEY")
        if not api_key:
            print("\n❌ 错误：未设置 MOONSHOT_API_KEY 环境变量")
            print("\n请执行：")
            print('  export MOONSHOT_API_KEY="your-api-key-here"')
            print("\n或在 ~/.zshrc 或 ~/.bashrc 中添加上述命令\n")
            sys.exit(1)
    
    def run_full_pipeline(
        self,
        topic: str,
        chapter_range: Optional[tuple] = None,
        skip_exploration: bool = False,
        skip_curriculum: bool = False
    ):
        """
        运行完整的内容生成流水线
        
        Args:
            topic: 主题名称
            chapter_range: 生成章节范围，如 (1, 3)
            skip_exploration: 跳过主题探索（如果已探索过）
            skip_curriculum: 跳过大纲生成（如果已生成过）
        """
        print(f"\n{'='*80}")
        print(f"🎯 开始完整流水线")
        print(f"   主题: {topic}")
        if chapter_range:
            print(f"   章节范围: 第 {chapter_range[0]}-{chapter_range[1]} 章")
        print(f"{'='*80}\n")
        
        try:
            # 阶段 1: 主题探索
            if not skip_exploration:
                print("【阶段 1/3】🔍 主题探索")
                print("-" * 80)
                
                existing = self.topic_explorer.get_topic_by_name(topic)
                if existing:
                    print(f"✓ 主题已探索过，跳过此步骤")
                    print(f"  发现 {len(existing.get('subtopics', []))} 个子主题\n")
                else:
                    self.topic_explorer.explore_topic(topic, verbose=True)
                    self._sync_databases()
            else:
                print("【阶段 1/3】🔍 主题探索 - 已跳过\n")
            
            # 阶段 2: 大纲生成
            if not skip_curriculum:
                print("\n【阶段 2/3】📖 教程大纲生成")
                print("-" * 80)
                
                existing = self.curriculum_generator.get_curriculum_by_topic(topic)
                if existing:
                    print(f"✓ 教程大纲已存在，跳过此步骤")
                    print(f"  共 {existing.get('total_chapters', 0)} 章\n")
                    curriculum = existing
                else:
                    curriculum = self.curriculum_generator.generate_curriculum(topic, verbose=True)
                    self._sync_databases()
            else:
                print("\n【阶段 2/3】📖 教程大纲生成 - 已跳过\n")
                curriculum = self.curriculum_generator.get_curriculum_by_topic(topic)
                if not curriculum:
                    print("❌ 错误：跳过大纲生成但未找到现有大纲")
                    return
            
            # 阶段 3: 文章生成
            print("\n【阶段 3/3】✍️  文章生成")
            print("-" * 80)
            
            chapters = curriculum.get("chapters", [])
            if chapter_range:
                start, end = chapter_range
                chapters = [ch for ch in chapters if start <= ch.get('chapter_number', 0) <= end]
            
            print(f"   将生成 {len(chapters)} 篇文章\n")
            
            results = []
            for i, chapter in enumerate(chapters, 1):
                ch_num = chapter.get('chapter_number', i)
                print(f"\n>>> [{i}/{len(chapters)}] 第 {ch_num} 章: {chapter['title']}")
                print("-" * 80)
                
                try:
                    result = self.article_generator.generate_article(
                        topic, ch_num, verbose=True
                    )
                    results.append(result)
                    print(f"✓ 完成\n")
                except Exception as e:
                    print(f"✗ 生成失败: {e}\n")
                    continue
                
                # 避免请求过快
                if i < len(chapters):
                    import time
                    print("⏳ 等待 5 秒...\n")
                    time.sleep(5)
            
            # 总结
            print(f"\n{'='*80}")
            print(f"✅ 流水线执行完成！")
            print(f"   主题: {topic}")
            print(f"   成功生成: {len(results)}/{len(chapters)} 篇文章")
            print(f"{'='*80}\n")
            
            if results:
                print("📄 生成的文章：")
                for r in results:
                    print(f"   • {r['output_file']}")
                print()
            
            return results
            
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断流水线")
        except Exception as e:
            print(f"\n❌ 流水线执行失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _sync_databases(self):
        """同步数据库，确保各模块能看到最新数据"""
        self.curriculum_generator.topics_db = self.curriculum_generator._load_json(
            self.curriculum_generator.topics_db_path
        )
        self.article_generator.curriculum_db = self.article_generator._load_json(
            self.article_generator.curriculum_db_path
        )
    
    def explore_only(self, topic: str):
        """仅执行主题探索"""
        print("\n🔍 主题探索模式\n")
        self.topic_explorer.explore_topic(topic, verbose=True)
    
    def generate_curriculum_only(self, topic: str):
        """仅生成教程大纲"""
        print("\n📖 大纲生成模式\n")
        self.curriculum_generator.generate_curriculum(topic, verbose=True)
    
    def generate_article_only(self, topic: str, chapter: int):
        """仅生成单篇文章"""
        print(f"\n✍️  文章生成模式 - 第 {chapter} 章\n")
        self.article_generator.generate_article(topic, chapter, verbose=True)
    
    def generate_series(self, topic: str, chapter_range: Optional[tuple] = None):
        """批量生成文章（假设大纲已存在）"""
        print("\n📚 批量生成模式\n")
        self.article_generator.generate_series(topic, chapter_range, verbose=True)
    
    def list_topics(self):
        """列出所有已探索的主题"""
        topics = self.topic_explorer.topics_db.get("topics", [])
        
        if not topics:
            print("\n暂无已探索的主题\n")
            return
        
        print("\n📚 已探索的主题：\n")
        for i, topic in enumerate(topics, 1):
            name = topic.get("main_topic", "未知")
            subtopics_count = len(topic.get("subtopics", []))
            explored_at = topic.get("explored_at", "未知时间")
            print(f"{i}. {name}")
            print(f"   子主题: {subtopics_count} 个")
            print(f"   探索时间: {explored_at}\n")
    
    def list_curriculums(self):
        """列出所有已生成的教程大纲"""
        curriculums = self.curriculum_generator.curriculum_db.get("curriculums", [])
        
        if not curriculums:
            print("\n暂无已生成的教程大纲\n")
            return
        
        print("\n📖 已生成的教程大纲：\n")
        for i, curr in enumerate(curriculums, 1):
            name = curr.get("main_topic", "未知")
            chapters = len(curr.get("chapters", []))
            created_at = curr.get("created_at", "未知时间")
            print(f"{i}. {name}")
            print(f"   章节数: {chapters}")
            print(f"   创建时间: {created_at}\n")
    
    def show_curriculum(self, topic: str):
        """显示指定主题的教程大纲"""
        curriculum = self.curriculum_generator.get_curriculum_by_topic(topic)
        
        if not curriculum:
            print(f"\n❌ 未找到主题 '{topic}' 的教程大纲\n")
            return
        
        print(f"\n{'='*80}")
        print(f"📖 教程大纲: {curriculum.get('curriculum_name', topic)}")
        print(f"{'='*80}\n")
        
        print(f"主题: {curriculum.get('main_topic', 'N/A')}")
        print(f"总章节: {curriculum.get('total_chapters', 0)}")
        print(f"预计总时长: {curriculum.get('total_estimated_hours', 0)} 小时")
        print(f"难度: {curriculum.get('overall_difficulty', 'N/A')}\n")
        
        print("章节列表：\n")
        for ch in curriculum.get("chapters", []):
            num = ch.get("chapter_number", "?")
            title = ch.get("title", "未命名")
            difficulty = ch.get("difficulty", "N/A")
            time = ch.get("estimated_reading_time", "N/A")
            print(f"第 {num} 章: {title}")
            print(f"  难度: {difficulty} | 预计阅读: {time} 分钟")
            print(f"  学习目标: {', '.join(ch.get('learning_objectives', [])[:2])}")
            print()
    
    def close(self):
        """关闭所有客户端"""
        self.article_generator.close()


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description='Kimi 内容自动生成系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：

  # 完整流水线：探索 -> 大纲 -> 生成所有文章
  python main.py --full "强化学习基础"
  
  # 生成特定章节
  python main.py --full "强化学习基础" --range 1-3
  
  # 仅探索主题
  python main.py --explore "Transformer架构"
  
  # 仅生成大纲
  python main.py --curriculum "Transformer架构"
  
  # 仅生成单篇文章
  python main.py --article "Transformer架构" --chapter 1
  
  # 批量生成文章（大纲已存在）
  python main.py --series "Transformer架构" --range 1-5
  
  # 列出所有主题和大纲
  python main.py --list
  
  # 查看指定主题的大纲
  python main.py --show "Transformer架构"
        """
    )
    
    # 模式选择
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--full', type=str, metavar='TOPIC',
                           help='完整流水线（探索+大纲+文章）')
    mode_group.add_argument('--explore', type=str, metavar='TOPIC',
                           help='仅探索主题')
    mode_group.add_argument('--curriculum', type=str, metavar='TOPIC',
                           help='仅生成教程大纲')
    mode_group.add_argument('--article', type=str, metavar='TOPIC',
                           help='仅生成单篇文章')
    mode_group.add_argument('--series', type=str, metavar='TOPIC',
                           help='批量生成文章（大纲需已存在）')
    mode_group.add_argument('--list', action='store_true',
                           help='列出所有主题和大纲')
    mode_group.add_argument('--show', type=str, metavar='TOPIC',
                           help='显示指定主题的大纲详情')
    
    # 可选参数
    parser.add_argument('--chapter', type=int, metavar='N',
                       help='章节编号（用于 --article）')
    parser.add_argument('--range', type=str, metavar='START-END',
                       help='章节范围，如 1-5')
    parser.add_argument('--skip-explore', action='store_true',
                       help='跳过主题探索（已探索过）')
    parser.add_argument('--skip-curriculum', action='store_true',
                       help='跳过大纲生成（已生成过）')
    parser.add_argument('--config', type=str, metavar='PATH',
                       help='配置文件路径')
    
    args = parser.parse_args()
    
    try:
        pipeline = ContentGenerationPipeline(config_path=args.config)
        
        # 解析章节范围
        chapter_range = None
        if args.range:
            try:
                start, end = map(int, args.range.split('-'))
                chapter_range = (start, end)
            except:
                print(f"❌ 错误：章节范围格式不正确，应为 '1-5' 格式")
                return
        
        # 执行相应模式
        if args.full:
            pipeline.run_full_pipeline(
                args.full,
                chapter_range=chapter_range,
                skip_exploration=args.skip_explore,
                skip_curriculum=args.skip_curriculum
            )
        
        elif args.explore:
            pipeline.explore_only(args.explore)
        
        elif args.curriculum:
            pipeline.generate_curriculum_only(args.curriculum)
        
        elif args.article:
            if not args.chapter:
                print("❌ 错误：使用 --article 时必须指定 --chapter")
                return
            pipeline.generate_article_only(args.article, args.chapter)
        
        elif args.series:
            pipeline.generate_series(args.series, chapter_range)
        
        elif args.list:
            pipeline.list_topics()
            pipeline.list_curriculums()
        
        elif args.show:
            pipeline.show_curriculum(args.show)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'pipeline' in locals():
            pipeline.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
教程大纲生成器
功能：基于探索的子主题，生成有逻辑、循序渐进的教程体系
"""

import os
import json
import yaml
import openai
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class CurriculumGenerator:
    """教程大纲生成器：组织子主题成为循序渐进的教程体系"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化生成器"""
        self.config = self._load_config(config_path)
        
        # 初始化 API 客户端
        base_url = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")
        api_key = os.getenv("MOONSHOT_API_KEY")
        
        if not api_key:
            raise ValueError("MOONSHOT_API_KEY 环境变量未设置")
        
        self.client = openai.Client(base_url=base_url, api_key=api_key)
        self.model = self.config['article_generation']['model']
        
        # 加载数据库
        self.topics_db_path = Path(__file__).parent / self.config['storage']['topics_db']
        self.curriculum_db_path = Path(__file__).parent / self.config['storage']['curriculum_db']
        self.curriculum_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.topics_db = self._load_json(self.topics_db_path)
        self.curriculum_db = self._load_json(self.curriculum_db_path, default={"curriculums": []})
    
    def _load_config(self, config_path: Optional[str] = None):
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent / "tutorial_config.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_json(self, path: Path, default: Optional[Dict] = None) -> Dict:
        """加载JSON文件"""
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default or {}
    
    def _save_json(self, path: Path, data: Dict):
        """保存JSON文件"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def generate_curriculum(self, topic_name: str, verbose: bool = True) -> Dict:
        """
        为指定主题生成教程大纲
        
        Args:
            topic_name: 主题名称
            verbose: 是否显示详细过程
            
        Returns:
            教程大纲数据
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"📖 生成教程大纲: {topic_name}")
            print(f"{'='*70}\n")
        
        # 从主题库中查找主题数据
        topic_data = self._find_topic(topic_name)
        if not topic_data:
            raise ValueError(f"主题 '{topic_name}' 未找到，请先使用 topic_explorer 探索该主题")
        
        if verbose:
            print(f"✓ 找到主题数据")
            print(f"  子主题数量: {len(topic_data.get('subtopics', []))}")
            print(f"  难度级别: {topic_data.get('difficulty_level', 'N/A')}\n")
        
        # 构建大纲生成提示词
        prompt = self._build_curriculum_prompt(topic_data)
        
        if verbose:
            print("🎯 正在生成循序渐进的教程大纲...\n")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一位资深的技术教育专家和课程架构师，擅长设计系统化、循序渐进的学习路径。

你的设计原则：
1. 知识递进：从基础概念到高级应用，层层深入
2. 逻辑连贯：前后章节紧密关联，形成完整知识体系
3. 目标明确：每章都有清晰的学习目标和实际产出
4. 难度合理：符合认知规律，避免突变和跳跃
5. 实战导向：注重理论与实践结合

章节标题要求：
- 准确反映核心内容
- 避免生硬的"第X章"格式
- 使用吸引人的表述
- 示例：
  ✓ "注意力机制的本质与计算原理"
  ✓ "从 RNN 到 Transformer 的演进历程"
  ✗ "第1章 基础知识"
  ✗ "Transformer 介绍"

输出格式必须是纯 JSON：
{
  "curriculum_name": "教程系列名称",
  "main_topic": "主题名称",
  "description": "教程系列简介",
  "target_audience": "目标读者",
  "prerequisites": ["前置要求"],
  "total_chapters": 章节总数,
  "estimated_total_time": "预计总学习时间",
  "chapters": [
    {
      "chapter_number": 章节编号,
      "title": "章节标题",
      "subtitle": "副标题",
      "difficulty": "beginner/intermediate/advanced",
      "estimated_reading_time": "预计阅读时间（分钟）",
      "learning_objectives": ["学习目标"],
      "key_concepts": ["核心概念"],
      "practical_exercises": ["实践练习"],
      "prerequisites": ["本章前置知识"],
      "related_chapters": [相关章节编号],
      "content_outline": [
        "一级标题1",
        "  二级标题1.1",
        "  二级标题1.2",
        "一级标题2"
      ]
    }
  ],
  "learning_path": {
    "beginner_track": [章节编号列表],
    "intermediate_track": [章节编号列表],
    "advanced_track": [章节编号列表]
  },
  "suggested_projects": ["项目建议"],
  "references": ["参考资源"]
}

确保输出有效的JSON，不包含其他文字。"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config['article_generation']['search_temperature'],
                max_tokens=self.config['article_generation']['max_tokens'],
            )
            
            content = response.choices[0].message.content
            
            # 清理和解析JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            curriculum = json.loads(content)
            
            # 添加元数据
            curriculum["generated_at"] = datetime.now().isoformat()
            curriculum["status"] = "generated"
            curriculum["topic_id"] = topic_data.get("main_topic")
            
            if verbose:
                print(f"✓ 大纲生成完成！")
                print(f"  教程名称: {curriculum.get('curriculum_name', 'N/A')}")
                print(f"  章节数量: {curriculum.get('total_chapters', 0)}")
                print(f"  预计时间: {curriculum.get('estimated_total_time', 'N/A')}\n")
                
                # 显示章节列表
                print("📚 章节列表:")
                for chapter in curriculum.get('chapters', []):
                    ch_num = chapter.get('chapter_number', '?')
                    title = chapter.get('title', '未命名')
                    difficulty = chapter.get('difficulty', 'N/A')
                    print(f"  第{ch_num}章: {title} [{difficulty}]")
                print()
            
            # 保存到数据库
            self.curriculum_db["curriculums"].append(curriculum)
            self._save_json(self.curriculum_db_path, self.curriculum_db)
            print(f"✓ 大纲已保存: {self.curriculum_db_path}\n")
            
            return curriculum
            
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析错误: {e}")
            print(f"原始内容:\n{content[:500]}...")
            raise
        except Exception as e:
            print(f"✗ 生成失败: {e}")
            raise
    
    def _find_topic(self, topic_name: str) -> Optional[Dict]:
        """在主题库中查找主题（支持模糊匹配）"""
        import re
        
        def normalize_name(name: str) -> str:
            """规范化主题名称：移除所有分隔符、统一为小写"""
            name = name.lower()
            # 移除所有括号、连字符、下划线、空格
            name = re.sub(r'[（）()_\-\s]+', '', name)
            return name
        
        normalized_search = normalize_name(topic_name)
        
        # 首先尝试精确匹配
        for topic in self.topics_db.get("topics", []):
            topic_main = topic.get("main_topic", "")
            if normalize_name(topic_main) == normalized_search:
                return topic
        
        # 如果精确匹配失败，尝试部分匹配
        for topic in self.topics_db.get("topics", []):
            topic_main = normalize_name(topic.get("main_topic", ""))
            # 检查是否包含搜索词的主要部分
            if normalized_search in topic_main or topic_main in normalized_search:
                print(f"  提示: 使用模糊匹配找到主题 '{topic.get('main_topic')}'")
                return topic
        
        return None
    
    def _build_curriculum_prompt(self, topic_data: Dict) -> str:
        """构建大纲生成提示词"""
        min_chapters = self.config['curriculum_generation']['min_chapters']
        max_chapters = self.config['curriculum_generation']['max_chapters']
        structure = self.config['curriculum_generation']['structure']
        
        subtopics_text = "\n".join([
            f"- {st['title']}: {st['description']} (难度: {st['difficulty']})"
            for st in topic_data.get('subtopics', [])
        ])
        
        return f"""请为以下技术主题设计一个完整的教程体系：

主题：{topic_data.get('main_topic')}
主题描述：{topic_data.get('description', '')}
难度级别：{topic_data.get('difficulty_level', 'intermediate')}

已发现的子主题：
{subtopics_text}

学习路径建议：{topic_data.get('learning_path', '')}

设计要求：
1. 章节数量在 {min_chapters}-{max_chapters} 章之间
2. 遵循循序渐进的原则：{self.config['curriculum_generation']['progression_style']}
3. 包含以下结构层次：
{chr(10).join(f'   - {k}: {v}' for k, v in structure.items())}

4. 每个章节应该：
   - 有明确的学习目标
   - 包含核心概念讲解
   - 提供实践练习（如适用）
   - 标注难度级别和前置要求

5. 整体设计要：
   - 逻辑连贯，前后呼应
   - 理论与实践结合
   - 适合自学和教学

请生成完整的教程大纲JSON。"""
    
    def get_all_curriculums(self) -> List[Dict]:
        """获取所有教程大纲"""
        return self.curriculum_db.get("curriculums", [])
    
    def get_curriculum_by_topic(self, topic_name: str) -> Optional[Dict]:
        """根据主题名称获取教程大纲（支持模糊匹配）"""
        import re
        
        def normalize_name(name: str) -> str:
            """规范化主题名称：移除所有分隔符、统一为小写"""
            name = name.lower()
            name = re.sub(r'[（）()_\-\s]+', '', name)
            return name
        
        normalized_search = normalize_name(topic_name)
        
        for curr in self.curriculum_db.get("curriculums", []):
            curr_topic = normalize_name(curr.get("main_topic", ""))
            if curr_topic == normalized_search or normalized_search in curr_topic or curr_topic in normalized_search:
                return curr
        return None
    
    def export_curriculum_markdown(self, curriculum: Dict, output_path: Optional[str] = None) -> str:
        """导出教程大纲为Markdown格式"""
        lines = []
        
        # 标题
        lines.append(f"# {curriculum.get('curriculum_name', '教程大纲')}")
        lines.append("")
        lines.append(f"**主题**: {curriculum.get('main_topic', 'N/A')}")
        lines.append(f"**目标读者**: {curriculum.get('target_audience', 'N/A')}")
        lines.append(f"**总章节数**: {curriculum.get('total_chapters', 0)}")
        lines.append(f"**预计学习时间**: {curriculum.get('estimated_total_time', 'N/A')}")
        lines.append("")
        
        # 简介
        lines.append("## 课程简介")
        lines.append("")
        lines.append(curriculum.get('description', ''))
        lines.append("")
        
        # 前置要求
        if curriculum.get('prerequisites'):
            lines.append("## 前置要求")
            lines.append("")
            for prereq in curriculum['prerequisites']:
                lines.append(f"- {prereq}")
            lines.append("")
        
        # 章节列表
        lines.append("## 章节目录")
        lines.append("")
        
        for chapter in curriculum.get('chapters', []):
            ch_num = chapter.get('chapter_number', '?')
            title = chapter.get('title', '未命名')
            subtitle = chapter.get('subtitle', '')
            difficulty = chapter.get('difficulty', '')
            time = chapter.get('estimated_reading_time', '')
            
            lines.append(f"### 第{ch_num}章: {title}")
            if subtitle:
                lines.append(f"*{subtitle}*")
            lines.append("")
            lines.append(f"**难度**: {difficulty} | **预计阅读**: {time}分钟")
            lines.append("")
            
            # 学习目标
            if chapter.get('learning_objectives'):
                lines.append("**学习目标**:")
                for obj in chapter['learning_objectives']:
                    lines.append(f"- {obj}")
                lines.append("")
            
            # 核心概念
            if chapter.get('key_concepts'):
                lines.append("**核心概念**: " + ", ".join(chapter['key_concepts']))
                lines.append("")
            
            # 内容大纲
            if chapter.get('content_outline'):
                lines.append("**内容大纲**:")
                for item in chapter['content_outline']:
                    lines.append(f"{item}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # 学习路径
        if curriculum.get('learning_path'):
            lines.append("## 学习路径")
            lines.append("")
            for track_name, chapters in curriculum['learning_path'].items():
                lines.append(f"**{track_name}**: 章节 {', '.join(map(str, chapters))}")
            lines.append("")
        
        # 项目建议
        if curriculum.get('suggested_projects'):
            lines.append("## 实践项目")
            lines.append("")
            for project in curriculum['suggested_projects']:
                lines.append(f"- {project}")
            lines.append("")
        
        # 参考资源
        if curriculum.get('references'):
            lines.append("## 参考资源")
            lines.append("")
            for ref in curriculum['references']:
                lines.append(f"- {ref}")
            lines.append("")
        
        markdown_content = "\n".join(lines)
        
        # 保存到文件
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"✓ Markdown大纲已导出: {output_path}")
        
        return markdown_content


def main():
    """测试教程大纲生成器"""
    import argparse
    
    parser = argparse.ArgumentParser(description='教程大纲生成器')
    parser.add_argument('-t', '--topic', type=str, help='主题名称')
    parser.add_argument('-l', '--list', action='store_true', help='列出所有教程大纲')
    parser.add_argument('-e', '--export', type=str, help='导出指定主题的大纲为Markdown')
    parser.add_argument('-c', '--config', type=str, help='配置文件路径')
    
    args = parser.parse_args()
    
    try:
        generator = CurriculumGenerator(config_path=args.config)
        
        if args.list:
            curriculums = generator.get_all_curriculums()
            if not curriculums:
                print("还没有生成任何教程大纲")
            else:
                print(f"\n已生成的教程大纲 (共 {len(curriculums)} 个):")
                print("=" * 70)
                for i, curr in enumerate(curriculums, 1):
                    print(f"{i}. {curr.get('curriculum_name', 'N/A')}")
                    print(f"   主题: {curr.get('main_topic', 'N/A')}")
                    print(f"   章节数: {curr.get('total_chapters', 0)}")
                    print(f"   生成时间: {curr.get('generated_at', 'N/A')}")
                    print()
        
        elif args.export:
            curriculum = generator.get_curriculum_by_topic(args.export)
            if not curriculum:
                print(f"未找到主题 '{args.export}' 的教程大纲")
                return
            
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in args.export)
            output_path = Path(f"../posts/curriculum_{safe_name}.md")
            generator.export_curriculum_markdown(curriculum, output_path)
        
        elif args.topic:
            generator.generate_curriculum(args.topic)
        
        else:
            # 交互模式
            print("\n教程大纲生成器")
            print("=" * 70)
            topic = input("请输入主题名称: ").strip()
            if topic:
                curriculum = generator.generate_curriculum(topic)
                
                # 询问是否导出
                export = input("\n是否导出为Markdown？(y/n): ").strip().lower()
                if export in ['y', 'yes']:
                    safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in topic)
                    output_path = Path(f"../posts/curriculum_{safe_name}.md")
                    generator.export_curriculum_markdown(curriculum, output_path)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

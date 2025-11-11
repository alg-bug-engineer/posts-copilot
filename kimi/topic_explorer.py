#!/usr/bin/env python3
"""
Topic 探索器模块
功能：深度挖掘某个技术方向，发现值得讲解的子主题
"""

import os
import json
import yaml
import openai
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class TopicExplorer:
    """主题探索器：深度挖掘技术方向，发现值得讲解的知识点"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化探索器"""
        self.config = self._load_config(config_path)
        
        # 初始化 API 客户端
        base_url = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")
        api_key = os.getenv("MOONSHOT_API_KEY")
        
        if not api_key:
            raise ValueError("MOONSHOT_API_KEY 环境变量未设置")
        
        self.client = openai.Client(base_url=base_url, api_key=api_key)
        self.model = self.config['article_generation']['model']
        
        # 加载现有主题库
        self.topics_db_path = Path(__file__).parent / self.config['storage']['topics_db']
        self.topics_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.topics_db = self._load_topics_db()
    
    def _load_config(self, config_path: Optional[str] = None):
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent / "tutorial_config.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_topics_db(self) -> Dict:
        """加载主题数据库"""
        if self.topics_db_path.exists():
            with open(self.topics_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"topics": [], "last_updated": None}
    
    def _save_topics_db(self):
        """保存主题数据库"""
        self.topics_db["last_updated"] = datetime.now().isoformat()
        with open(self.topics_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.topics_db, f, ensure_ascii=False, indent=2)
        print(f"✓ 主题库已保存: {self.topics_db_path}")
    
    def explore_topic(self, main_topic: str, verbose: bool = True) -> Dict:
        """
        深度探索一个主题，发现值得讲解的子主题
        
        Args:
            main_topic: 主题名称，如 "强化学习" 或 "Vision Language Action Model"
            verbose: 是否显示详细过程
            
        Returns:
            包含主题和子主题的字典
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"🔍 开始探索主题: {main_topic}")
            print(f"{'='*70}\n")
        
        # 构建探索提示词
        exploration_prompt = self._build_exploration_prompt(main_topic)
        
        if verbose:
            print("📊 正在分析技术领域，发现值得深入讲解的子主题...\n")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一位在技术教育领域深耕多年的专家，擅长发现和梳理值得深入学习的知识点。

你的分析视角：
1. 技术价值：该子主题是否代表核心技术或重要突破
2. 实用性：是否有真实应用场景和实践意义
3. 教学性：是否适合作为独立章节进行系统讲解
4. 层次性：涵盖基础、进阶、高级不同难度层次
5. 连贯性：子主题之间能否形成连贯的学习路径

子主题命名要求：
- 清晰准确，一目了然
- 体现技术核心或方法论
- 避免过于宽泛或过于细碎
- 示例：
  ✓ "Transformer 的注意力机制原理"
  ✓ "多模态数据融合的技术方案"
  ✓ "强化学习中的价值函数近似"
  ✗ "深度学习基础"（太宽泛）
  ✗ "某个参数的设置"（太细碎）

输出格式必须是纯 JSON：
{
  "main_topic": "主题名称",
  "description": "主题简介",
  "difficulty_level": "beginner/intermediate/advanced",
  "estimated_articles": "预计需要多少篇文章",
  "subtopics": [
    {
      "title": "子主题标题",
      "description": "子主题描述",
      "difficulty": "beginner/intermediate/advanced",
      "prerequisites": ["前置知识"],
      "learning_objectives": ["学习目标1", "学习目标2"],
      "estimated_reading_time": "预计阅读时间（分钟）",
      "practical_value": "实践价值说明"
    }
  ],
  "learning_path": "学习路径建议",
  "related_topics": ["相关主题"]
}

确保输出的是有效的JSON格式，不要包含任何其他文字。"""
                    },
                    {
                        "role": "user",
                        "content": exploration_prompt
                    }
                ],
                temperature=self.config['article_generation']['search_temperature'],
                max_tokens=self.config['article_generation']['max_tokens'],
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            # 移除可能的markdown代码块标记
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            topic_data = json.loads(content)
            
            # 添加元数据
            topic_data["explored_at"] = datetime.now().isoformat()
            topic_data["status"] = "explored"
            
            if verbose:
                print(f"✓ 探索完成！")
                print(f"  发现 {len(topic_data.get('subtopics', []))} 个子主题")
                print(f"  难度级别: {topic_data.get('difficulty_level', 'N/A')}")
                print(f"  预计文章数: {topic_data.get('estimated_articles', 'N/A')}\n")
                
                # 显示子主题列表
                print("📚 子主题列表:")
                for i, subtopic in enumerate(topic_data.get('subtopics', []), 1):
                    print(f"  {i}. {subtopic['title']} ({subtopic['difficulty']})")
                    print(f"     {subtopic['description'][:80]}...")
                print()
            
            # 保存到数据库
            self.topics_db["topics"].append(topic_data)
            self._save_topics_db()
            
            return topic_data
            
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析错误: {e}")
            print(f"原始内容:\n{content[:500]}...")
            raise
        except Exception as e:
            print(f"✗ 探索失败: {e}")
            raise
    
    def _build_exploration_prompt(self, main_topic: str) -> str:
        """构建探索提示词"""
        depth = self.config['topic_exploration']['exploration_depth']
        strategies = self.config['topic_exploration']['strategies']
        
        return f"""请深入分析以下技术主题，发现值得深入讲解的子主题：

主题：{main_topic}

分析维度：
{chr(10).join(f'- {s}' for s in strategies)}

要求：
1. 发现 {depth} 个左右有价值的子主题
2. 子主题应该覆盖从入门到高级的不同层次
3. 每个子主题都要有明确的学习目标和实践价值
4. 考虑子主题之间的逻辑关系和学习顺序
5. 关注最新的技术动态和实际应用

请以JSON格式输出完整的主题分析结果。"""
    
    def batch_explore(self, topics: List[str], verbose: bool = True) -> List[Dict]:
        """批量探索多个主题"""
        print(f"\n{'='*70}")
        print(f"📚 批量探索模式 - 共 {len(topics)} 个主题")
        print(f"{'='*70}\n")
        
        results = []
        for i, topic in enumerate(topics, 1):
            print(f"[{i}/{len(topics)}] 探索主题: {topic}")
            print("-" * 70)
            
            try:
                result = self.explore_topic(topic, verbose=verbose)
                results.append(result)
            except Exception as e:
                print(f"✗ 探索失败: {e}\n")
                continue
            
            # 避免请求过快
            if i < len(topics):
                import time
                print("⏳ 等待 3 秒...\n")
                time.sleep(3)
        
        print(f"{'='*70}")
        print(f"✅ 批量探索完成 - 成功 {len(results)}/{len(topics)}")
        print(f"{'='*70}\n")
        
        return results
    
    def get_all_topics(self) -> List[Dict]:
        """获取所有已探索的主题"""
        return self.topics_db.get("topics", [])
    
    def get_topic_by_name(self, topic_name: str) -> Optional[Dict]:
        """根据名称查找主题（支持模糊匹配）"""
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
                return topic
        
        return None
    
    def suggest_next_topics(self, current_topic: str, count: int = 5) -> List[str]:
        """基于当前主题建议相关的下一个主题"""
        topic_data = self.get_topic_by_name(current_topic)
        if not topic_data:
            return []
        
        related = topic_data.get("related_topics", [])
        return related[:count]


def main():
    """测试主题探索器"""
    import argparse
    
    parser = argparse.ArgumentParser(description='主题探索器 - 发现值得讲解的技术子主题')
    parser.add_argument('-t', '--topic', type=str, help='要探索的主题')
    parser.add_argument('-b', '--batch', type=str, help='批量探索，指定包含主题列表的文件')
    parser.add_argument('-l', '--list', action='store_true', help='列出所有已探索的主题')
    parser.add_argument('-c', '--config', type=str, help='配置文件路径')
    
    args = parser.parse_args()
    
    try:
        explorer = TopicExplorer(config_path=args.config)
        
        if args.list:
            topics = explorer.get_all_topics()
            if not topics:
                print("还没有探索过任何主题")
            else:
                print(f"\n已探索的主题 (共 {len(topics)} 个):")
                print("=" * 70)
                for i, topic in enumerate(topics, 1):
                    print(f"{i}. {topic['main_topic']}")
                    print(f"   难度: {topic.get('difficulty_level', 'N/A')}")
                    print(f"   子主题数: {len(topic.get('subtopics', []))}")
                    print(f"   探索时间: {topic.get('explored_at', 'N/A')}")
                    print()
        
        elif args.batch:
            batch_file = Path(args.batch)
            if not batch_file.exists():
                print(f"文件不存在: {batch_file}")
                return
            
            with open(batch_file, 'r', encoding='utf-8') as f:
                topics = [line.strip() for line in f if line.strip()]
            
            explorer.batch_explore(topics)
        
        elif args.topic:
            explorer.explore_topic(args.topic)
        
        else:
            # 交互模式
            while True:
                topic = input("\n请输入要探索的主题 (输入 'q' 退出): ").strip()
                if topic.lower() in ['q', 'quit', 'exit']:
                    break
                if topic:
                    explorer.explore_topic(topic)
                    
                    # 询问是否继续
                    cont = input("\n继续探索其他主题？(y/n): ").strip().lower()
                    if cont not in ['y', 'yes']:
                        break
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
文章生成器模块
功能：基于教程章节，进行深度研究并生成带frontmatter的Markdown文章
"""

import os
import json
import yaml
import httpx
import openai
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class FormulaChatClient:
    """Formula API 客户端（支持联网搜索）"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.openai = openai.Client(base_url=base_url, api_key=api_key)
        self.httpx = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )
        self.model = "kimi-k2-thinking"
    
    def get_tools(self, formula_uri: str):
        """获取工具定义"""
        response = self.httpx.get(f"/formulas/{formula_uri}/tools")
        response.raise_for_status()
        return response.json().get("tools", [])
    
    def call_tool(self, formula_uri: str, function: str, args: dict):
        """调用工具"""
        response = self.httpx.post(
            f"/formulas/{formula_uri}/fibers",
            json={"name": function, "arguments": json.dumps(args)},
        )
        response.raise_for_status()
        fiber = response.json()
        
        if fiber.get("status") == "succeeded":
            return fiber["context"].get("output") or fiber["context"].get("encrypted_output")
        
        if "error" in fiber:
            return f"Error: {fiber['error']}"
        return "Error: Unknown error"
    
    def close(self):
        self.httpx.close()


class ArticleGenerator:
    """文章生成器：基于章节生成深度技术文章"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化生成器"""
        self.config = self._load_config(config_path)
        
        # 初始化客户端
        base_url = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")
        api_key = os.getenv("MOONSHOT_API_KEY")
        
        if not api_key:
            raise ValueError("MOONSHOT_API_KEY 环境变量未设置")
        
        self.client = FormulaChatClient(base_url, api_key)
        self.client.model = self.config['article_generation']['model']
        
        # 加载搜索工具
        self.formula_uris = ["moonshot/web-search:latest", "moonshot/date:latest"]
        self.all_tools = []
        self.tool_to_uri = {}
        self._load_tools()
        
        # 加载数据库
        self.curriculum_db_path = Path(__file__).parent / self.config['storage']['curriculum_db']
        self.history_db_path = Path(__file__).parent / self.config['storage']['generation_history']
        self.history_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.curriculum_db = self._load_json(self.curriculum_db_path)
        self.history_db = self._load_json(self.history_db_path, default={"generations": []})
        
        # 搜索结果存储
        self.search_results = []
        
        # 加载专家提示词模板
        self.expert_prompt_template = self._load_expert_prompt()
    
    def _load_config(self, config_path: Optional[str] = None):
        """加载配置"""
        if config_path is None:
            config_path = Path(__file__).parent / "tutorial_config.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_json(self, path: Path, default: Optional[Dict] = None) -> Dict:
        """加载JSON"""
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default or {}
    
    def _save_json(self, path: Path, data: Dict):
        """保存JSON"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_tools(self):
        """加载搜索工具"""
        print("\n🔧 加载搜索工具...")
        for uri in self.formula_uris:
            try:
                tools = self.client.get_tools(uri)
                for tool in tools:
                    func = tool.get("function")
                    if func:
                        func_name = func.get("name")
                        if func_name:
                            self.tool_to_uri[func_name] = uri
                            self.all_tools.append(tool)
                            print(f"   ✓ {func_name}")
            except Exception as e:
                print(f"   ✗ 加载 {uri} 失败: {e}")
        print(f"   共加载 {len(self.all_tools)} 个工具\n")
    
    def _load_expert_prompt(self):
        """加载专家提示词模板"""
        prompt_path = Path(__file__).parent / "prompts" / "expert_narrator.txt"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self._default_expert_prompt()
    
    def _default_expert_prompt(self):
        """默认专家提示词"""
        return """你是一位在 AI/大模型领域有 15 年研究经验的资深专家。

基于以下信息：
{search_results}

请深入讲解：{topic}

章节大纲：
{content_outline}

学习目标：
{learning_objectives}

要求：
1. 深入浅出，通俗易懂
2. 使用比喻和实例
3. 结构清晰，逻辑流畅
4. Markdown 格式
5. 包含代码示例（如适用）

开始你的讲解："""
    
    def generate_article(
        self, 
        topic_name: str, 
        chapter_number: int,
        verbose: bool = True
    ) -> Dict:
        """
        生成指定章节的文章
        
        Args:
            topic_name: 主题名称
            chapter_number: 章节编号
            verbose: 是否显示详细过程
            
        Returns:
            包含文章内容和元数据的字典
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"✍️  生成文章")
            print(f"   主题: {topic_name}")
            print(f"   章节: 第{chapter_number}章")
            print(f"{'='*70}\n")
        
        # 获取教程大纲
        curriculum = self._get_curriculum(topic_name)
        if not curriculum:
            raise ValueError(f"未找到主题 '{topic_name}' 的教程大纲")
        
        # 获取章节信息
        chapter = self._get_chapter(curriculum, chapter_number)
        if not chapter:
            raise ValueError(f"未找到第 {chapter_number} 章")
        
        if verbose:
            print(f"📖 章节信息:")
            print(f"   标题: {chapter['title']}")
            print(f"   难度: {chapter.get('difficulty', 'N/A')}")
            print(f"   预计时间: {chapter.get('estimated_reading_time', 'N/A')}分钟\n")
        
        # 第一阶段：信息收集
        self.search_results = []
        search_topic = f"{topic_name} - {chapter['title']}"
        
        if verbose:
            print("【阶段 1/2】📚 信息收集")
            print("-" * 70)
        
        self._research_phase(search_topic, chapter, verbose)
        
        # 第二阶段：文章写作
        if verbose:
            print(f"\n{'='*70}")
            print("【阶段 2/2】✍️  文章写作")
            print("-" * 70)
        
        article_content = self._writing_phase(
            topic_name, 
            chapter, 
            curriculum.get('curriculum_name', topic_name),
            verbose
        )
        
        # 生成frontmatter
        frontmatter = self._generate_frontmatter(
            topic_name, 
            chapter, 
            curriculum
        )
        
        # 组合完整文章
        full_content = self._compose_article(frontmatter, article_content)
        
        # 保存文章
        output_file = self._save_article(
            topic_name,
            chapter_number,
            chapter['title'],
            full_content
        )
        
        # 记录生成历史
        generation_record = {
            "topic": topic_name,
            "chapter_number": chapter_number,
            "chapter_title": chapter['title'],
            "generated_at": datetime.now().isoformat(),
            "output_file": str(output_file),
            "word_count": len(article_content),
            "search_count": len(self.search_results)
        }
        
        self.history_db["generations"].append(generation_record)
        self._save_json(self.history_db_path, self.history_db)
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"✅ 文章生成完成！")
            print(f"   文件: {output_file}")
            print(f"   字数: {len(article_content):,}")
            print(f"   搜索次数: {len(self.search_results)}")
            print(f"{'='*70}\n")
        
        return {
            "content": full_content,
            "frontmatter": frontmatter,
            "output_file": str(output_file),
            "metadata": generation_record
        }
    
    def _research_phase(self, topic: str, chapter: Dict, verbose: bool):
        """信息收集阶段"""
        max_rounds = self.config['article_generation']['max_search_rounds']
        
        # 构建研究提示词
        research_prompt = self._build_research_prompt(topic, chapter)
        
        messages = [
            {
                "role": "system",
                "content": """你是一位经验丰富的技术研究员，负责为技术文章收集全面、权威的资料。

研究策略：
- 优先搜索权威来源：顶会论文、官方文档、知名团队的技术博客
- 注重时效性：寻找最新的研究进展和实际应用案例
- 多角度覆盖：理论基础、技术实现、应用案例、对比分析
- 关注细节：算法流程、代码实现、性能数据、实际效果
- 避免冗余：不重复搜索已覆盖的内容

信息收集标准：
✓ 概念定义清晰
✓ 原理讲解充分
✓ 实现细节具体
✓ 案例真实可靠
✓ 数据准确权威

当你认为已收集到足够全面的信息时，回复"资料收集完成"。"""
            },
            {
                "role": "user",
                "content": research_prompt
            }
        ]
        
        for round_num in range(max_rounds):
            if verbose:
                print(f"\n>>> 第 {round_num + 1}/{max_rounds} 轮")
            
            try:
                completion = self.client.openai.chat.completions.create(
                    model=self.client.model,
                    messages=messages,
                    max_tokens=self.config['article_generation']['max_tokens'],
                    tools=self.all_tools,
                    temperature=self.config['article_generation']['search_temperature'],
                )
            except Exception as e:
                print(f"✗ API调用失败: {e}")
                break
            
            message = completion.choices[0].message
            messages.append(message)
            
            # 处理工具调用
            if not message.tool_calls:
                if message.content and any(kw in message.content for kw in 
                    ["信息收集完成", "收集完毕", "研究完成", "资料收集完成", "搜索完成", 
                     "已收集", "足够", "完成收集"]):
                    if verbose:
                        print("\n✓ 资料收集完成")
                    break
                continue
            
            if verbose:
                print(f"🔍 调用 {len(message.tool_calls)} 个工具")
            
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if verbose:
                    query = args.get('query', str(args)[:50])
                    print(f"   搜索: {query}")
                
                formula_uri = self.tool_to_uri.get(func_name)
                if not formula_uri:
                    continue
                
                try:
                    result = self.client.call_tool(formula_uri, func_name, args)
                    
                    if func_name == "web_search":
                        self.search_results.append({
                            "query": args.get("query", ""),
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": result
                    })
                except Exception as e:
                    if verbose:
                        print(f"   ✗ 工具调用失败: {e}")
    
    def _writing_phase(
        self, 
        topic_name: str, 
        chapter: Dict, 
        series_name: str,
        verbose: bool
    ) -> str:
        """文章写作阶段"""
        if verbose:
            print(f"\n📊 已收集 {len(self.search_results)} 条搜索结果")
            print("🎯 正在生成文章...\n")
        
        # 整理搜索结果
        formatted_results = self._format_search_results()
        
        # 构建学习目标（更自然的表述）
        learning_objectives_text = "\n".join([f"• {obj}" for obj in chapter.get('learning_objectives', [])])
        
        # 构建内容要点（更自然的表述）
        content_outline_text = "\n".join([f"{i}. {item}" for i, item in enumerate(chapter.get('content_outline', []), 1)])
        
        # 构建写作提示词
        writing_prompt = self.expert_prompt_template.format(
            topic=chapter['title'],
            search_results=formatted_results,
            content_outline=content_outline_text,
            learning_objectives=learning_objectives_text
        )
        
        try:
            response = self.client.openai.chat.completions.create(
                model=self.client.model,
                messages=[{"role": "user", "content": writing_prompt}],
                max_tokens=self.config['article_generation']['max_tokens'],
                temperature=self.config['article_generation']['writing_temperature'],
            )
            
            content = response.choices[0].message.content
            
            if verbose:
                print("✓ 文章生成完成")
            
            return content
            
        except Exception as e:
            print(f"✗ 文章生成失败: {e}")
            raise
    
    def _format_search_results(self) -> str:
        """格式化搜索结果"""
        if not self.search_results:
            return "（暂无参考资料）"
        
        formatted = []
        for i, item in enumerate(self.search_results, 1):
            query = item['query']
            result = item['result']
            
            # 更自然的格式，便于 AI 理解和引用
            formatted.append(f"""
## 参考资料 {i}

**搜索主题**：{query}

**相关信息**：
{result}

---
""")
        
        return "\n".join(formatted)
    
    def _build_research_prompt(self, topic: str, chapter: Dict) -> str:
        """构建研究提示词"""
        # 格式化学习目标
        objectives = chapter.get('learning_objectives', [])
        objectives_text = "\n".join(f"  • {obj}" for obj in objectives) if objectives else "  暂无"
        
        # 格式化核心概念
        concepts = chapter.get('key_concepts', [])
        concepts_text = "、".join(concepts) if concepts else "暂无"
        
        # 格式化内容大纲
        outline = chapter.get('content_outline', [])
        outline_text = "\n".join(f"  {i}. {item}" for i, item in enumerate(outline, 1)) if outline else "  暂无"
        
        return f"""我需要为以下主题撰写一篇技术文章，请帮我收集全面、权威的资料。

📖 文章主题：
{chapter.get('title', topic)}

🎯 学习目标：
{objectives_text}

🔑 核心概念：
{concepts_text}

📋 内容要点：
{outline_text}

请按以下维度收集信息：
1. 概念定义和理论基础
2. 技术原理和实现方法
3. 实际应用案例（最好是知名产品）
4. 代码示例和最佳实践
5. 性能数据和效果对比
6. 研究进展和未来趋势

注意：
- 优先搜索权威来源（论文、官方文档、技术博客）
- 关注 2023-2025 年的最新进展
- 收集具体的数据和案例，而非泛泛而谈
- 避免重复搜索已知内容

开始搜索吧！"""
    
    def _generate_frontmatter(
        self, 
        topic_name: str, 
        chapter: Dict, 
        curriculum: Dict
    ) -> Dict:
        """生成frontmatter"""
        # 提取分类
        categories = ["AI", "深度学习"]
        
        # 根据主题添加特定分类
        topic_lower = topic_name.lower()
        if any(kw in topic_lower for kw in ["transformer", "注意力", "attention"]):
            categories.append("Transformer")
        if any(kw in topic_lower for kw in ["vla", "vision", "language", "action"]):
            categories.append("多模态")
        if any(kw in topic_lower for kw in ["强化学习", "reinforcement", "rl"]):
            categories.append("强化学习")
        if any(kw in topic_lower for kw in ["agent", "智能体"]):
            categories.append("AI Agent")
        
        # 从章节提取标签
        tags = []
        
        # 从核心概念提取（限制数量）
        key_concepts = chapter.get('key_concepts', [])[:5]
        tags.extend(key_concepts)
        
        # 去重和清理
        tags = list(dict.fromkeys([t.strip() for t in tags if t.strip()]))
        categories = list(dict.fromkeys(categories))
        
        return {
            "title": chapter['title'],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "author": "AI技术专家",
            "categories": categories,
            "tags": tags,
            "description": chapter.get('subtitle', chapter['title'])[:150],
            "series": curriculum.get('curriculum_name', topic_name),
            "chapter": chapter.get('chapter_number', 1),
            "difficulty": chapter.get('difficulty', 'intermediate'),
            "estimated_reading_time": f"{chapter.get('estimated_reading_time', 15)}分钟"
        }
    
    def _compose_article(self, frontmatter: Dict, content: str) -> str:
        """组合完整文章"""
        # 清理内容：如果模型生成了 frontmatter，需要移除
        content = content.strip()
        
        # 检测并移除内容开头的 frontmatter
        if content.startswith("---"):
            # 找到第二个 --- 的位置
            second_delimiter = content.find("---", 3)
            if second_delimiter != -1:
                # 移除整个 frontmatter 块
                content = content[second_delimiter + 3:].strip()
                print("⚠️  检测到模型生成了 frontmatter，已自动移除")
        
        # 生成我们自己的 YAML frontmatter
        fm_lines = ["---"]
        for key, value in frontmatter.items():
            if isinstance(value, list):
                fm_lines.append(f"{key}:")
                for item in value:
                    fm_lines.append(f"  - {item}")
            else:
                fm_lines.append(f"{key}: {value}")
        fm_lines.append("---")
        fm_lines.append("")
        
        return "\n".join(fm_lines) + "\n" + content
    
    def _save_article(
        self, 
        topic_name: str, 
        chapter_number: int,
        chapter_title: str,
        content: str
    ) -> Path:
        """保存文章到文件"""
        output_dir = Path(__file__).parent / self.config['storage']['articles_output']
        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名：直接使用章节标题作为文件名（适合作为博客标题）
        # 清理文件名中的非法字符，但保留中文、英文、数字和常用分隔符
        import re
        
        # 保留中文、英文、数字、空格、连字符和下划线
        safe_title = re.sub(r'[^\w\s\-\u4e00-\u9fff]', '', chapter_title)
        # 将多个空格替换为单个下划线
        safe_title = re.sub(r'\s+', '_', safe_title.strip())
        # 限制长度
        safe_title = safe_title[:100]
        
        # 如果标题为空，使用备用方案
        if not safe_title:
            safe_title = f"{topic_name}_Chapter_{chapter_number}"
            safe_title = re.sub(r'[^\w\s\-\u4e00-\u9fff]', '', safe_title)
            safe_title = re.sub(r'\s+', '_', safe_title.strip())
        
        filename = f"{safe_title}.md"
        output_path = output_dir / filename
        
        # 如果文件已存在，添加时间戳后缀
        if output_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_title}_{timestamp}.md"
            output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def _get_curriculum(self, topic_name: str) -> Optional[Dict]:
        """获取教程大纲（支持模糊匹配）"""
        import re
        
        def normalize_name(name: str) -> str:
            """规范化主题名称：移除所有分隔符、统一为小写"""
            name = name.lower()
            # 移除所有括号、连字符、下划线、空格
            name = re.sub(r'[（）()_\-\s]+', '', name)
            return name
        
        normalized_search = normalize_name(topic_name)
        
        # 首先尝试精确匹配
        for curr in self.curriculum_db.get("curriculums", []):
            curr_topic = curr.get("main_topic", "")
            if normalize_name(curr_topic) == normalized_search:
                return curr
        
        # 如果精确匹配失败，尝试部分匹配
        for curr in self.curriculum_db.get("curriculums", []):
            curr_topic = normalize_name(curr.get("main_topic", ""))
            # 检查是否包含搜索词的主要部分
            if normalized_search in curr_topic or curr_topic in normalized_search:
                return curr
        
        return None
    
    def _get_chapter(self, curriculum: Dict, chapter_number: int) -> Optional[Dict]:
        """获取指定章节"""
        for chapter in curriculum.get("chapters", []):
            if chapter.get("chapter_number") == chapter_number:
                return chapter
        return None
    
    def generate_series(
        self, 
        topic_name: str, 
        chapter_range: Optional[tuple] = None,
        verbose: bool = True
    ):
        """生成系列教程"""
        curriculum = self._get_curriculum(topic_name)
        if not curriculum:
            raise ValueError(f"未找到主题 '{topic_name}' 的教程大纲")
        
        chapters = curriculum.get("chapters", [])
        total = len(chapters)
        
        if chapter_range:
            start, end = chapter_range
            chapters = [ch for ch in chapters if start <= ch.get('chapter_number', 0) <= end]
        
        print(f"\n{'='*70}")
        print(f"📚 批量生成教程系列")
        print(f"   主题: {topic_name}")
        print(f"   章节: {len(chapters)}/{total}")
        print(f"{'='*70}\n")
        
        results = []
        for i, chapter in enumerate(chapters, 1):
            ch_num = chapter.get('chapter_number', i)
            print(f"[{i}/{len(chapters)}] 生成第{ch_num}章: {chapter['title']}")
            print("-" * 70)
            
            try:
                result = self.generate_article(topic_name, ch_num, verbose=verbose)
                results.append(result)
            except Exception as e:
                print(f"✗ 生成失败: {e}\n")
                continue
            
            # 避免请求过快
            if i < len(chapters):
                import time
                print("\n⏳ 等待 5 秒...\n")
                time.sleep(5)
        
        print(f"{'='*70}")
        print(f"✅ 系列生成完成 - 成功 {len(results)}/{len(chapters)}")
        print(f"{'='*70}\n")
        
        return results
    
    def close(self):
        """关闭客户端"""
        self.client.close()


def main():
    """测试文章生成器"""
    import argparse
    
    parser = argparse.ArgumentParser(description='文章生成器')
    parser.add_argument('-t', '--topic', type=str, required=True, help='主题名称')
    parser.add_argument('-n', '--chapter', type=int, help='章节编号')
    parser.add_argument('-r', '--range', type=str, help='章节范围，如 1-5')
    parser.add_argument('-a', '--all', action='store_true', help='生成所有章节')
    parser.add_argument('-c', '--config', type=str, help='配置文件路径')
    
    args = parser.parse_args()
    
    try:
        generator = ArticleGenerator(config_path=args.config)
        
        if args.all:
            generator.generate_series(args.topic, verbose=True)
        elif args.range:
            start, end = map(int, args.range.split('-'))
            generator.generate_series(args.topic, chapter_range=(start, end), verbose=True)
        elif args.chapter:
            generator.generate_article(args.topic, args.chapter, verbose=True)
        else:
            print("请指定章节编号 (-n) 或范围 (-r) 或全部 (-a)")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'generator' in locals():
            generator.close()


if __name__ == "__main__":
    main()

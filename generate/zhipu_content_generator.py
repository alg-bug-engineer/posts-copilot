#!/usr/bin/env python3
"""
zhipu_content_generator.py

使用智谱AI API生成文章标题和内容
面向AI和大模型领域，为AI从业者提供专业、通俗易懂的技术内容
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from zhipuai import ZhipuAI


class ZhipuContentGenerator:
    """智谱AI内容生成器 - 专注于AI和大模型领域"""
    
    # 默认的领域和受众设置
    DEFAULT_DOMAIN = "AI、大模型、机器学习"
    DEFAULT_AUDIENCE = "AI领域从业者、算法工程师、技术研发人员"
    DEFAULT_STYLE = "通俗易懂、夹叙夹议、深入浅出"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化智谱AI客户端
        
        Args:
            api_key: API密钥，如果为None则从环境变量ZHIPUAI_API_KEY读取
        """
        self.api_key = api_key or os.environ.get("ZHIPUAI_API_KEY")
        if not self.api_key:
            raise ValueError("请提供智谱AI API Key，或设置环境变量 ZHIPUAI_API_KEY")
        
        self.client = ZhipuAI(api_key=self.api_key)
    
    def generate_article_with_keyword(
        self, 
        keyword: str,
        auto_generate_title: bool = True,
        custom_title: Optional[str] = None,
        min_words: int = 1500,
        max_words: int = 2500
    ) -> Dict[str, Any]:
        """
        根据关键词生成完整文章（包含Front Matter）
        这是主要的对外接口
        
        Args:
            keyword: 关键词（必填）
            auto_generate_title: 是否自动生成标题，默认True
            custom_title: 自定义标题，如果提供则不自动生成
            min_words: 最小字数
            max_words: 最大字数
            
        Returns:
            包含以下键的字典：
            - title: 文章标题
            - description: 文章摘要
            - tags: 标签列表
            - content: 完整的Markdown内容（包含Front Matter）
            - content_without_frontmatter: 不含Front Matter的正文
        """
        print(f"\n{'='*60}")
        print(f"🚀 开始生成文章：关键词 = {keyword}")
        print(f"{'='*60}\n")
        
        # 确定标题
        if custom_title:
            title = custom_title
            print(f"✓ 使用自定义标题：{title}")
        elif auto_generate_title:
            print("📝 正在生成标题...")
            titles = self.generate_titles(keyword=keyword, count=1)
            title = titles[0] if titles else f"{keyword}深度解析"
            print(f"✓ 标题生成完成：{title}")
        else:
            title = f"{keyword}深度解析"
            print(f"✓ 使用默认标题：{title}")
        
        # 生成文章内容
        print("\n📄 正在生成文章内容...")
        content = self._generate_article_content(
            title=title,
            keyword=keyword,
            min_words=min_words,
            max_words=max_words
        )
        print(f"✓ 文章内容生成完成（{len(content)}字符）")
        
        # 生成描述和标签
        print("\n🏷️  正在生成描述和标签...")
        description = self._generate_description(title, content)
        tags = self._generate_tags(keyword, title)
        print(f"✓ 描述：{description}")
        print(f"✓ 标签：{', '.join(tags)}")
        
        # 添加Front Matter
        print("\n📋 正在添加Front Matter...")
        full_content = self._add_front_matter(
            title=title,
            description=description,
            tags=tags,
            content=content
        )
        print("✓ Front Matter添加完成")
        
        print(f"\n{'='*60}")
        print("🎉 文章生成完成！")
        print(f"{'='*60}\n")
        
        return {
            'title': title,
            'description': description,
            'tags': tags,
            'content': full_content,
            'content_without_frontmatter': content
        }
    
    def generate_titles(self, keyword: Optional[str] = None, count: int = 10) -> List[str]:
        """
        生成文章标题（优化为AI和大模型领域）
        
        Args:
            keyword: 关键词，如果为None则基于AI领域热门话题
            count: 生成标题数量，默认10个
            
        Returns:
            标题列表
        """
        if keyword:
            prompt = f"""作为一名资深的AI和大模型领域技术博客作者，请围绕关键词"{keyword}"生成{count}个专业且吸引人的技术文章标题。

领域定位：{self.DEFAULT_DOMAIN}
目标读者：{self.DEFAULT_AUDIENCE}

标题要求：
1. 专业性：体现AI和大模型领域的技术深度
2. 实用性：聚焦实际应用场景和问题解决
3. 吸引力：标题要有亮点，激发读者兴趣
4. 长度适中：15-35个字之间
5. 形式多样：可以是"深度解析"、"实战指南"、"原理剖析"、"最佳实践"等
6. 避免标题党：不夸大、不误导
7. 关注热点：结合当前AI领域的技术趋势

标题风格示例：
- XXX技术深度解析：原理、实现与应用
- 从零到一：XXX实战指南
- XXX vs XXX：技术对比与选型建议
- 揭秘XXX：底层原理与优化策略
- XXX最佳实践：企业级应用案例分析

注意事项：
- 不要使用书名号《》等标点符号包裹标题
- 标题要简洁有力，直接点明主题

请直接输出{count}个标题，每行一个，不要序号："""
        else:
            prompt = f"""作为一名资深的AI和大模型领域技术博客作者，请基于当前AI领域的最新技术趋势和热门话题，生成{count}个专业且吸引人的技术文章标题。

领域定位：{self.DEFAULT_DOMAIN}
目标读者：{self.DEFAULT_AUDIENCE}

热门主题方向（可参考）：
- 大语言模型（LLM）：GPT、Claude、LLaMA等
- AI应用开发：RAG、Agent、Prompt Engineering
- 模型训练与优化：微调、量化、推理加速
- AI基础设施：向量数据库、模型部署、MLOps
- 多模态AI：图文、语音、视频理解
- AI安全与伦理：对齐、安全、隐私保护

标题要求：
1. 紧跟AI技术发展前沿
2. 体现技术深度和实用价值
3. 适合技术博客平台发布
4. 长度15-35个字之间
5. 形式多样化
6. 不要序号，直接输出标题
7. 不要使用书名号《》等标点符号包裹标题

请直接输出{count}个标题，每行一个："""
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # 解析标题列表
            titles = []
            for line in content.split('\n'):
                line = line.strip()
                # 移除序号
                line = re.sub(r'^[\d\.\、\-》>]+\s*', '', line).strip()
                if line and len(line) >= 5:
                    titles.append(line)
            
            if len(titles) < count:
                print(f"警告: 只生成了 {len(titles)} 个标题")
            
            return titles[:count]
            
        except Exception as e:
            print(f"生成标题时出错: {e}")
            raise
    
    def _generate_article_content(
        self, 
        title: str, 
        keyword: str,
        min_words: int = 1500,
        max_words: int = 2500
    ) -> str:
        """生成文章正文内容"""
        prompt = f"""作为一名资深的AI和大模型领域技术专家，请根据标题"{title}"撰写一篇高质量的技术文章。

【领域定位】
- 专注领域：{self.DEFAULT_DOMAIN}
- 目标读者：{self.DEFAULT_AUDIENCE}
- 写作风格：{self.DEFAULT_STYLE}

【核心关键词】
{keyword}

【内容要求】

1. 文章结构（必须完整）：
   - 开篇引言：简要介绍背景、痛点或趋势（100-200字）
   - 核心内容：3-5个主要章节，每个章节深入展开（使用 ## 二级标题）
   - 实战示例：至少包含1-2个代码示例或应用场景
   - 总结展望：总结要点，给出建议或展望（100-200字）

2. 写作风格要求：
   - 通俗易懂：避免过度学术化，用生动的比喻和例子
   - 夹叙夹议：既讲技术原理，也谈个人见解和行业观察
   - 深入浅出：从简单到复杂，循序渐进
   - 实战导向：理论结合实践，给出可操作的建议
   - 自然流畅：避免使用"总之"、"综上所述"、"首先"、"其次"、"然后"、"最后"等AI式过渡词
   - 口语化表达：像与朋友交流般自然，可以用"我们来看"、"这里需要注意"、"实际应用中"等自然过渡

3. 内容形式要求（丰富化）：
   - 使用列表：核心要点用无序列表或有序列表
   - 使用表格：对比、参数说明等适合用表格
   - 使用代码块：技术示例要有完整的代码展示
   - 使用引用：重要观点用 > 引用块强调
   - 使用加粗：关键术语和重点内容用 **加粗**
   - 使用斜体：强调或英文术语用 *斜体*

4. 专业性要求：
   - 技术准确：概念、原理、代码都要准确无误
   - 有深度：不止停留在表面，要深入原理和实现
   - 有广度：关联相关技术，给出技术选型建议
   - 有前瞻：提及技术趋势和未来发展

5. Markdown格式规范：
   - 使用 ## 作为主要章节标题（二级标题）
   - 使用 ### 作为小节标题（三级标题）
   - 代码块要标注语言：```python、```bash等
   - 列表项之间要有空行
   - 段落之间要有空行

6. 字数要求：
   - 正文字数：{min_words}-{max_words}字
   - 结构完整，不要虎头蛇尾

【特别注意】
- 不要在开头重复文章标题
- 不要输出 Front Matter
- 直接从引言部分开始
- 确保输出的是规范的Markdown格式

请开始撰写文章正文："""
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=8000
            )
            
            content = response.choices[0].message.content.strip()
            content = self._clean_markdown_wrapper(content)
            content = self._remove_duplicate_title(content, title)
            
            return content
            
        except Exception as e:
            print(f"生成文章内容时出错: {e}")
            raise
    
    def _generate_description(self, title: str, content: str, max_length: int = 120) -> str:
        """生成文章摘要描述"""
        prompt = f"""请为以下技术文章生成一个简洁、吸引人的摘要描述。

文章标题：{title}

文章内容：
{content[:500]}...

要求：
1. 摘要长度：{max_length}字以内
2. 简明扼要地概括文章的核心内容和价值
3. 突出技术亮点和实用性
4. 适合在文章列表、推荐页面等场景展示
5. 不要使用"本文"、"这篇文章"等开头
6. 直接描述内容，语言精练

请直接输出摘要，不要其他内容："""
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            description = response.choices[0].message.content.strip()
            description = description.strip('"\'')
            
            if len(description) > max_length:
                description = description[:max_length-3] + "..."
            
            return description
            
        except Exception as e:
            print(f"生成描述时出错: {e}")
            return self._extract_description_from_content(content, max_length)
    
    def _generate_tags(self, keyword: str, title: str, max_tags: int = 5) -> List[str]:
        """生成文章标签"""
        prompt = f"""请为以下技术文章生成{max_tags}个精准的标签。

文章标题：{title}
核心关键词：{keyword}

标签要求：
1. 与AI、大模型领域相关
2. 准确反映文章的技术主题
3. 有助于文章的搜索和分类
4. 每个标签2-8个字
5. 既要有通用标签，也要有细分标签
6. 优先使用常见的技术术语

示例标签：
- 大语言模型、LLM、GPT
- Prompt工程、RAG、向量数据库
- 模型微调、量化、推理优化
- AI应用开发、AI Agent
- 机器学习、深度学习
- Python、PyTorch、TensorFlow

请直接输出{max_tags}个标签，每行一个，不要序号："""
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            tags = []
            for line in content.split('\n'):
                line = line.strip()
                line = re.sub(r'^[\d\.\、\-#]+\s*', '', line).strip()
                line = line.strip('"\'')
                if line and len(line) >= 2:
                    tags.append(line)
            
            if keyword not in tags:
                tags.insert(0, keyword)
            
            return tags[:max_tags]
            
        except Exception as e:
            print(f"生成标签时出错: {e}")
            return self._extract_tags_from_keyword(keyword, max_tags)
    
    def _add_front_matter(
        self, 
        title: str, 
        description: str, 
        tags: List[str], 
        content: str
    ) -> str:
        """为文章添加Front Matter"""
        front_matter_lines = [
            "---",
            f'title: "{title}"',
            f'description: "{description}"',
            "tags:"
        ]
        
        for tag in tags:
            front_matter_lines.append(f'  - "{tag}"')
        
        front_matter_lines.append("---")
        front_matter_lines.append("")
        
        front_matter = '\n'.join(front_matter_lines)
        full_content = f"{front_matter}\n{content}"
        
        return full_content
    
    def _extract_description_from_content(self, content: str, max_length: int = 120) -> str:
        """从内容中提取描述（备用方案）"""
        text = re.sub(r'[#*`\[\]]+', '', content)
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        return text
    
    def _extract_tags_from_keyword(self, keyword: str, max_tags: int = 5) -> List[str]:
        """从关键词提取标签（备用方案）"""
        tags = [keyword]
        default_tags = ["AI", "大模型", "机器学习", "深度学习", "人工智能"]
        
        for tag in default_tags:
            if tag not in tags and len(tags) < max_tags:
                tags.append(tag)
        
        return tags[:max_tags]
    
    def _remove_duplicate_title(self, content: str, title: str) -> str:
        """移除内容开头可能重复的标题"""
        lines = content.split('\n')
        
        if lines and lines[0].strip().lstrip('#').strip() == title:
            content = '\n'.join(lines[1:]).lstrip()
        
        return content
    
    def _extract_keyword_from_title(self, title: str) -> str:
        """从标题中提取关键词"""
        stopwords = ['深度', '解析', '指南', '实战', '详解', '探索', '揭秘', '最佳', '实践', 
                    '从', '到', '：', ':', '、', '与', '和', '的', '了']
        
        keyword = title
        for word in stopwords:
            keyword = keyword.replace(word, ' ')
        
        words = [w.strip() for w in keyword.split() if w.strip()]
        return words[0] if words else title
    
    def save_article_to_file(
        self, 
        content: str, 
        title: str,
        output_dir: Path = None
    ) -> Path:
        """
        保存文章到文件
        
        Args:
            content: 文章内容
            title: 文章标题
            output_dir: 输出目录，默认为当前目录下的posts
            
        Returns:
            保存的文件路径
        """
        if output_dir is None:
            output_dir = Path.cwd() / "posts"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 清理文件名
        safe_filename = self._sanitize_filename(title)
        filepath = output_dir / f"{safe_filename}.md"
        
        # 如果文件已存在，添加时间戳
        if filepath.exists():
            timestamp = datetime.now().strftime("%H%M%S")
            filepath = output_dir / f"{safe_filename}_{timestamp}.md"
        
        # 保存文章
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 文章已保存到: {filepath}")
        return filepath
    
    @staticmethod
    def _clean_markdown_wrapper(content: str) -> str:
        """清理Markdown内容中的代码块包裹标记"""
        content = content.strip()
        
        if content.startswith('```'):
            first_newline = content.find('\n')
            if first_newline != -1:
                content = content[first_newline + 1:]
            else:
                content = content[3:].lstrip()
        
        if content.endswith('```'):
            content = content.rstrip('`').rstrip()
        
        pattern = r'^```(?:markdown|md|text)?\s*\n(.*?)\n```\s*$'
        match = re.match(pattern, content, re.DOTALL)
        if match:
            content = match.group(1)
        
        return content.strip()
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """清理文件名"""
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '')
        
        filename = filename.strip()
        
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename


def main():
    """命令行测试入口"""
    import sys
    
    keyword = None
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
    else:
        keyword = input("请输入关键词（如：RAG、大模型微调、Prompt工程等）: ").strip()
    
    if not keyword:
        print("错误: 请提供关键词")
        sys.exit(1)
    
    try:
        generator = ZhipuContentGenerator()
        
        # 生成文章
        result = generator.generate_article_with_keyword(keyword=keyword)
        
        # 保存到文件
        filepath = generator.save_article_to_file(
            content=result['content'],
            title=result['title']
        )
        
        print(f"\n{'='*60}")
        print("✅ 任务完成！")
        print(f"{'='*60}")
        print(f"📄 标题: {result['title']}")
        print(f"�� 描述: {result['description']}")
        print(f"🏷️  标签: {', '.join(result['tags'])}")
        print(f"💾 文件: {filepath}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

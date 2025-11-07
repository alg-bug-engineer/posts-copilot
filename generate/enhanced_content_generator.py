#!/usr/bin/env python3
"""
enhanced_content_generator.py

增强版内容生成器
基于参考资料和风格模板，生成高仿风格但内容有差异的技术文章
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from zhipuai import ZhipuAI


class EnhancedContentGenerator:
    """增强版内容生成器 - 支持风格模仿和内容创新"""
    
    # 量子位风格特征
    QBITAI_STYLE = """
【量子位文章风格特征】

标题风格：
- 简洁有力，不用冒号分隔
- 常用惊叹号增加冲击力
- 突出核心数据或关键词
- 示例："马斯克薪酬破万亿美元！"而非"马斯克薪酬：破万亿美元的背后"

开篇特点：
- 直接抛数据或核心事件
- 制造话题感和冲击力  
- 不铺垫，不废话
- 示例："就在刚刚，XX公司宣布..."

叙述方式：
- 新闻报道节奏，信息密度大
- 短段落为主（3-5行）
- 一段说一个点，不贪多
- 段落间自然过渡，不用连接词

语言风格：
- 口语化，像朋友聊天
- 有态度，有情感
- 数据驱动，用数字说话
- 引用网友评论增加互动感

段落组织：
- 不用"首先其次然后"
- 不用"总之综上所述"  
- 直接说事，自然过渡
- 可以用短句成段

格式使用：
- 克制使用章节标题
- 更多靠段落自然划分
- 加粗用于关键数据
- 列表用于罗列要点
"""
    
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
    
    def generate_article_from_news(
        self,
        news_item: Dict[str, str],
        references: Dict[str, Any],
        style: str = "qbitai",
        output_dir: str = "posts"
    ) -> Dict[str, Any]:
        """
        基于新闻和参考资料生成文章
        
        Args:
            news_item: 新闻信息，包含title、summary、tags等
            references: 参考资料，来自ReferenceSearcher
            style: 写作风格，默认"qbitai"（量子位风格）
            output_dir: 输出目录
            
        Returns:
            包含文章内容和元信息的字典
        """
        print(f"\n{'='*70}")
        print(f"✍️  开始生成文章: {news_item.get('title', '')}")
        print(f"{'='*70}\n")
        
        # 生成新标题（基于原标题，但有创新）
        print("📝 [1/5] 生成创新标题...")
        new_title = self._generate_creative_title(
            original_title=news_item.get('title', ''),
            topic=references.get('topic', ''),
            tags=news_item.get('tags', [])
        )
        print(f"  ✓ 新标题: {new_title}")
        
        # 生成文章正文
        print("\n📄 [2/5] 生成文章正文...")
        content = self._generate_article_content(
            title=new_title,
            original_summary=news_item.get('summary', ''),
            references=references,
            style=style
        )
        print(f"  ✓ 正文生成完成 ({len(content)} 字符)")
        
        # 生成描述
        print("\n🏷️  [3/5] 生成文章描述...")
        description = self._generate_description(new_title, content)
        print(f"  ✓ 描述: {description[:50]}...")
        
        # 生成标签
        print("\n🔖 [4/5] 生成文章标签...")
        tags = self._generate_tags(
            original_tags=news_item.get('tags', []),
            content=content[:500]
        )
        print(f"  ✓ 标签: {', '.join(tags)}")
        
        # 添加Front Matter
        print("\n📋 [5/5] 添加Front Matter...")
        full_content = self._add_front_matter(
            title=new_title,
            description=description,
            tags=tags,
            content=content
        )
        
        # 保存文章
        output_path = self._save_article(new_title, full_content, output_dir)
        
        print(f"\n{'='*70}")
        print(f"🎉 文章生成完成！")
        print(f"📁 保存位置: {output_path}")
        print(f"{'='*70}\n")
        
        return {
            'title': new_title,
            'description': description,
            'tags': tags,
            'content': full_content,
            'file_path': output_path,
            'original_news': news_item
        }
    
    def _generate_creative_title(
        self,
        original_title: str,
        topic: str,
        tags: List[str]
    ) -> str:
        """
        生成创新标题 - 保持原意但表达不同
        """
        prompt = f"""你是一位资深的科技媒体编辑，请基于原标题生成一个创新性的新标题。

原标题：{original_title}
核心主题：{topic}
相关标签：{', '.join(tags) if tags else '无'}

【重要】创新要求：
1. **必须大幅改写**，不能只是简单替换几个词
2. 可以改变叙述角度：
   - 从结果导向改为过程导向
   - 从技术角度改为应用角度
   - 从宏观改为微观，或反之
3. 使用完全不同的表达方式和结构
4. 保持核心信息但换一种说法
5. 长度15-35字
6. 体现量子位风格但不拘泥于固定模式

标题改写示例：
原标题："Kimi K2 Thinking突袭！智能体&推理能力超GPT-5"
创新改写：
- "月之暗面放大招：K2模型推理实力碾压GPT-5"
- "国产AI新突破！Kimi K2让智能体能力跃升一个档次"
- "不只是模型升级：Kimi K2如何重新定义AI推理？"

原标题："马斯克1万亿美元薪酬方案获批！"
创新改写：
- "史上最贵打工人！马斯克薪酬包价值破万亿美元"
- "特斯拉股东通过：给马斯克发1万亿薪水"
- "万亿薪酬背后：马斯克要完成的地狱级OKR"

请输出一个创新性强、与原标题差异明显的新标题："""
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9  # 提高温度增加创新性
            )
            
            new_title = response.choices[0].message.content.strip()
            # 清理可能的引号
            new_title = new_title.strip('"\'""''')
            
            # 验证标题差异度（简单检查）
            # 如果新标题和原标题相似度太高，重试一次
            if self._calculate_similarity(new_title, original_title) > 0.7:
                print(f"  ⚠️ 标题相似度过高，重新生成...")
                response = self.client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": new_title},
                        {"role": "user", "content": "这个标题和原标题太相似了，请生成一个完全不同角度的标题，改变表达方式和结构"}
                    ],
                    temperature=0.95
                )
                new_title = response.choices[0].message.content.strip().strip('"\'""''')
            
            return new_title
            
        except Exception as e:
            print(f"  ⚠️ 标题生成失败，使用原标题: {e}")
            return original_title
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度（简单版本）
        """
        # 移除标点符号
        import re
        t1 = re.sub(r'[^\w\s]', '', text1.lower())
        t2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        # 计算字符集合的Jaccard相似度
        set1 = set(t1)
        set2 = set(t2)
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _generate_article_content(
        self,
        title: str,
        original_summary: str,
        references: Dict[str, Any],
        style: str = "qbitai"
    ) -> str:
        """
        生成文章正文 - 融合参考资料
        """
        # 构建参考资料摘要
        ref_summary = self._build_reference_summary(references)
        
        style_guide = self.QBITAI_STYLE if style == "qbitai" else ""
        
        prompt = f"""你是量子位的资深技术记者，有10年科技报道经验。请根据以下信息撰写一篇深度科技报道。

【文章标题】
{title}

【核心信息】
{original_summary}

【技术背景与参考资料】
{ref_summary}

{style_guide}

【核心要求】

一、内容深度（必须达到2000-3000字）

开篇部分（150-200字）
- 直接切入核心事件或关键数据
- 用简洁有力的陈述句开场
- 例如："刚刚宣布"、"最新数据显示"、"业内证实"
- 避免冗长铺垫

主体内容（分4-6个段落，每段200-400字）
- 用准确的技术术语解释原理
- 提供具体案例和应用场景
- 必须引用准确的数据和性能指标
- 段落间逻辑严密，过渡自然
- 保持客观中立的报道立场

结尾部分（100-150字）
- 行业展望或专家观点
- 市场分析或技术趋势
- 避免使用"总之"、"总结"等词
- 自然收尾

二、语言风格（专业性要求）

严格禁用的表达方式：
- "首先"、"其次"、"然后"、"最后"（列举式过渡词）
- "总之"、"综上所述"、"总的来说"（总结式结尾）
- "值得注意的是"、"需要指出的是"（提示性表达）
- "通过...实现"、"基于...技术"（模式化句式）
- "为...提供了"、"使得...成为可能"（功能描述套话）

推荐的专业表达：
- 直接陈述事实："数据显示"、"测试结果表明"、"官方透露"
- 引用来源："据了解"、"公司方面表示"、"业内人士称"
- 转折连接："与此同时"、"实际情况是"、"另一方面"
- 深入分析："背后原因在于"、"关键突破点是"、"核心竞争力体现在"

段落组织原则：
- 采用倒金字塔结构，重要信息前置
- 单一段落聚焦单一主题
- 段落长度灵活：短段强调，长段分析
- 使用过渡句保持连贯性

三、格式规范（技术新闻标准）

标题使用：
- 正文避免使用二级标题（##）
- 保持内容的连贯性和流畅性
- 如确需分节，使用简洁的关键词作为标题
- 避免"XX：XX"的冗长标题格式

强调手法：
- 使用**加粗**标注关键数据和核心观点
- 每段加粗不超过2处，保持克制
- 直接呈现数据，无需额外强调符号

列表使用：
- 仅用于罗列技术参数、功能特性、对比数据
- 列表项保持简洁，单行呈现
- 避免过度使用列表

引用块：
- 用于引述专家观点或重要声明
- 全文最多使用1-2次

四、写作技巧（专业深度）

数据驱动：
- 准确引用性能指标："提升300%"、"延迟降至10ms"
- 提供对比数据："相比上代产品"、"行业平均水平"
- 注明数据来源和测试条件

案例支撑：
- 描述真实应用场景
- 举例说明技术价值
- 引用实际部署案例

分析深度：
- 剖析技术原理和实现路径
- 对比竞品或前代技术
- 分析市场影响和行业趋势

信源可靠：
- 引用官方声明
- 采访业内专家
- 参考权威研究报告

五、字数分配

开篇：150-200字
主体部分：1600-2500字（分4-6个段落）
结尾：100-150字
总计：2000-3000字（必须严格达到）

【写作禁忌】

不要使用总结段落
不要出现"这说明"、"可以看出"等分析套话
不要使用"从XX角度来看"的视角切换
不要使用"随着...的发展"的时间铺垫
不要在正文中重复标题
不要使用过于口语化的表达
不要使用整齐划一的段落长度
不要采用机械的结构模式

【质量标准】

客观准确：事实清楚，数据可靠
专业深度：技术分析到位，不浅尝辄止
信息密度：内容充实，避免空洞表述
可读性：逻辑清晰，表达流畅
时效性：体现最新动态和趋势

【输出格式要求】

⚠️ 重要：直接输出文章正文，不要包含任何元标记！

严禁输出以下内容：
❌ 【文章标题】、【开篇部分】、【主体内容】、【结尾部分】
❌ 【正文】、【内容】、【导语】、【结语】
❌ 任何用【】括起来的标记或分段标识
❌ markdown代码块标记（```）

✅ 正确输出格式：
直接从文章正文第一段开始
不包含任何元信息或标记
纯净的markdown格式文本

现在，按照专业科技新闻标准开始写作（严格要求：2000字以上，客观专业，无AI痕迹，无元标记）："""
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,  # 提高一点，让表达更自然多样
                max_tokens=12000  # 增加token限制，确保能生成足够长的内容
            )
            
            content = response.choices[0].message.content.strip()
            
            # 清理markdown标记
            content = content.replace('```markdown', '').replace('```', '').strip()
            
            # 移除可能重复的标题
            content = self._remove_duplicate_title(content, title)
            
            # 后处理：清理AI生成的标记
            content = self._post_process_content(content)
            
            # 检查内容长度
            content_length = len(content)
            if content_length < 1500:
                print(f"  ⚠️ 内容过短({content_length}字符)，这不符合要求")
            else:
                print(f"  ✓ 内容长度: {content_length}字符")
            
            return content
            
        except Exception as e:
            print(f"  ❌ 内容生成失败: {e}")
            raise
    
    def _build_reference_summary(self, references: Dict[str, Any]) -> str:
        """
        构建参考资料摘要
        """
        parts = []
        
        if references.get('technical_background'):
            parts.append(f"**技术背景**\n{references['technical_background'][:500]}")
        
        if references.get('key_innovations'):
            innovations = '\n'.join([f"- {item}" for item in references['key_innovations'][:5]])
            parts.append(f"**关键创新点**\n{innovations}")
        
        if references.get('application_scenarios'):
            scenarios = '\n'.join([f"- {item}" for item in references['application_scenarios'][:3]])
            parts.append(f"**应用场景**\n{scenarios}")
        
        if references.get('industry_impact'):
            parts.append(f"**行业影响**\n{references['industry_impact'][:300]}")
        
        return '\n\n'.join(parts) if parts else "（暂无详细参考资料）"
    
    def _generate_description(self, title: str, content: str) -> str:
        """
        生成文章描述/摘要
        """
        # 提取内容的前300字作为上下文
        context = content[:300]
        
        prompt = f"""请为以下文章生成一个简短的描述（摘要），用于SEO和文章预览。

标题：{title}
内容片段：{context}

要求：
1. 50-100字
2. 概括文章核心内容
3. 吸引读者阅读
4. 包含关键技术词
5. 简洁明了

请直接输出描述，不要其他内容："""
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            
            description = response.choices[0].message.content.strip()
            return description[:150]  # 确保不超过150字
            
        except Exception as e:
            print(f"  ⚠️ 描述生成失败，使用默认: {e}")
            return title
    
    def _generate_tags(
        self,
        original_tags: List[str],
        content: str
    ) -> List[str]:
        """
        生成文章标签
        """
        prompt = f"""请基于以下信息生成5个合适的文章标签。

原始标签：{', '.join(original_tags) if original_tags else '无'}
内容片段：{content}

要求：
1. 标签要准确反映文章内容
2. 包含技术关键词
3. 可以基于原始标签，但要适当调整和扩展
4. 标签长度2-6个字
5. 避免过于宽泛的标签

请直接输出标签列表，用逗号分隔："""
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            
            tags_text = response.choices[0].message.content.strip()
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            
            # 确保至少有3个标签
            if len(tags) < 3 and original_tags:
                tags.extend(original_tags[:3])
            
            return tags[:8]  # 最多8个标签
            
        except Exception as e:
            print(f"  ⚠️ 标签生成失败，使用原标签: {e}")
            return original_tags[:5] if original_tags else ["AI", "技术"]
    
    def _add_front_matter(
        self,
        title: str,
        description: str,
        tags: List[str],
        content: str
    ) -> str:
        """
        添加Front Matter
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        front_matter = f"""---
title: {title}
date: {current_date}
description: {description}
tags:
"""
        for tag in tags:
            front_matter += f"  - {tag}\n"
        
        front_matter += "---\n\n"
        
        return front_matter + content
    
    def _remove_duplicate_title(self, content: str, title: str) -> str:
        """
        移除内容中重复的标题
        """
        lines = content.split('\n')
        result_lines = []
        
        for line in lines:
            # 检查是否是重复的标题行
            clean_line = line.strip('#').strip()
            if clean_line == title and not result_lines:
                continue
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _post_process_content(self, content: str) -> str:
        """
        后处理内容，清理AI生成的标记和不需要的格式
        
        清理以下内容：
        1. 【文章标题】、【主体内容】、【开篇部分】、【结尾部分】等标记
        2. 多余的空行
        3. 其他AI生成的元标记
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

    
    def _save_article(
        self,
        title: str,
        content: str,
        output_dir: str
    ) -> str:
        """
        保存文章到文件
        """
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        safe_filename = re.sub(r'[^\w\s-]', '', title)
        safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
        safe_filename = safe_filename[:80]  # 限制长度
        
        file_path = Path(output_dir) / f"{safe_filename}.md"
        
        # 如果文件已存在，添加唯一标识符
        if file_path.exists():
            import hashlib
            # 使用标题的哈希值作为唯一标识
            title_hash = hashlib.md5(title.encode()).hexdigest()[:8]
            file_path = Path(output_dir) / f"{safe_filename}-{title_hash}.md"
            
            # 如果还是存在（极端情况），添加时间戳
            if file_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                file_path = Path(output_dir) / f"{safe_filename}-{timestamp}.md"
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)


def main():
    """测试增强版内容生成器"""
    generator = EnhancedContentGenerator()
    
    # 模拟新闻和参考资料
    test_news = {
        'title': 'Kimi K2 Thinking突袭！智能体&推理能力超GPT-5',
        'summary': '"模型即Agent"，再次缩小开源闭源差距',
        'tags': ['Agent', 'Kimi', 'AI'],
        'author': '鱼羊',
        'time': '刚刚'
    }
    
    test_references = {
        'topic': 'Kimi K2 Thinking AI智能体',
        'technical_background': 'Kimi K2 Thinking是月之暗面推出的最新大模型，采用了先进的推理增强技术...',
        'key_innovations': [
            '原生支持智能体能力，无需额外工程',
            '推理性能超越GPT-5水平',
            '开源闭源差距进一步缩小'
        ],
        'application_scenarios': [
            '复杂任务规划和执行',
            '多步骤推理和决策',
            '自主智能体应用开发'
        ],
        'industry_impact': '这标志着国产AI大模型在智能体领域取得重大突破，将推动AI应用向更智能化方向发展...'
    }
    
    # 生成文章
    result = generator.generate_article_from_news(
        news_item=test_news,
        references=test_references,
        style="qbitai",
        output_dir="posts"
    )
    
    print(f"\n✅ 测试完成！")
    print(f"标题: {result['title']}")
    print(f"标签: {', '.join(result['tags'])}")
    print(f"文件: {result['file_path']}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
reference_searcher.py

为热点话题搜索相关辅助材料
使用智谱AI的Web Search功能深度搜索技术背景、应用案例等
"""

import os
import json
import time
from typing import List, Dict, Optional
from datetime import datetime
from zhipuai import ZhipuAI


class ReferenceSearcher:
    """参考资料搜索器 - 为内容生成提供丰富的背景材料"""
    
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
    
    def search_topic_references(
        self, 
        topic: str,
        original_summary: str = "",
        search_depth: str = "deep"
    ) -> Dict[str, any]:
        """
        为特定话题搜索参考资料
        
        Args:
            topic: 话题标题
            original_summary: 原始摘要（可选）
            search_depth: 搜索深度，"quick"(快速) 或 "deep"(深度)
            
        Returns:
            包含多维度参考资料的字典：
            {
                'topic': 话题,
                'technical_background': 技术背景,
                'key_innovations': 关键创新点,
                'application_scenarios': 应用场景,
                'industry_impact': 行业影响,
                'related_technologies': 相关技术,
                'search_results': 原始搜索结果
            }
        """
        print(f"\n{'='*70}")
        print(f"🔍 正在为话题搜索参考资料: {topic}")
        print(f"{'='*70}\n")
        
        references = {
            'topic': topic,
            'original_summary': original_summary,
            'searched_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'technical_background': "",
            'key_innovations': [],
            'application_scenarios': [],
            'industry_impact': "",
            'related_technologies': [],
            'search_results': ""
        }
        
        try:
            # 第一步：搜索技术背景和最新进展
            print("📚 [1/3] 搜索技术背景和最新进展...")
            background = self._search_technical_background(topic, original_summary)
            references['technical_background'] = background['content']
            references['search_results'] = background['raw_results']
            print(f"  ✓ 找到 {len(background['content'])} 字技术背景资料")
            
            # 第二步：搜索应用场景和案例
            if search_depth == "deep":
                time.sleep(1)  # 避免API请求过快
                print("\n💡 [2/3] 搜索应用场景和实际案例...")
                applications = self._search_applications(topic)
                references['application_scenarios'] = applications['scenarios']
                references['key_innovations'] = applications['innovations']
                print(f"  ✓ 找到 {len(applications['scenarios'])} 个应用场景")
                print(f"  ✓ 提取 {len(applications['innovations'])} 个创新点")
                
                # 第三步：搜索行业影响和相关技术
                time.sleep(1)
                print("\n🌐 [3/3] 搜索行业影响和相关技术...")
                context = self._search_industry_context(topic)
                references['industry_impact'] = context['impact']
                references['related_technologies'] = context['related_tech']
                print(f"  ✓ 找到 {len(context['impact'])} 字行业影响分析")
                print(f"  ✓ 提取 {len(context['related_tech'])} 个相关技术")
            else:
                print("  ⚡ 快速模式：跳过深度搜索")
            
            print(f"\n{'='*70}")
            print(f"✅ 参考资料搜索完成")
            print(f"{'='*70}\n")
            
            return references
            
        except Exception as e:
            print(f"\n❌ 搜索失败: {e}")
            return references
    
    def _search_technical_background(
        self, 
        topic: str, 
        summary: str
    ) -> Dict[str, str]:
        """
        搜索技术背景
        
        Returns:
            {'content': 整理后的内容, 'raw_results': 原始搜索结果}
        """
        # 构建搜索查询
        search_query = f"{topic} 技术原理 发展历程 最新进展"
        if summary:
            search_query += f" {summary}"
        
        # 配置搜索工具
        tools = [{
            "type": "web_search",
            "web_search": {
                "enable": True,
                "search_result": True
            }
        }]
        
        messages = [{
            "role": "user",
            "content": f"""请搜索关于"{topic}"的技术背景信息，包括：
1. 技术原理和核心概念
2. 发展历程和演进过程
3. 最新的技术突破和进展
4. 技术优势和特点

请提供详细、准确的技术信息。"""
        }]
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=messages,
                tools=tools,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # 提取结构化内容
            structured = self._extract_structured_content(content, "technical_background")
            
            return {
                'content': structured,
                'raw_results': content
            }
            
        except Exception as e:
            print(f"  ⚠️ 技术背景搜索失败: {e}")
            return {'content': '', 'raw_results': ''}
    
    def _search_applications(self, topic: str) -> Dict[str, List]:
        """
        搜索应用场景和创新点
        
        Returns:
            {'scenarios': 应用场景列表, 'innovations': 创新点列表}
        """
        tools = [{
            "type": "web_search",
            "web_search": {
                "enable": True,
                "search_result": True
            }
        }]
        
        messages = [{
            "role": "user",
            "content": f"""请搜索关于"{topic}"的实际应用信息：
1. 典型应用场景（至少3个）
2. 成功案例或落地项目
3. 关键创新点和突破
4. 技术价值和业务价值

请提供具体的应用案例和创新点。"""
        }]
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=messages,
                tools=tools,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # 提取应用场景和创新点
            scenarios, innovations = self._extract_applications_and_innovations(content)
            
            return {
                'scenarios': scenarios,
                'innovations': innovations
            }
            
        except Exception as e:
            print(f"  ⚠️ 应用场景搜索失败: {e}")
            return {'scenarios': [], 'innovations': []}
    
    def _search_industry_context(self, topic: str) -> Dict[str, any]:
        """
        搜索行业影响和相关技术
        
        Returns:
            {'impact': 行业影响, 'related_tech': 相关技术列表}
        """
        tools = [{
            "type": "web_search",
            "web_search": {
                "enable": True,
                "search_result": True
            }
        }]
        
        messages = [{
            "role": "user",
            "content": f"""请搜索关于"{topic}"的行业影响和技术生态：
1. 对相关行业的影响和改变
2. 未来发展趋势
3. 相关的技术栈和技术体系
4. 竞争格局和市场动态

请提供宏观的行业视角分析。"""
        }]
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=messages,
                tools=tools,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # 提取行业影响和相关技术
            impact, related_tech = self._extract_industry_info(content)
            
            return {
                'impact': impact,
                'related_tech': related_tech
            }
            
        except Exception as e:
            print(f"  ⚠️ 行业分析搜索失败: {e}")
            return {'impact': '', 'related_tech': []}
    
    def _extract_structured_content(self, content: str, content_type: str) -> str:
        """
        使用AI提取和整理结构化内容
        """
        prompt = f"""请从以下搜索结果中提取和整理技术背景信息，要求：
1. 内容准确、客观
2. 重点突出技术原理和核心概念
3. 包含最新进展
4. 300-500字
5. 使用流畅的叙述方式，不要列表形式

搜索结果：
{content}

请直接输出整理后的内容："""
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
        except:
            return content[:500]  # 降级：直接截取
    
    def _extract_applications_and_innovations(self, content: str) -> tuple:
        """
        提取应用场景和创新点
        """
        prompt = f"""请从以下内容中提取：
1. 应用场景（3-5个，每个30-50字）
2. 关键创新点（3-5个，每个20-30字）

输出JSON格式：
{{
    "scenarios": ["场景1", "场景2", ...],
    "innovations": ["创新点1", "创新点2", ...]
}}

内容：
{content}

请直接输出JSON："""
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            data = json.loads(result_text)
            return data.get('scenarios', []), data.get('innovations', [])
        except:
            return [], []
    
    def _extract_industry_info(self, content: str) -> tuple:
        """
        提取行业影响和相关技术
        """
        prompt = f"""请从以下内容中提取：
1. 行业影响（200-300字的分析）
2. 相关技术（3-5个技术名称）

输出JSON格式：
{{
    "impact": "行业影响分析文本",
    "related_technologies": ["技术1", "技术2", ...]
}}

内容：
{content}

请直接输出JSON："""
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            data = json.loads(result_text)
            return data.get('impact', ''), data.get('related_technologies', [])
        except:
            return '', []
    
    def batch_search(
        self, 
        topics: List[Dict[str, str]], 
        delay: float = 2.0
    ) -> List[Dict]:
        """
        批量搜索多个话题的参考资料
        
        Args:
            topics: 话题列表，每个元素包含 {'title': 标题, 'summary': 摘要}
            delay: 请求间隔（秒），避免API限流
            
        Returns:
            参考资料列表
        """
        print(f"\n{'='*70}")
        print(f"🔍 批量搜索 {len(topics)} 个话题的参考资料")
        print(f"{'='*70}\n")
        
        all_references = []
        
        for idx, topic_info in enumerate(topics, 1):
            print(f"\n[{idx}/{len(topics)}] 处理话题: {topic_info.get('title', '')}")
            
            try:
                references = self.search_topic_references(
                    topic=topic_info.get('title', ''),
                    original_summary=topic_info.get('summary', ''),
                    search_depth="quick" if len(topics) > 5 else "deep"  # 多话题时使用快速模式
                )
                all_references.append(references)
                
                # 延迟，避免请求过快
                if idx < len(topics):
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"  ❌ 处理失败: {e}")
                continue
        
        print(f"\n{'='*70}")
        print(f"✅ 批量搜索完成，成功处理 {len(all_references)}/{len(topics)} 个话题")
        print(f"{'='*70}\n")
        
        return all_references


def main():
    """测试参考资料搜索功能"""
    searcher = ReferenceSearcher()
    
    # 测试单个话题搜索
    test_topic = "Kimi K2 Thinking AI智能体"
    test_summary = "模型即Agent，超GPT-5的推理能力"
    
    references = searcher.search_topic_references(
        topic=test_topic,
        original_summary=test_summary,
        search_depth="deep"
    )
    
    # 打印结果
    print("\n" + "="*70)
    print("📋 搜索结果汇总")
    print("="*70 + "\n")
    
    print(f"话题: {references['topic']}")
    print(f"\n技术背景:\n{references['technical_background'][:300]}...")
    print(f"\n关键创新点: {', '.join(references['key_innovations'][:3])}")
    print(f"\n应用场景: {', '.join(references['application_scenarios'][:3])}")
    
    # 保存为JSON
    output_file = "data/reference_example.json"
    os.makedirs("data", exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(references, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 参考资料已保存到: {output_file}")


if __name__ == "__main__":
    main()

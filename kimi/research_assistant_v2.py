#!/usr/bin/env python3
"""
增强版信息挖掘助手
支持配置文件、交互模式、批量研究等功能
"""

import os
import sys
import json
import yaml
import httpx
import openai
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class FormulaChatClient:
    def __init__(self, base_url: str, api_key: str):
        """初始化 Formula 客户端"""
        self.base_url = base_url
        self.api_key = api_key
        self.openai = openai.Client(
            base_url=base_url,
            api_key=api_key,
        )
        self.httpx = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )
        self.model = "kimi-k2-thinking"

    def get_tools(self, formula_uri: str):
        """从 Formula API 获取工具定义"""
        response = self.httpx.get(f"/formulas/{formula_uri}/tools")
        response.raise_for_status()
        
        try:
            return response.json().get("tools", [])
        except json.JSONDecodeError as e:
            print(f"错误: 无法解析响应为 JSON (状态码: {response.status_code})")
            print(f"响应内容: {response.text[:500]}")
            raise

    def call_tool(self, formula_uri: str, function: str, args: dict):
        """调用官方工具"""
        response = self.httpx.post(
            f"/formulas/{formula_uri}/fibers",
            json={"name": function, "arguments": json.dumps(args)},
        )
        response.raise_for_status()
        fiber = response.json()
        
        if fiber.get("status", "") == "succeeded":
            return fiber["context"].get("output") or fiber["context"].get("encrypted_output")
        
        if "error" in fiber:
            return f"Error: {fiber['error']}"
        if "error" in fiber.get("context", {}):
            return f"Error: {fiber['context']['error']}"
        return "Error: Unknown error"

    def close(self):
        """关闭客户端连接"""
        self.httpx.close()


class EnhancedResearchAssistant:
    """增强版信息挖掘研究助手"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化研究助手"""
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化客户端
        base_url = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")
        api_key = os.getenv("MOONSHOT_API_KEY")
        
        if not api_key:
            raise ValueError("MOONSHOT_API_KEY 环境变量未设置，请先设置 API 密钥")
        
        self.client = FormulaChatClient(base_url, api_key)
        self.client.model = self.config['generation']['model']
        
        # 加载工具
        self.formula_uris = self.config['tools']['enabled']
        self.all_tools = []
        self.tool_to_uri = {}
        self._load_tools()
        
        # 加载提示词模板
        self.expert_prompt = self._load_expert_prompt()
        
        # 搜索结果存储
        self.search_results = []
        self.search_history = []
        
    def _load_config(self, config_path: Optional[str] = None):
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        else:
            config_path = Path(config_path)
        
        if not config_path.exists():
            print(f"⚠️  配置文件不存在: {config_path}，使用默认配置")
            return self._default_config()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"✓ 已加载配置: {config_path}")
                return config
        except Exception as e:
            print(f"⚠️  加载配置文件失败: {e}，使用默认配置")
            return self._default_config()
    
    def _default_config(self):
        """默认配置"""
        return {
            'research': {
                'max_iterations': 15,
            },
            'generation': {
                'model': 'kimi-k2-thinking',
                'search_temperature': 0.7,
                'expert_temperature': 0.8,
                'max_tokens': 32768,
            },
            'output': {
                'directory': '../posts',
                'timestamp_format': '%Y%m%d_%H%M%S',
                'show_full_content': False,
                'preview_length': 500,
            },
            'tools': {
                'enabled': [
                    'moonshot/date:latest',
                    'moonshot/web-search:latest'
                ]
            },
            'logging': {
                'show_reasoning': True,
                'reasoning_length': 200,
                'save_search_history': True,
                'search_history_file': '../data/generated/search_history.json',
            }
        }
    
    def _load_tools(self):
        """加载所有工具定义"""
        print("\n🔧 正在加载官方工具...")
        
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
                continue
        
        print(f"   共加载 {len(self.all_tools)} 个工具\n")
        
        if not self.all_tools:
            raise ValueError("未能加载任何工具，请检查 API 密钥和网络连接")
    
    def _load_expert_prompt(self):
        """加载专家讲解提示词"""
        prompt_path = Path(__file__).parent / "prompts" / "expert_narrator.txt"
        
        if not prompt_path.exists():
            print(f"⚠️  提示词文件不存在: {prompt_path}")
            return self._default_expert_prompt()
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _default_expert_prompt(self):
        """默认专家提示词"""
        return """你是一位资深的技术专家，擅长用通俗易懂的方式讲解复杂的技术概念。

请基于以下搜索到的信息：
{search_results}

深入浅出地讲解主题：{topic}

要求：
1. 结构清晰，逻辑流畅
2. 适当使用比喻和案例
3. 突出重点和关键信息
4. 使用 Markdown 格式
5. 提供独特见解
"""
    
    def research(self, topic: str, verbose: bool = True):
        """
        研究指定主题
        
        Args:
            topic: 研究主题
            verbose: 是否显示详细过程
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"🔍 开始研究主题: {topic}")
            print(f"{'='*70}\n")
        
        # 重置搜索结果
        self.search_results = []
        
        # 第一阶段：信息收集
        if verbose:
            print("【阶段 1/2】📚 信息收集与学习")
            print("-" * 70)
        
        search_phase_messages = [
            {
                "role": "system",
                "content": """你是一位资深的信息研究员，擅长通过联网搜索收集和整理信息。

你的任务：
1. 使用搜索工具深入研究用户指定的主题
2. 从多个角度收集相关信息：
   - 基本概念和定义
   - 技术原理和实现细节
   - 发展历程和重要里程碑
   - 实际应用案例（最好是知名产品）
   - 行业影响和市场动态
   - 技术对比和优劣分析
   - 挑战、局限性和未来趋势
3. 确保信息的全面性、准确性和时效性
4. 将搜索到的关键信息进行结构化整理

搜索技巧：
- 使用不同的关键词组合，覆盖不同角度
- 优先搜索权威来源和最新信息
- 注意收集具体的数据、案例和引用
- 避免重复搜索相似的内容

当你认为已经收集到足够全面的信息（通常需要 5-10 次搜索），请总结所有搜索结果，并明确说明"信息收集完成"。"""
            },
            {
                "role": "user",
                "content": f"""请深入研究以下主题，收集全面的信息：

主题：{topic}

请通过多次搜索，从不同角度收集信息。建议的搜索方向：
1. {topic} 是什么？基本概念和定义
2. {topic} 的技术原理和工作机制
3. {topic} 的发展历程和重要版本/里程碑
4. {topic} 的实际应用案例和成功案例
5. {topic} 与其他技术的对比
6. {topic} 的挑战和局限性
7. {topic} 的未来发展趋势

请确保信息的完整性和准确性。"""
            }
        ]
        
        # 信息收集循环
        max_iterations = self.config['research']['max_iterations']
        
        for iteration in range(max_iterations):
            if verbose:
                print(f"\n{'─'*70}")
                print(f">>> 第 {iteration + 1}/{max_iterations} 轮")
            
            try:
                completion = self.client.openai.chat.completions.create(
                    model=self.client.model,
                    messages=search_phase_messages,
                    max_tokens=self.config['generation']['max_tokens'],
                    tools=self.all_tools,
                    temperature=self.config['generation']['search_temperature'],
                )
            except Exception as e:
                print(f"✗ 调用模型时发生错误: {e}")
                break
            
            message = completion.choices[0].message
            
            # 打印思考过程
            if verbose and self.config['logging']['show_reasoning']:
                if hasattr(message, "reasoning_content"):
                    reasoning = getattr(message, "reasoning_content")
                    if reasoning:
                        max_len = self.config['logging']['reasoning_length']
                        display_reasoning = reasoning[:max_len] + "..." if len(reasoning) > max_len else reasoning
                        print(f"💭 {display_reasoning}")
            
            # 添加消息到上下文
            search_phase_messages.append(message)
            
            # 如果没有工具调用，检查是否完成
            if not message.tool_calls:
                if verbose:
                    print(f"\n📝 AI 回复:\n{message.content}")
                
                # 检查是否明确表示完成
                if message.content and any(keyword in message.content for keyword in 
                    ["信息收集完成", "收集完毕", "已经收集到足够", "搜集完成", "研究完成"]):
                    if verbose:
                        print("\n✓ 信息收集阶段完成")
                    break
                elif iteration >= max_iterations - 1:
                    if verbose:
                        print("\n✓ 达到最大迭代次数，进入下一阶段")
                    break
                else:
                    continue
            
            # 处理工具调用
            if verbose:
                print(f"🔧 调用 {len(message.tool_calls)} 个工具:")
            
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if verbose:
                    # 美化参数显示
                    args_str = ", ".join(f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" 
                                        for k, v in list(args.items())[:3])
                    if len(args) > 3:
                        args_str += ", ..."
                    print(f"   🔍 {func_name}({args_str})")
                
                # 获取 formula_uri
                formula_uri = self.tool_to_uri.get(func_name)
                if not formula_uri:
                    print(f"     ✗ 找不到工具对应的 URI")
                    continue
                
                # 调用工具
                try:
                    result = self.client.call_tool(formula_uri, func_name, args)
                    
                    # 保存搜索结果
                    if func_name == "web_search":
                        self.search_results.append({
                            "query": args.get("query", ""),
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        })
                        if verbose:
                            result_preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
                            print(f"     ✓ 搜索完成: {result_preview}")
                    
                    # 添加工具结果到消息列表
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": result
                    }
                    search_phase_messages.append(tool_message)
                    
                except Exception as e:
                    print(f"     ✗ 工具调用失败: {e}")
                    continue
        
        # 保存搜索历史
        if self.config['logging']['save_search_history']:
            self._save_search_history(topic)
        
        # 第二阶段：生成专家讲解
        if verbose:
            print(f"\n{'='*70}")
            print("【阶段 2/2】✍️  生成专家级讲解")
            print("-" * 70)
        
        # 整理搜索结果
        formatted_results = self._format_search_results()
        
        if verbose:
            print(f"\n📊 已收集 {len(self.search_results)} 条搜索结果")
            print(f"📝 总字符数: {len(formatted_results):,}\n")
        
        # 使用专家提示词
        expert_prompt = self.expert_prompt.format(
            topic=topic,
            search_results=formatted_results
        )
        
        expert_messages = [
            {
                "role": "user",
                "content": expert_prompt
            }
        ]
        
        if verbose:
            print("🎯 正在生成专家讲解...\n")
        
        try:
            completion = self.client.openai.chat.completions.create(
                model=self.client.model,
                messages=expert_messages,
                max_tokens=self.config['generation']['max_tokens'],
                temperature=self.config['generation']['expert_temperature'],
            )
        except Exception as e:
            print(f"✗ 生成讲解时发生错误: {e}")
            return None
        
        final_content = completion.choices[0].message.content
        
        if verbose:
            print("✓ 讲解生成完成")
        
        # 保存到文件
        output_file = self._save_to_file(topic, final_content)
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"✅ 研究完成！")
            print(f"📁 输出文件: {output_file}")
            print(f"{'='*70}\n")
            
            # 显示内容预览
            if self.config['output']['show_full_content']:
                print("\n" + "="*70)
                print("📄 生成的内容:")
                print("="*70)
                print(final_content)
            else:
                preview_len = self.config['output']['preview_length']
                print(f"\n📄 内容预览 (前 {preview_len} 字符):")
                print("-" * 70)
                print(final_content[:preview_len] + "..." if len(final_content) > preview_len else final_content)
        
        return final_content
    
    def _format_search_results(self):
        """格式化搜索结果"""
        if not self.search_results:
            return "（未搜索到相关信息）"
        
        formatted = []
        for i, item in enumerate(self.search_results, 1):
            formatted.append(f"""### 搜索 {i}：{item['query']}

{item['result']}

---
""")
        
        return "\n".join(formatted)
    
    def _save_to_file(self, topic: str, content: str):
        """保存到文件"""
        # 创建输出目录
        output_dir = Path(__file__).parent / self.config['output']['directory']
        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名（替换特殊字符）
        safe_filename = "".join(c if c.isalnum() or c in (' ', '-', '_', '中', '文') else '_' for c in topic)
        safe_filename = safe_filename.strip('_')[:100]  # 限制长度
        
        timestamp = datetime.now().strftime(self.config['output']['timestamp_format'])
        filename = f"{safe_filename}_{timestamp}.md"
        
        output_path = output_dir / filename
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {topic}\n\n")
            f.write(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write(f"*基于 {len(self.search_results)} 次网络搜索生成*\n\n")
            f.write("---\n\n")
            f.write(content)
        
        return output_path
    
    def _save_search_history(self, topic: str):
        """保存搜索历史"""
        try:
            history_file = Path(__file__).parent / self.config['logging']['search_history_file']
            history_file = history_file.resolve()
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取现有历史
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
            
            # 添加新记录
            history.append({
                "topic": topic,
                "timestamp": datetime.now().isoformat(),
                "search_count": len(self.search_results),
                "searches": self.search_results
            })
            
            # 保存
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"⚠️  保存搜索历史失败: {e}")
    
    def batch_research(self, topics: List[str]):
        """批量研究多个主题"""
        print(f"\n{'='*70}")
        print(f"📚 批量研究模式")
        print(f"   共 {len(topics)} 个主题")
        print(f"{'='*70}\n")
        
        results = []
        
        for i, topic in enumerate(topics, 1):
            print(f"\n[{i}/{len(topics)}] 研究主题: {topic}")
            print("-" * 70)
            
            try:
                result = self.research(topic, verbose=True)
                results.append({
                    "topic": topic,
                    "success": True,
                    "content": result
                })
            except Exception as e:
                print(f"✗ 研究失败: {e}")
                results.append({
                    "topic": topic,
                    "success": False,
                    "error": str(e)
                })
            
            # 避免请求过快
            if i < len(topics):
                import time
                print("\n⏳ 等待 3 秒后继续...")
                time.sleep(3)
        
        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        print(f"\n{'='*70}")
        print(f"✅ 批量研究完成")
        print(f"   成功: {success_count}/{len(topics)}")
        print(f"{'='*70}\n")
        
        return results
    
    def close(self):
        """关闭客户端"""
        self.client.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AI 信息挖掘助手 - 基于 Kimi 模型的智能研究工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互模式
  python research_assistant_v2.py
  
  # 直接指定主题
  python research_assistant_v2.py -t "大语言模型的发展历程"
  
  # 批量研究
  python research_assistant_v2.py -b topics.txt
  
  # 使用自定义配置
  python research_assistant_v2.py -c my_config.yaml -t "AI Agent"
        """
    )
    
    parser.add_argument('-t', '--topic', type=str, help='研究主题')
    parser.add_argument('-b', '--batch', type=str, help='批量研究，指定包含主题列表的文件路径（每行一个主题）')
    parser.add_argument('-c', '--config', type=str, help='配置文件路径')
    parser.add_argument('-q', '--quiet', action='store_true', help='静默模式，只显示关键信息')
    
    args = parser.parse_args()
    
    # 打印欢迎信息
    if not args.quiet:
        print("\n" + "="*70)
        print("🔍 AI 信息挖掘助手 v2.0")
        print("   基于 Kimi 模型的智能研究工具")
        print("="*70 + "\n")
    
    try:
        # 创建助手实例
        assistant = EnhancedResearchAssistant(config_path=args.config)
        
        # 批量模式
        if args.batch:
            batch_file = Path(args.batch)
            if not batch_file.exists():
                print(f"❌ 文件不存在: {batch_file}")
                return
            
            with open(batch_file, 'r', encoding='utf-8') as f:
                topics = [line.strip() for line in f if line.strip()]
            
            if not topics:
                print("❌ 文件中没有找到任何主题")
                return
            
            assistant.batch_research(topics)
        
        # 单个主题
        elif args.topic:
            assistant.research(args.topic, verbose=not args.quiet)
        
        # 交互模式
        else:
            while True:
                topic = input("\n请输入您想研究的主题 (输入 'q' 退出): ").strip()
                
                if topic.lower() in ['q', 'quit', 'exit', '退出']:
                    break
                
                if not topic:
                    print("❌ 主题不能为空")
                    continue
                
                assistant.research(topic, verbose=not args.quiet)
                
                # 询问是否继续
                cont = input("\n是否继续研究其他主题？(y/n): ").strip().lower()
                if cont not in ['y', 'yes', '是', 'Y']:
                    break
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
    finally:
        if 'assistant' in locals():
            assistant.close()
        if not args.quiet:
            print("\n👋 感谢使用！\n")


if __name__ == "__main__":
    main()

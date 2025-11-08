#!/usr/bin/env python3
"""
信息挖掘助手
基于 Kimi 模型的智能研究助手，自动搜索、学习和生成专业讲解
"""

import os
import json
import httpx
import openai
from datetime import datetime
from pathlib import Path


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


class ResearchAssistant:
    """信息挖掘研究助手"""
    
    def __init__(self):
        """初始化研究助手"""
        # 初始化客户端
        base_url = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")
        api_key = os.getenv("MOONSHOT_API_KEY")
        
        if not api_key:
            raise ValueError("MOONSHOT_API_KEY 环境变量未设置，请先设置 API 密钥")
        
        self.client = FormulaChatClient(base_url, api_key)
        
        # 定义要使用的官方工具
        self.formula_uris = [
            "moonshot/date:latest",
            "moonshot/web-search:latest"
        ]
        
        # 加载工具
        self.all_tools = []
        self.tool_to_uri = {}
        self._load_tools()
        
        # 加载提示词模板
        self.expert_prompt = self._load_expert_prompt()
        
        # 搜索结果存储
        self.search_results = []
        
    def _load_tools(self):
        """加载所有工具定义"""
        print("正在加载官方工具...")
        
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
                            print(f"  ✓ 已加载工具: {func_name}")
            except Exception as e:
                print(f"  ✗ 警告: 加载工具 {uri} 失败: {e}")
                continue
        
        print(f"总共加载 {len(self.all_tools)} 个工具\n")
        
        if not self.all_tools:
            raise ValueError("未能加载任何工具，请检查 API 密钥和网络连接")
    
    def _load_expert_prompt(self):
        """加载专家讲解提示词"""
        prompt_path = Path(__file__).parent / "prompts" / "expert_narrator.txt"
        
        if not prompt_path.exists():
            print(f"警告: 提示词文件不存在: {prompt_path}")
            return ""
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def research(self, topic: str, max_iterations: int = 15):
        """
        研究指定主题
        
        Args:
            topic: 研究主题
            max_iterations: 最大迭代次数
        """
        print(f"\n{'='*60}")
        print(f"开始研究主题: {topic}")
        print(f"{'='*60}\n")
        
        # 重置搜索结果
        self.search_results = []
        
        # 第一阶段：信息收集
        print("【阶段 1/2】信息收集与学习")
        print("-" * 60)
        
        search_phase_messages = [
            {
                "role": "system",
                "content": """你是一位资深的信息研究员，擅长通过联网搜索收集和整理信息。

你的任务：
1. 使用搜索工具深入研究用户指定的主题
2. 从多个角度收集相关信息：技术原理、发展历程、应用案例、行业影响等
3. 确保信息的全面性和准确性
4. 将搜索到的关键信息进行结构化整理

搜索策略：
- 先搜索主题的基本概念和定义
- 然后搜索技术细节、原理解析
- 再搜索实际应用案例和行业动态
- 最后搜索未来趋势和专家观点

当你认为已经收集到足够全面的信息后，请总结所有搜索结果，并说明"信息收集完成"。"""
            },
            {
                "role": "user",
                "content": f"请深入研究以下主题，收集全面的信息：\n\n主题：{topic}\n\n请通过多次搜索，从不同角度收集信息，确保内容的完整性和准确性。"
            }
        ]
        
        # 信息收集循环
        for iteration in range(max_iterations):
            print(f"\n>>> 第 {iteration + 1} 轮信息收集")
            
            try:
                completion = self.client.openai.chat.completions.create(
                    model=self.client.model,
                    messages=search_phase_messages,
                    max_tokens=1024 * 32,
                    tools=self.all_tools,
                    temperature=0.7,
                )
            except Exception as e:
                print(f"✗ 调用模型时发生错误: {e}")
                break
            
            message = completion.choices[0].message
            
            # 打印思考过程（简化版）
            if hasattr(message, "reasoning_content"):
                reasoning = getattr(message, "reasoning_content")
                if reasoning:
                    # 只显示思考的前200字符
                    print(f"💭 思考: {reasoning[:200]}..." if len(reasoning) > 200 else f"💭 思考: {reasoning}")
            
            # 添加消息到上下文
            search_phase_messages.append(message)
            
            # 如果没有工具调用，检查是否完成
            if not message.tool_calls:
                print(f"\n📝 阶段总结:\n{message.content}")
                
                # 检查是否明确表示完成
                if message.content and ("信息收集完成" in message.content or "收集完毕" in message.content or "已经收集到足够" in message.content):
                    print("\n✓ 信息收集阶段完成")
                    break
                elif iteration >= max_iterations - 1:
                    print("\n✓ 达到最大迭代次数，进入下一阶段")
                    break
                else:
                    # 继续收集
                    continue
            
            # 处理工具调用
            print(f"🔧 调用 {len(message.tool_calls)} 个工具")
            
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                print(f"   - {func_name}({', '.join(f'{k}={v}' for k, v in args.items())})")
                
                # 获取 formula_uri
                formula_uri = self.tool_to_uri.get(func_name)
                if not formula_uri:
                    print(f"     ✗ 找不到工具对应的 URI")
                    continue
                
                # 调用工具
                result = self.client.call_tool(formula_uri, func_name, args)
                
                # 保存搜索结果
                if func_name == "web_search":
                    self.search_results.append({
                        "query": args.get("query", ""),
                        "result": result
                    })
                    print(f"     ✓ 搜索完成，结果已保存")
                
                # 添加工具结果到消息列表
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": result
                }
                search_phase_messages.append(tool_message)
        
        # 第二阶段：生成专家讲解
        print(f"\n{'='*60}")
        print("【阶段 2/2】生成专家级讲解")
        print("-" * 60)
        
        # 整理搜索结果
        formatted_results = self._format_search_results()
        
        # 使用专家提示词
        expert_prompt = self.expert_prompt.format(
            topic=topic,
            search_results=formatted_results
        )
        
        expert_messages = [
            {
                "role": "system",
                "content": expert_prompt
            }
        ]
        
        print("\n🎯 开始生成专家讲解...")
        
        try:
            completion = self.client.openai.chat.completions.create(
                model=self.client.model,
                messages=expert_messages,
                max_tokens=1024 * 32,
                temperature=0.8,
            )
        except Exception as e:
            print(f"✗ 生成讲解时发生错误: {e}")
            return None
        
        final_content = completion.choices[0].message.content
        
        print("\n✓ 讲解生成完成")
        
        # 保存到文件
        output_file = self._save_to_file(topic, final_content)
        
        print(f"\n{'='*60}")
        print(f"研究完成！")
        print(f"输出文件: {output_file}")
        print(f"{'='*60}\n")
        
        return final_content
    
    def _format_search_results(self):
        """格式化搜索结果"""
        if not self.search_results:
            return "（未搜索到相关信息）"
        
        formatted = []
        for i, item in enumerate(self.search_results, 1):
            formatted.append(f"### 搜索 {i}：{item['query']}\n\n{item['result']}\n")
        
        return "\n".join(formatted)
    
    def _save_to_file(self, topic: str, content: str):
        """保存到文件"""
        # 创建输出目录
        output_dir = Path(__file__).parent.parent / "posts"
        output_dir.mkdir(exist_ok=True)
        
        # 生成文件名（替换特殊字符）
        safe_filename = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in topic)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_filename}_{timestamp}.md"
        
        output_path = output_dir / filename
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {topic}\n\n")
            f.write(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write("---\n\n")
            f.write(content)
        
        return output_path
    
    def close(self):
        """关闭客户端"""
        self.client.close()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🔍 AI 信息挖掘助手")
    print("基于 Kimi 模型的智能研究工具")
    print("="*60 + "\n")
    
    # 获取用户输入
    topic = input("请输入您想研究的主题: ").strip()
    
    if not topic:
        print("❌ 主题不能为空")
        return
    
    # 创建助手实例
    assistant = ResearchAssistant()
    
    try:
        # 开始研究
        result = assistant.research(topic)
        
        if result:
            print("\n" + "="*60)
            print("📄 生成的内容预览:")
            print("="*60)
            print(result[:500] + "..." if len(result) > 500 else result)
            print("\n" + "="*60)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        assistant.close()
        print("\n👋 感谢使用！")


if __name__ == "__main__":
    main()

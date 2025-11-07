#!/usr/bin/env python3
"""
测试标题生成功能
验证25字限制和格式要求
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate.enhanced_content_generator import EnhancedContentGenerator

def test_title_generation():
    """测试标题生成"""
    
    # 检查 API Key
    api_key = os.environ.get('ZHIPUAI_API_KEY')
    if not api_key:
        print("❌ 错误：未设置 ZHIPUAI_API_KEY 环境变量")
        print("请运行：export ZHIPUAI_API_KEY='your-api-key'")
        return
    
    # 初始化生成器
    generator = EnhancedContentGenerator(api_key)
    
    # 测试用例
    test_cases = [
        {
            "original_title": "Kimi K2 Thinking突袭！智能体&推理能力超GPT-5",
            "topic": "AI大模型发布",
            "tags": ["Kimi", "AI", "大模型"]
        },
        {
            "original_title": "马斯克1万亿美元薪酬方案获批！史上最贵CEO诞生",
            "topic": "科技人物",
            "tags": ["马斯克", "薪酬", "特斯拉"]
        },
        {
            "original_title": "谷歌发布Magika 1.0：Rust语言驱动的AI文件识别工具",
            "topic": "开源工具",
            "tags": ["谷歌", "Rust", "AI工具"]
        }
    ]
    
    print("=" * 60)
    print("标题生成测试")
    print("=" * 60)
    print()
    
    for i, case in enumerate(test_cases, 1):
        print(f"测试用例 {i}:")
        print(f"原标题：{case['original_title']}")
        print(f"原标题长度：{len(case['original_title'])} 字符")
        print()
        
        # 生成新标题
        new_title = generator._generate_innovative_title(
            case['original_title'],
            case['topic'],
            case['tags']
        )
        
        # 计算汉字数量
        chinese_chars = len([c for c in new_title if '\u4e00' <= c <= '\u9fff'])
        
        # 检查格式
        has_quotes = any(q in new_title for q in ['"', "'", '"', '"', ''', ''', '「', '」'])
        has_spaces = ' ' in new_title
        
        print(f"新标题：{new_title}")
        print(f"汉字数量：{chinese_chars}")
        print(f"总长度：{len(new_title)} 字符")
        print(f"✓ 长度检查：{'通过' if chinese_chars <= 25 else '❌ 超长'}")
        print(f"✓ 引号检查：{'通过' if not has_quotes else '❌ 包含引号'}")
        print(f"✓ 空格检查：{'通过' if not has_spaces else '❌ 包含空格'}")
        print()
        print("-" * 60)
        print()

if __name__ == '__main__':
    test_title_generation()

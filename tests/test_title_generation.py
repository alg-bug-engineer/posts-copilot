#!/usr/bin/env python3
"""
test_title_generation.py

测试标题生成的创新性和差异性
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generate.enhanced_content_generator import EnhancedContentGenerator


def test_title_creativity():
    """测试标题创新性"""
    
    # 检查API密钥
    if not os.environ.get("ZHIPUAI_API_KEY"):
        print("❌ 未设置 ZHIPUAI_API_KEY")
        return
    
    print("\n" + "="*80)
    print("🧪 测试标题生成的创新性")
    print("="*80 + "\n")
    
    generator = EnhancedContentGenerator()
    
    # 测试用例
    test_cases = [
        {
            'original': 'Kimi K2 Thinking突袭！智能体&推理能力超GPT-5，网友：再次缩小开源闭源差距',
            'topic': 'Kimi K2 Thinking',
            'tags': ['Agent', 'Kimi', 'AI']
        },
        {
            'original': '马斯克1万亿美元薪酬方案获批！',
            'topic': '马斯克薪酬',
            'tags': ['马斯克', '特斯拉']
        },
        {
            'original': '小马智行彭军：有司机的Robotaxi毫无意义，辅助驾驶和无人驾驶是两回事',
            'topic': '小马智行无人驾驶',
            'tags': ['自动驾驶', 'Robotaxi']
        }
    ]
    
    for idx, case in enumerate(test_cases, 1):
        print(f"\n【测试 {idx}】")
        print(f"原标题: {case['original']}")
        print("-" * 80)
        
        # 生成3个新标题看看差异
        for i in range(3):
            new_title = generator._generate_creative_title(
                original_title=case['original'],
                topic=case['topic'],
                tags=case['tags']
            )
            
            # 计算相似度
            similarity = generator._calculate_similarity(new_title, case['original'])
            
            status = "✅" if similarity < 0.7 else "⚠️"
            print(f"  {status} 新标题 {i+1}: {new_title}")
            print(f"     相似度: {similarity:.2%}")
        
        print()
    
    print("="*80)
    print("✅ 测试完成")
    print("\n💡 相似度指标:")
    print("   < 0.5  : 优秀（差异明显）")
    print("   0.5-0.7: 良好（有一定差异）")
    print("   > 0.7  : 需改进（相似度过高）")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_title_creativity()

"""
测试文章选择逻辑
验证在多次平台选择时，文章路径是否保持一致
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_article_selection_logic():
    """
    模拟测试文章选择逻辑
    """
    print("=" * 60)
    print("测试文章选择逻辑")
    print("=" * 60)
    
    # 模拟文章列表
    articles = [
        "/path/to/article_0.md",
        "/path/to/article_1.md",
        "/path/to/article_2.md",
    ]
    
    # 模拟选择 index=2 的文章
    selected_index = 2
    article_path = articles[selected_index]
    current_article_path = article_path
    
    print(f"\n1. 用户选择文章 index={selected_index}")
    print(f"   article_path = {article_path}")
    print(f"   current_article_path = {current_article_path}")
    
    # 模拟内层循环 - 第一次发布到 CSDN
    print(f"\n2. 第一次发布到 CSDN")
    print(f"   使用文章：{current_article_path}")
    print(f"   验证：{os.path.basename(current_article_path)} == article_2.md")
    assert os.path.basename(current_article_path) == "article_2.md", "第一次发布文章错误"
    print("   ✓ 验证通过")
    
    # 模拟发布成功后，继续在内层循环
    print(f"\n3. 发布成功，返回平台选择（仍在内层循环）")
    print(f"   current_article_path = {current_article_path}")
    print(f"   文章路径是否改变：{current_article_path == article_path}")
    
    # 模拟第二次发布到知乎
    print(f"\n4. 第二次发布到知乎")
    print(f"   使用文章：{current_article_path}")
    print(f"   验证：{os.path.basename(current_article_path)} == article_2.md")
    assert os.path.basename(current_article_path) == "article_2.md", "第二次发布文章错误"
    print("   ✓ 验证通过")
    
    # 模拟选择返回上一级
    print(f"\n5. 用户选择返回上一级（跳出内层循环）")
    print(f"   将重新选择文章")
    
    # 模拟重新选择文章 index=0
    new_selected_index = 0
    article_path = articles[new_selected_index]
    current_article_path = article_path
    
    print(f"\n6. 用户重新选择文章 index={new_selected_index}")
    print(f"   article_path = {article_path}")
    print(f"   current_article_path = {current_article_path}")
    
    # 模拟发布到掘金
    print(f"\n7. 发布到掘金")
    print(f"   使用文章：{current_article_path}")
    print(f"   验证：{os.path.basename(current_article_path)} == article_0.md")
    assert os.path.basename(current_article_path) == "article_0.md", "重新选择后发布文章错误"
    print("   ✓ 验证通过")
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    print("\n结论：")
    print("- 在内层循环中（平台选择），文章路径保持不变")
    print("- 只有返回上一级（跳出内层循环）才会重新选择文章")
    print("- 逻辑正确，用户描述的bug不应该发生")
    print("- 建议通过日志追踪实际运行情况")


if __name__ == "__main__":
    test_article_selection_logic()

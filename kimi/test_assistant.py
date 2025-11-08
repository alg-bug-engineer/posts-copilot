#!/usr/bin/env python3
"""
快速测试脚本 - 验证信息挖掘助手功能
"""

import os
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from research_assistant_v2 import EnhancedResearchAssistant


def test_basic_functionality():
    """测试基本功能"""
    print("\n" + "="*70)
    print("🧪 测试信息挖掘助手")
    print("="*70 + "\n")
    
    # 检查 API 密钥
    if not os.getenv("MOONSHOT_API_KEY"):
        print("❌ 错误: MOONSHOT_API_KEY 环境变量未设置")
        print("\n请运行以下命令设置 API 密钥：")
        print("export MOONSHOT_API_KEY='your-api-key-here'")
        return False
    
    print("✓ API 密钥已设置\n")
    
    try:
        # 创建助手实例
        print("1. 创建助手实例...")
        assistant = EnhancedResearchAssistant()
        print("   ✓ 助手创建成功\n")
        
        # 测试简单主题
        test_topic = "什么是大语言模型"
        print(f"2. 测试研究功能 (主题: {test_topic})...")
        print("   这可能需要几分钟时间...\n")
        
        result = assistant.research(test_topic, verbose=True)
        
        if result:
            print("\n   ✓ 研究完成")
            print(f"   内容长度: {len(result)} 字符")
        else:
            print("\n   ✗ 研究失败")
            return False
        
        # 清理
        assistant.close()
        print("\n3. ✓ 所有测试通过\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tools_loading():
    """测试工具加载"""
    print("\n" + "="*70)
    print("🧪 测试工具加载")
    print("="*70 + "\n")
    
    try:
        assistant = EnhancedResearchAssistant()
        
        print(f"✓ 成功加载 {len(assistant.all_tools)} 个工具:")
        for tool in assistant.all_tools:
            func_name = tool.get('function', {}).get('name', 'Unknown')
            print(f"   - {func_name}")
        
        assistant.close()
        print("\n✓ 工具加载测试通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 工具加载失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n" + "="*70)
    print("🔍 AI 信息挖掘助手 - 测试套件")
    print("="*70)
    
    print("\n选择测试模式:")
    print("1) 快速测试（仅测试工具加载）")
    print("2) 完整测试（包含实际研究）")
    print("3) 两者都运行")
    
    choice = input("\n请输入选项 (1-3，默认 1): ").strip() or "1"
    
    if choice == "1":
        test_tools_loading()
    elif choice == "2":
        test_basic_functionality()
    elif choice == "3":
        if test_tools_loading():
            print("\n" + "="*70 + "\n")
            test_basic_functionality()
    else:
        print("❌ 无效选项")
        return
    
    print("\n" + "="*70)
    print("✅ 测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

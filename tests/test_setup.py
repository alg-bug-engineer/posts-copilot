"""
测试脚本 - 验证重构后的功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("博客自动发布工具 - 功能测试")
print("=" * 60)
print()

# 测试1: 导入核心模块
print("1. 测试核心模块导入...")
try:
    from src.core import setup_logger, get_logger, SessionManager
    print("   ✓ 核心模块导入成功")
except Exception as e:
    print(f"   ✗ 核心模块导入失败: {e}")
    sys.exit(1)

# 测试2: 日志系统
print("\n2. 测试日志系统...")
try:
    logger = setup_logger('test_logger')
    logger.info("这是一条测试日志")
    logger.debug("这是调试信息")
    logger.warning("这是警告信息")
    print("   ✓ 日志系统工作正常")
except Exception as e:
    print(f"   ✗ 日志系统测试失败: {e}")

# 测试3: 配置读取
print("\n3. 测试配置读取...")
try:
    from src.utils.yaml_file_utils import read_common, read_csdn
    common_config = read_common()
    csdn_config = read_csdn()
    print(f"   ✓ 通用配置读取成功")
    print(f"   ✓ CSDN配置读取成功")
except Exception as e:
    print(f"   ✗ 配置读取失败: {e}")

# 测试4: 工具函数
print("\n4. 测试工具函数...")
try:
    from src.utils.file_utils import list_files, parse_front_matter
    print("   ✓ 文件工具导入成功")
except Exception as e:
    print(f"   ✗ 工具函数导入失败: {e}")

# 测试5: 发布器模块
print("\n5. 测试发布器模块...")
try:
    from src.publisher.base_publisher import BasePublisher
    from src.publisher.common_handler import wait_login, safe_click, safe_input
    from src.publisher.csdn_publisher import CSDNPublisher
    print("   ✓ 基础发布器导入成功")
    print("   ✓ 通用处理器导入成功")
    print("   ✓ CSDN发布器导入成功")
except Exception as e:
    print(f"   ✗ 发布器模块导入失败: {e}")

# 测试6: 目录结构
print("\n6. 检查目录结构...")
directories = [
    'src/core',
    'src/publisher',
    'src/utils',
    'scripts',
    'docs',
    'data/cookies',
    'data/logs',
    'config'
]
all_exist = True
for dir_path in directories:
    full_path = project_root / dir_path
    if full_path.exists():
        print(f"   ✓ {dir_path} 存在")
    else:
        print(f"   ✗ {dir_path} 不存在")
        all_exist = False

if all_exist:
    print("   ✓ 所有必需目录都存在")

# 测试7: 文档文件
print("\n7. 检查文档文件...")
documents = [
    'README.md',
    'docs/README.md',
    'docs/USAGE.md',
    'docs/CHANGELOG.md',
    'requirements.txt'
]
all_exist = True
for doc_path in documents:
    full_path = project_root / doc_path
    if full_path.exists():
        print(f"   ✓ {doc_path} 存在")
    else:
        print(f"   ✗ {doc_path} 不存在")
        all_exist = False

if all_exist:
    print("   ✓ 所有文档文件都存在")

# 测试8: Cookie 和日志目录可写
print("\n8. 测试数据目录权限...")
try:
    import tempfile
    import os
    
    # 测试 cookies 目录
    cookie_dir = project_root / 'data' / 'cookies'
    test_file = cookie_dir / 'test.tmp'
    test_file.write_text('test')
    test_file.unlink()
    print("   ✓ cookies 目录可写")
    
    # 测试 logs 目录
    log_dir = project_root / 'data' / 'logs'
    test_file = log_dir / 'test.tmp'
    test_file.write_text('test')
    test_file.unlink()
    print("   ✓ logs 目录可写")
except Exception as e:
    print(f"   ✗ 目录权限测试失败: {e}")

# 总结
print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print()
print("如果所有测试都通过，说明重构成功！")
print("现在可以运行: python publish.py")
print()

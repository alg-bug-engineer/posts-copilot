#!/bin/bash

# 自动化内容生成和发布脚本
# 这个脚本会：
# 1. 自动生成内容
# 2. 自动发布到所有启用的平台

set -e

# 获取脚本所在目录的父目录（项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "========================================"
echo "🚀 自动化内容生成和发布流水线"
echo "========================================"
echo ""

# 检查是否设置了 ZHIPUAI_API_KEY
if [ -z "$ZHIPUAI_API_KEY" ]; then
    echo "❌ 错误: 未设置 ZHIPUAI_API_KEY 环境变量"
    echo ""
    echo "请设置环境变量："
    echo "  export ZHIPUAI_API_KEY='your-api-key-here'"
    echo ""
    exit 1
fi

# 检查 Chrome 是否在调试模式下运行
echo "🔍 检查 Chrome 调试模式..."
if ! lsof -i :9222 > /dev/null 2>&1; then
    echo "⚠️  Chrome 调试模式未运行"
    echo ""
    echo "正在启动 Chrome 调试模式..."
    bash scripts/start_chrome.sh &
    
    # 等待 Chrome 启动
    sleep 3
    
    if ! lsof -i :9222 > /dev/null 2>&1; then
        echo "❌ Chrome 启动失败"
        exit 1
    fi
    
    echo "✅ Chrome 调试模式已启动"
else
    echo "✅ Chrome 调试模式已运行"
fi

echo ""
echo "========================================"
echo "📝 开始执行流水线..."
echo "========================================"
echo ""

# 运行流水线
# 默认参数：
# - 抓取 10 条新闻
# - 生成 1 篇文章
# - 快速搜索模式
# - API 延迟 2 秒
# - 发布延迟 3 秒
python3 auto_publish_pipeline.py \
    --news-limit 10 \
    --article-limit 1 \
    --search-depth quick \
    --delay 2.0 \
    --publish-delay 3.0

echo ""
echo "========================================"
echo "✅ 流水线执行完成"
echo "========================================"
echo ""

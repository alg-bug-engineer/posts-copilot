#!/bin/bash

# Chrome 调试模式启动脚本

echo "=========================================="
echo "  启动 Chrome 调试模式"
echo "=========================================="
echo ""

# 检查是否已经在运行
if curl -s http://127.0.0.1:9222/json/version > /dev/null 2>&1; then
    echo "⚠️  Chrome 调试模式已在运行"
    echo ""
    echo "如需重启，请先关闭现有的 Chrome 实例"
    exit 0
fi

# 根据操作系统启动 Chrome
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "正在启动 Chrome（macOS）..."
    echo ""
    
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    if [ ! -f "$CHROME_PATH" ]; then
        echo "✗ 未找到 Chrome"
        echo "请确保 Chrome 已安装在：/Applications/Google Chrome.app"
        exit 1
    fi
    
    # 启动 Chrome
    "$CHROME_PATH" \
        --remote-debugging-port=9222 \
        --user-data-dir="/tmp/chrome_dev" \
        about:blank \
        > /dev/null 2>&1 &
    
    CHROME_PID=$!
    
    echo "✓ Chrome 已启动（PID: $CHROME_PID）"
    echo ""
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "正在启动 Chrome（Linux）..."
    echo ""
    
    if ! command -v google-chrome &> /dev/null; then
        echo "✗ 未找到 google-chrome 命令"
        echo "请确保 Chrome 已安装"
        exit 1
    fi
    
    # 启动 Chrome
    google-chrome \
        --remote-debugging-port=9222 \
        --user-data-dir="/tmp/chrome_dev" \
        > /dev/null 2>&1 &
    
    CHROME_PID=$!
    
    echo "✓ Chrome 已启动（PID: $CHROME_PID）"
    echo ""
    
else
    echo "✗ 不支持的操作系统：$OSTYPE"
    exit 1
fi

# 等待 Chrome 启动
echo "等待 Chrome 调试端口就绪..."
for i in {1..10}; do
    if curl -s http://127.0.0.1:9222/json/version > /dev/null 2>&1; then
        echo ""
        echo "✓ Chrome 调试模式已就绪！"
        echo ""
        echo "调试地址：http://127.0.0.1:9222"
        echo ""
        echo "=========================================="
        echo "  现在可以运行发布脚本了"
        echo "=========================================="
        echo ""
        echo "运行命令："
        echo "  python publish.py"
        echo ""
        echo "或使用："
        echo "  ./scripts/start.sh"
        echo ""
        exit 0
    fi
    sleep 1
done

echo ""
echo "⚠️  Chrome 启动较慢，请稍后..."
echo ""
echo "可以通过以下命令检查状态："
echo "  curl http://127.0.0.1:9222/json/version"
echo ""

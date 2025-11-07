#!/bin/bash

# Chrome 调试模式启动脚本
# 自动检测并清理旧实例，然后启动新的 Chrome 调试实例

echo "=========================================="
echo "  启动 Chrome 调试模式"
echo "=========================================="
echo ""

# 函数：检测 Chrome 调试进程
check_chrome_running() {
    if curl -s http://127.0.0.1:9222/json/version > /dev/null 2>&1; then
        return 0  # 运行中
    else
        return 1  # 未运行
    fi
}

# 函数：查找 Chrome 调试进程的 PID
find_chrome_pid() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS: 查找带有 remote-debugging-port=9222 的 Chrome 进程
        ps aux | grep "[C]hrome.*remote-debugging-port=9222" | awk '{print $2}'
    else
        # Linux
        ps aux | grep "[c]hrome.*remote-debugging-port=9222" | awk '{print $2}'
    fi
}

# 函数：停止 Chrome 调试进程
kill_chrome() {
    echo "🔍 检查现有的 Chrome 调试进程..."
    
    local pids=$(find_chrome_pid)
    
    if [ -z "$pids" ]; then
        echo "✓ 没有发现运行中的 Chrome 调试进程"
        echo ""
        return 0
    fi
    
    echo "⚠️  发现运行中的 Chrome 调试进程："
    echo "$pids" | while read pid; do
        echo "  - PID: $pid"
    done
    echo ""
    
    echo "🛑 正在停止旧的 Chrome 实例..."
    
    # 尝试优雅关闭
    echo "$pids" | while read pid; do
        if [ -n "$pid" ]; then
            kill "$pid" 2>/dev/null
        fi
    done
    
    # 等待进程关闭
    sleep 2
    
    # 检查是否还在运行
    pids=$(find_chrome_pid)
    if [ -n "$pids" ]; then
        echo "⚠️  部分进程未响应，强制终止..."
        echo "$pids" | while read pid; do
            if [ -n "$pid" ]; then
                kill -9 "$pid" 2>/dev/null
            fi
        done
        sleep 1
    fi
    
    # 清理用户数据目录锁文件
    if [ -d "/tmp/chrome_dev" ]; then
        echo "🧹 清理临时数据目录锁文件..."
        rm -f /tmp/chrome_dev/SingletonLock 2>/dev/null
        rm -f /tmp/chrome_dev/SingletonSocket 2>/dev/null
        rm -f /tmp/chrome_dev/SingletonCookie 2>/dev/null
    fi
    
    echo "✓ 旧实例已停止"
    echo ""
}

# 主流程：先清理旧实例
kill_chrome

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
    
    # 启动 Chrome（后台模式配置）
    "$CHROME_PATH" \
        --remote-debugging-port=9222 \
        --user-data-dir="/tmp/chrome_dev" \
        --disable-popup-blocking \
        --disable-notifications \
        --disable-infobars \
        --no-first-run \
        --no-default-browser-check \
        about:blank \
        > /dev/null 2>&1 &
    
    CHROME_PID=$!
    
    echo "✓ Chrome 已启动（PID: $CHROME_PID，后台模式）"
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
    
    # 启动 Chrome（后台模式配置）
    google-chrome \
        --remote-debugging-port=9222 \
        --user-data-dir="/tmp/chrome_dev" \
        --disable-popup-blocking \
        --disable-notifications \
        --disable-infobars \
        --no-first-run \
        --no-default-browser-check \
        > /dev/null 2>&1 &
    
    CHROME_PID=$!
    
    echo "✓ Chrome 已启动（PID: $CHROME_PID，后台模式）"
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

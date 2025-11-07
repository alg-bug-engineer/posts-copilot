#!/bin/bash

# 停止 Chrome 调试模式脚本

echo "=========================================="
echo "  停止 Chrome 调试模式"
echo "=========================================="
echo ""

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

# 查找进程
echo "🔍 查找 Chrome 调试进程..."
pids=$(find_chrome_pid)

if [ -z "$pids" ]; then
    echo "✓ 没有发现运行中的 Chrome 调试进程"
    echo ""
    exit 0
fi

echo "⚠️  发现运行中的 Chrome 调试进程："
echo "$pids" | while read pid; do
    echo "  - PID: $pid"
done
echo ""

# 停止进程
echo "🛑 正在停止 Chrome 调试进程..."

# 尝试优雅关闭
echo "$pids" | while read pid; do
    if [ -n "$pid" ]; then
        echo "  停止 PID: $pid"
        kill "$pid" 2>/dev/null
    fi
done

# 等待进程关闭
sleep 2

# 检查是否还在运行
pids=$(find_chrome_pid)
if [ -n "$pids" ]; then
    echo ""
    echo "⚠️  部分进程未响应，强制终止..."
    echo "$pids" | while read pid; do
        if [ -n "$pid" ]; then
            echo "  强制终止 PID: $pid"
            kill -9 "$pid" 2>/dev/null
        fi
    done
    sleep 1
fi

# 清理用户数据目录锁文件
if [ -d "/tmp/chrome_dev" ]; then
    echo ""
    echo "🧹 清理临时数据目录锁文件..."
    rm -f /tmp/chrome_dev/SingletonLock 2>/dev/null
    rm -f /tmp/chrome_dev/SingletonSocket 2>/dev/null
    rm -f /tmp/chrome_dev/SingletonCookie 2>/dev/null
fi

echo ""
echo "✓ Chrome 调试模式已停止"
echo ""
echo "=========================================="
echo ""

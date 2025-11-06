#!/bin/bash

# 博客自动发布工具 - 快速启动脚本

echo "=========================================="
echo "  博客自动发布工具 v2.0"
echo "=========================================="
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
pip3 show selenium > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "警告: 缺少依赖，正在安装..."
    pip3 install -r requirements.txt
fi

# 检查配置文件
if [ ! -f "config/common.yaml" ]; then
    echo "警告: 配置文件不存在，正在复制默认配置..."
    if [ -f "config/common.default.yaml" ]; then
        cp config/common.default.yaml config/common.yaml
        echo "请编辑 config/common.yaml 配置文件后重新运行"
        exit 1
    else
        echo "错误: 默认配置文件不存在"
        exit 1
    fi
fi

# 检查 Chrome 调试模式
echo ""
echo "检查 Chrome 调试模式..."
if ! curl -s http://127.0.0.1:9222/json/version > /dev/null 2>&1; then
    echo ""
    echo "=========================================="
    echo "  ⚠️  Chrome 调试模式未启动！"
    echo "=========================================="
    echo ""
    echo "请在新终端窗口中运行以下命令："
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \'
        echo '  --remote-debugging-port=9222 \'
        echo '  --user-data-dir="/tmp/chrome_dev"'
        echo ""
        echo "💡 提示：可以复制下面的命令："
        echo ""
        echo "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=\"/tmp/chrome_dev\""
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo 'google-chrome \'
        echo '  --remote-debugging-port=9222 \'
        echo '  --user-data-dir="/tmp/chrome_dev"'
        echo ""
        echo "💡 提示：可以复制下面的命令："
        echo ""
        echo "google-chrome --remote-debugging-port=9222 --user-data-dir=\"/tmp/chrome_dev\""
    fi
    echo ""
    echo "=========================================="
    echo ""
    
    # 循环检测直到 Chrome 启动
    echo "等待 Chrome 启动中..."
    echo "（启动 Chrome 后会自动继续，或按 Ctrl+C 退出）"
    echo ""
    
    for i in {1..60}; do
        if curl -s http://127.0.0.1:9222/json/version > /dev/null 2>&1; then
            echo ""
            echo "✓ 检测到 Chrome 调试模式已启动！"
            sleep 1
            break
        fi
        
        # 每5秒显示一次提示
        if [ $((i % 5)) -eq 0 ]; then
            echo "⏳ 等待中... ($i/60 秒)"
        fi
        
        sleep 1
    done
    
    # 最后再检查一次
    if ! curl -s http://127.0.0.1:9222/json/version > /dev/null 2>&1; then
        echo ""
        echo "✗ Chrome 调试模式仍未启动"
        echo "请先启动 Chrome 后再运行此脚本"
        exit 1
    fi
else
    echo "✓ Chrome 调试模式已运行"
fi

# 运行发布脚本
echo ""
echo "启动发布脚本..."
echo ""
python3 scripts/publish.py

echo ""
echo "程序已退出"

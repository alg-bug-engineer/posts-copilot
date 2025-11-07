#!/bin/bash

# Chrome 调试模式重启脚本
# 快速重启 Chrome 调试实例

echo "=========================================="
echo "  重启 Chrome 调试模式"
echo "=========================================="
echo ""

# 调用 start_chrome.sh（它会自动清理旧实例并启动新实例）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SCRIPT_DIR/start_chrome.sh"

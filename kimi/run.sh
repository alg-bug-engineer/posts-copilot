#!/bin/bash

# Kimi 内容自动生成系统 - 启动脚本

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}          🚀 Kimi 内容自动生成系统${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检查 API 密钥
if [ -z "$MOONSHOT_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  未检测到 MOONSHOT_API_KEY 环境变量${NC}"
    echo ""
    echo "请先设置 API 密钥："
    echo -e "${GREEN}  export MOONSHOT_API_KEY=\"your-api-key-here\"${NC}"
    echo ""
    echo "或者现在输入（临时设置）："
    read -p "API Key: " api_key
    if [ -n "$api_key" ]; then
        export MOONSHOT_API_KEY="$api_key"
        echo -e "${GREEN}✓ API 密钥已设置${NC}"
        echo ""
    else
        echo -e "${RED}❌ 未设置 API 密钥，退出${NC}"
        exit 1
    fi
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 Python3，请先安装${NC}"
    exit 1
fi

# 检查依赖
echo -e "${BLUE}检查 Python 依赖...${NC}"
python3 -c "import openai, httpx, yaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  缺少依赖包，正在安装...${NC}"
    pip3 install openai httpx pyyaml
    echo ""
fi

# 获取脚本目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# 显示菜单
echo -e "${GREEN}请选择操作模式：${NC}"
echo ""
echo "  1) 完整流水线（探索 → 大纲 → 生成文章）"
echo "  2) 仅探索主题"
echo "  3) 仅生成大纲"
echo "  4) 仅生成文章"
echo "  5) 批量生成系列文章"
echo "  6) 查看已有主题和大纲"
echo "  7) 查看指定主题的大纲详情"
echo "  0) 退出"
echo ""
read -p "请输入选项 [0-7]: " choice

case $choice in
    1)
        echo ""
        read -p "请输入主题名称: " topic
        read -p "是否指定章节范围？(如: 1-3，留空表示全部): " range
        
        if [ -n "$range" ]; then
            python3 main.py --full "$topic" --range "$range"
        else
            python3 main.py --full "$topic"
        fi
        ;;
    
    2)
        echo ""
        read -p "请输入要探索的主题: " topic
        python3 main.py --explore "$topic"
        ;;
    
    3)
        echo ""
        read -p "请输入主题名称: " topic
        python3 main.py --curriculum "$topic"
        ;;
    
    4)
        echo ""
        read -p "请输入主题名称: " topic
        read -p "请输入章节编号: " chapter
        python3 main.py --article "$topic" --chapter "$chapter"
        ;;
    
    5)
        echo ""
        read -p "请输入主题名称: " topic
        read -p "请输入章节范围 (如: 1-5): " range
        
        if [ -n "$range" ]; then
            python3 main.py --series "$topic" --range "$range"
        else
            python3 main.py --series "$topic"
        fi
        ;;
    
    6)
        python3 main.py --list
        ;;
    
    7)
        echo ""
        read -p "请输入主题名称: " topic
        python3 main.py --show "$topic"
        ;;
    
    0)
        echo ""
        echo "再见！"
        exit 0
        ;;
    
    *)
        echo ""
        echo -e "${RED}❌ 无效的选项${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}          ✅ 操作完成${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

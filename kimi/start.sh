#!/bin/bash

# AI 信息挖掘助手 - 快速启动脚本

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  🔍 AI 信息挖掘助手${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 检查 API 密钥
if [ -z "$MOONSHOT_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  检测到 MOONSHOT_API_KEY 未设置${NC}"
    echo ""
    read -p "请输入您的 API 密钥: " api_key
    export MOONSHOT_API_KEY="$api_key"
    echo -e "${GREEN}✓ API 密钥已设置${NC}"
    echo ""
fi

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 Python3，请先安装 Python${NC}"
    exit 1
fi

# 检查依赖
echo -e "${BLUE}检查依赖...${NC}"
python3 -c "import openai, httpx, yaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  缺少依赖，正在安装...${NC}"
    pip3 install openai httpx pyyaml
    echo ""
fi

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 菜单选择
echo -e "${GREEN}请选择运行模式:${NC}"
echo "1) 交互模式（推荐）"
echo "2) 单个主题研究"
echo "3) 批量研究"
echo "4) 查看示例主题"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo -e "${BLUE}启动交互模式...${NC}"
        python3 "$DIR/research_assistant_v2.py"
        ;;
    2)
        echo ""
        read -p "请输入研究主题: " topic
        if [ -z "$topic" ]; then
            echo -e "${RED}❌ 主题不能为空${NC}"
            exit 1
        fi
        echo -e "${BLUE}开始研究: $topic${NC}"
        python3 "$DIR/research_assistant_v2.py" -t "$topic"
        ;;
    3)
        echo ""
        read -p "请输入主题列表文件路径 (默认: example_topics.txt): " batch_file
        batch_file=${batch_file:-"$DIR/example_topics.txt"}
        
        if [ ! -f "$batch_file" ]; then
            echo -e "${RED}❌ 文件不存在: $batch_file${NC}"
            exit 1
        fi
        
        echo -e "${BLUE}开始批量研究...${NC}"
        python3 "$DIR/research_assistant_v2.py" -b "$batch_file"
        ;;
    4)
        echo -e "${BLUE}示例主题列表:${NC}"
        echo ""
        cat "$DIR/example_topics.txt"
        echo ""
        echo -e "${GREEN}您可以编辑 example_topics.txt 来定制主题列表${NC}"
        ;;
    *)
        echo -e "${RED}❌ 无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ 完成！${NC}"

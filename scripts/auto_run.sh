#!/bin/bash
# 
# 一键启动脚本：内容生成 + 自动分发
# 用于快速执行完整的内容生成和发布流程
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色信息
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# 打印分隔线
print_separator() {
    echo "========================================================================"
}

# 检查依赖
check_dependencies() {
    info "检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        error "未找到 Python3，请先安装"
        exit 1
    fi
    
    # 检查Chrome
    if ! command -v google-chrome &> /dev/null && ! command -v chromium &> /dev/null; then
        warning "未找到 Chrome 浏览器，发布功能可能无法使用"
    fi
    
    # 检查API密钥
    if [ -z "$ZHIPUAI_API_KEY" ]; then
        warning "未设置 ZHIPUAI_API_KEY 环境变量，内容生成功能将无法使用"
        warning "设置方法: export ZHIPUAI_API_KEY='your-api-key'"
    fi
    
    success "依赖检查完成"
}

# 生成内容
generate_content() {
    local news_limit=${1:-10}
    local article_limit=${2:-5}
    local search_depth=${3:-quick}
    
    print_separator
    info "开始生成内容..."
    print_separator
    
    if [ -z "$ZHIPUAI_API_KEY" ]; then
        error "未设置 ZHIPUAI_API_KEY，无法生成内容"
        return 1
    fi
    
    python3 generate/auto_content_pipeline.py \
        --news-limit "$news_limit" \
        --article-limit "$article_limit" \
        --search-depth "$search_depth" \
        --delay 2.0 \
        --output-dir posts
    
    if [ $? -eq 0 ]; then
        success "内容生成完成！"
        return 0
    else
        error "内容生成失败"
        return 1
    fi
}

# 发布内容
publish_content() {
    local skip_published=${1:-yes}
    
    print_separator
    info "开始发布内容..."
    print_separator
    
    if [ "$skip_published" = "yes" ]; then
        python3 batch_publish.py --skip-published
    else
        python3 batch_publish.py
    fi
    
    if [ $? -eq 0 ]; then
        success "内容发布完成！"
        return 0
    else
        error "内容发布失败"
        return 1
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
用法: $0 [选项]

自动化内容生成和发布工具

选项:
    -h, --help              显示此帮助信息
    -g, --generate-only     仅生成内容，不发布
    -p, --publish-only      仅发布内容，不生成
    -n, --news-limit N      抓取的新闻数量（默认: 10）
    -a, --article-limit N   生成的文章数量（默认: 5）
    -d, --depth MODE        搜索深度: quick 或 deep（默认: quick）
    -f, --force-publish     强制发布所有文章（包括已发布的）
    --check                 检查依赖和配置

示例:
    # 使用默认配置（生成5篇 + 发布）
    $0

    # 仅生成3篇文章
    $0 --generate-only --article-limit 3

    # 仅发布已生成的文章
    $0 --publish-only

    # 生成10篇文章，使用深度搜索
    $0 --article-limit 10 --depth deep

    # 检查环境配置
    $0 --check
EOF
}

# 主函数
main() {
    # 默认参数
    local mode="both"  # both, generate, publish
    local news_limit=10
    local article_limit=5
    local search_depth="quick"
    local force_publish="no"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -g|--generate-only)
                mode="generate"
                shift
                ;;
            -p|--publish-only)
                mode="publish"
                shift
                ;;
            -n|--news-limit)
                news_limit="$2"
                shift 2
                ;;
            -a|--article-limit)
                article_limit="$2"
                shift 2
                ;;
            -d|--depth)
                search_depth="$2"
                shift 2
                ;;
            -f|--force-publish)
                force_publish="yes"
                shift
                ;;
            --check)
                check_dependencies
                exit 0
                ;;
            *)
                error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 打印欢迎信息
    print_separator
    echo -e "${GREEN}"
    cat << "EOF"
    ____             __            ______            _ __      __ 
   / __ \____  _____/ /______     / ____/___  ____  (_) /___  / /_
  / /_/ / __ \/ ___/ __/ ___/    / /   / __ \/ __ \/ / / __ \/ __/
 / ____/ /_/ (__  ) /_(__  )    / /___/ /_/ / /_/ / / / /_/ / /_  
/_/    \____/____/\__/____/     \____/\____/ .___/_/_/\____/\__/  
                                          /_/                      
EOF
    echo -e "${NC}"
    info "自动化内容生成与发布系统"
    print_separator
    
    # 检查依赖
    check_dependencies
    
    # 执行任务
    case $mode in
        both)
            info "模式: 完整流程（生成 + 发布）"
            if generate_content "$news_limit" "$article_limit" "$search_depth"; then
                echo ""
                info "等待3秒后开始发布..."
                sleep 3
                
                skip_pub="yes"
                [ "$force_publish" = "yes" ] && skip_pub="no"
                publish_content "$skip_pub"
            else
                error "生成失败，跳过发布步骤"
                exit 1
            fi
            ;;
        generate)
            info "模式: 仅生成内容"
            generate_content "$news_limit" "$article_limit" "$search_depth"
            ;;
        publish)
            info "模式: 仅发布内容"
            skip_pub="yes"
            [ "$force_publish" = "yes" ] && skip_pub="no"
            publish_content "$skip_pub"
            ;;
    esac
    
    # 完成
    print_separator
    success "所有任务执行完成！"
    print_separator
    
    # 显示生成的文章
    if [ "$mode" = "both" ] || [ "$mode" = "generate" ]; then
        info "生成的文章："
        ls -lh posts/*.md 2>/dev/null | tail -n "$article_limit" || warning "未找到生成的文章"
    fi
}

# 执行主函数
main "$@"

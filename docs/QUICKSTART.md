# 快速开始指南

## 🎯 使用场景

### 场景一：内容生成 + 自动分发（完整闭环）

```bash
# 1. 设置API密钥
export ZHIPUAI_API_KEY="your-api-key"

# 2. 自动生成热点文章（从量子位抓取 -> 生成文章）
python generate/auto_content_pipeline.py --article-limit 5

# 3. 自动分发到各平台
python batch_publish.py
```

### 场景二：仅内容生成

```bash
# 抓取量子位TOP10热点，生成3篇文章
python generate/auto_content_pipeline.py \
  --news-limit 10 \
  --article-limit 3 \
  --search-depth deep

# 查看生成的文章
ls posts/*.md
```

### 场景三：仅内容分发

```bash
# 单篇文章发布
python publish.py posts/my-article.md

# 批量发布
python batch_publish.py
```

## 🚀 5分钟快速上手

### 第一步：环境准备

```bash
# 克隆项目
git clone https://github.com/your-username/posts-copilot.git
cd posts-copilot

# 安装依赖
pip install -r requirements.txt

# 安装ChromeDriver
# macOS
brew install chromedriver

# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# Windows
# 下载对应版本的ChromeDriver并添加到PATH
```

### 第二步：配置平台账号

```bash
# 复制配置模板
cp config/common.yaml.example config/common.yaml

# 编辑配置文件
vim config/common.yaml
```

在配置文件中设置要发布的平台（设为true启用）：

```yaml
platforms:
  csdn: true
  juejin: true
  zhihu: true
  cto51: false
  alicloud: false
  toutiao: false
  wechat: false
```

### 第三步（可选）：配置内容生成

如果需要使用AI内容生成功能：

```bash
# 设置智谱AI密钥
export ZHIPUAI_API_KEY="your-zhipu-api-key"

# 或在配置文件中设置
vim config/content_generation.yaml
```

### 第四步：测试运行

#### 测试内容生成（可选）

```bash
# 测试爬虫
python generate/qbitai_crawler.py

# 测试完整流水线（生成1篇）
python generate/auto_content_pipeline.py --article-limit 1
```

#### 测试内容分发

```bash
# 准备一篇测试文章
cat > posts/test-article.md << 'EOF'
---
title: 测试文章标题
tags:
  - Python
  - AI
---

这是一篇测试文章。

## 测试内容

测试发布功能是否正常工作。
EOF

# 单平台测试（只发布到CSDN）
python publish.py posts/test-article.md --platforms csdn

# 如果成功，尝试发布到所有平台
python publish.py posts/test-article.md
```

## 📖 详细使用说明

### 内容生成模块

完整文档请参考 [内容生成文档](docs/CONTENT_GENERATION.md)

#### 基础用法

```bash
# 使用默认配置
python generate/auto_content_pipeline.py

# 自定义参数
python generate/auto_content_pipeline.py \
  --news-limit 15 \      # 抓取15条热点
  --article-limit 10 \   # 生成10篇文章
  --search-depth deep \  # 深度搜索资料
  --delay 3.0 \          # API请求间隔3秒
  --output-dir posts     # 输出到posts目录
```

#### Python API使用

```python
from generate.qbitai_crawler import QbitAICrawler
from generate.reference_searcher import ReferenceSearcher
from generate.enhanced_content_generator import EnhancedContentGenerator

# 1. 抓取热点
crawler = QbitAICrawler()
news_list = crawler.fetch_top_news(limit=10)

# 2. 搜索资料
searcher = ReferenceSearcher()
references = searcher.search_topic_references(
    topic=news_list[0]['title'],
    original_summary=news_list[0]['summary']
)

# 3. 生成文章
generator = EnhancedContentGenerator()
article = generator.generate_article_from_news(
    news_item=news_list[0],
    references=references,
    style="qbitai"
)

print(f"文章已保存: {article['file_path']}")
```

### 内容分发模块

完整文档请参考 [分发模块文档](docs/USAGE.md)

#### 单篇文章发布

```bash
# 发布到所有配置的平台
python publish.py posts/my-article.md

# 发布到指定平台
python publish.py posts/my-article.md --platforms csdn juejin

# 重新发布（跳过已发布检查）
python publish.py posts/my-article.md --force
```

#### 批量发布

```bash
# 发布posts目录下所有未发布的文章
python batch_publish.py

# 指定目录
python batch_publish.py --posts-dir articles/

# 设置并发数
python batch_publish.py --max-workers 3

# 跳过已发布文章
python batch_publish.py --skip-published
```

## 🎨 典型工作流

### 工作流1：每日自动化

```bash
#!/bin/bash
# daily_update.sh - 每日自动内容生成和分发

# 1. 生成今日热点文章
python generate/auto_content_pipeline.py \
  --news-limit 10 \
  --article-limit 3 \
  --search-depth quick

# 2. 等待人工审核（可选）
echo "请审核生成的文章，按Enter继续发布..."
read

# 3. 批量发布
python batch_publish.py --skip-published

echo "✅ 今日内容更新完成！"
```

### 工作流2：定时任务

```bash
# 添加到crontab
# 每天早上9点自动执行

0 9 * * * cd /path/to/posts-copilot && /path/to/daily_update.sh >> logs/daily.log 2>&1
```

### 工作流3：手动精选

```bash
# 1. 抓取热点，不自动生成
python generate/qbitai_crawler.py

# 2. 查看抓取的热点
cat data/qbitai_top10.json

# 3. 手动编写文章
vim posts/my-awesome-article.md

# 4. 发布
python publish.py posts/my-awesome-article.md
```

## ⚙️ 配置速查

### 平台配置文件

| 文件 | 说明 |
|------|------|
| `config/common.yaml` | 全局配置和平台开关 |
| `config/csdn.yaml` | CSDN平台专属配置 |
| `config/juejin.yaml` | 掘金平台专属配置 |
| `config/zhihu.yaml` | 知乎平台专属配置 |
| `config/content_generation.yaml` | 内容生成配置 |

### 关键配置项

```yaml
# common.yaml
platforms:
  csdn: true      # 启用CSDN
  juejin: true    # 启用掘金

browser:
  headless: false # 显示浏览器窗口（调试用）
  wait_time: 10   # 元素等待时间

# content_generation.yaml
generator:
  article_limit: 5  # 每次生成文章数
  style: "qbitai"   # 写作风格
  
search:
  depth: "quick"    # 搜索深度
```

## 🔧 故障排查

### 问题1: ChromeDriver版本不匹配

```bash
# 查看Chrome版本
google-chrome --version

# 下载对应版本的ChromeDriver
# https://chromedriver.chromium.org/downloads
```

### 问题2: 登录失效

```bash
# 清除缓存的登录状态
rm -rf data/cookies/*

# 重新登录
python publish.py posts/test.md --platforms csdn
```

### 问题3: API配额不足

```bash
# 检查API密钥
echo $ZHIPUAI_API_KEY

# 降低生成频率
python generate/auto_content_pipeline.py \
  --article-limit 1 \
  --delay 5.0
```

### 问题4: 元素定位失败

平台网页可能更新，需要更新选择器：

```bash
# 查看详细日志
tail -f data/logs/publisher.log

# 运行测试
python tests/test_csdn_publisher.py
```

## 📚 更多资源

- [完整文档](docs/) - 详细的使用和开发文档
- [内容生成指南](docs/CONTENT_GENERATION.md) - AI内容生成详解
- [平台对接指南](docs/DEVELOPMENT.md) - 如何添加新平台
- [常见问题](docs/FAQ.md) - 常见问题解答

## 🆘 获取帮助

```bash
# 查看命令行帮助
python publish.py --help
python batch_publish.py --help
python generate/auto_content_pipeline.py --help

# 运行测试套件
python -m pytest tests/

# 查看日志
tail -f data/logs/publisher.log
```

## 🚦 下一步

- ✅ 完成基础配置
- ✅ 测试单平台发布
- ✅ 测试批量发布
- 🎯 配置内容生成（可选）
- 🎯 设置定时任务
- 🎯 自定义样式和模板
- 🎯 添加更多平台支持

---

**Happy Publishing! 🎉**

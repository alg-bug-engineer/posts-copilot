# 多平台博客自动发布工具 🚀

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/your-username/posts-copilot.svg)](https://github.com/your-username/posts-copilot/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/your-username/posts-copilot.svg)](https://github.com/your-username/posts-copilot/issues)

一键将你的技术文章发布到多个平台！支持 CSDN、掘金、知乎、51CTO、阿里云开发者社区、今日头条、微信公众号等主流技术平台的自动化发布。

## ✨ 核心特性

- 🎯 **多平台支持**：一次写作，多处发布，覆盖 7+ 主流技术平台
- 🤖 **智能登录管理**：自动保存和恢复登录状态，告别重复登录烦恼  
- 📝 **Markdown 原生支持**：完美支持 Markdown 格式和 Front Matter 元数据
- 🔧 **灵活配置系统**：支持标签、分类、封面图等个性化设置
- 📊 **详细日志记录**：完善的日志系统，便于调试和问题追踪
- 🏗️ **可扩展架构**：基于抽象类设计，轻松添加新平台支持
- 🎨 **AI 内容生成**：集成智谱 AI，支持热点新闻内容自动生成（可选）

## 🌟 支持平台

| 平台 | 状态 | 功能特点 |
|------|------|----------|
| [CSDN](https://blog.csdn.net/) | ✅ 已支持 | 标签、分类、封面图 |
| [掘金](https://juejin.cn/) | ✅ 已支持 | 标签、专栏、封面图 |
| [知乎](https://zhihu.com/) | ✅ 已支持 | 话题标签、封面图 |
| [51CTO](https://blog.51cto.com/) | ✅ 已支持 | 分类、标签 |
| [阿里云开发者社区](https://developer.aliyun.com/) | ✅ 已支持 | 标签、分类 |
| [今日头条](https://www.toutiao.com/) | ✅ 已支持 | 标签、封面图 |
| [微信公众号](https://mp.weixin.qq.com/) | ✅ 已支持 | 保存草稿 |

## 📋 目录

- [快速开始](#-快速开始)
- [安装部署](#-安装部署)
- [使用指南](#-使用指南)
- [配置说明](#️-配置说明)
- [扩展开发](#-扩展开发)
- [常见问题](#-常见问题)
- [贡献指南](#-贡献指南)

## � 快速开始

### 1️⃣ 环境准备

确保你的系统已安装：
- Python 3.7 或更高版本
- Google Chrome 浏览器

### 2️⃣ 克隆项目

```bash
git clone https://github.com/your-username/posts-copilot.git
cd posts-copilot
```

### 3️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 4️⃣ 启动 Chrome 调试模式

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome_dev"

# Linux  
google-chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_dev"

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_dev"
```

### 5️⃣ 运行发布

```bash
python publish.py
```

按照提示选择文章和平台，首次使用需要手动登录各个平台（登录状态会自动保存）。

> 💡 **提示**：详细安装和配置说明请查看 [安装部署](#-安装部署) 章节。

## � 安装部署

### 环境要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.7+ | 推荐使用 3.8+ |
| Chrome | 最新版 | 用于自动化操作 |
| ChromeDriver | 自动匹配 | 可选，工具会自动管理 |

### 详细安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/posts-copilot.git
   cd posts-copilot
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置文件设置**
   
   复制示例配置文件并根据需要修改：
   ```bash
   # 复制通用配置
   cp config/common.yaml.example config/common.yaml
   
   # 编辑配置文件，设置文章目录等
   vim config/common.yaml
   ```

5. **首次运行**
   ```bash
   python publish.py
   ```

## 📖 使用指南

### 基本使用流程

1. **准备文章**：将 Markdown 文章放在指定目录
2. **启动 Chrome 调试模式**：运行调试命令启动 Chrome
3. **运行发布脚本**：执行 `python publish.py`（单篇）或 `python batch_publish.py`（批量）
4. **选择文章和平台**：按提示进行选择
5. **首次登录**：首次使用需要手动登录各平台（会自动保存登录状态）
6. **自动发布**：等待程序自动完成发布流程

### 📦 批量并发发布（新功能）

一次性将多篇文章并发发布到多个平台：

```bash
# 基本使用（默认并发数3）
python batch_publish.py

# 自定义并发数
python batch_publish.py --workers 6

# 演练模式（查看计划但不发布）
python batch_publish.py --dry-run
```

**工作原理**：
- 循环处理每篇文章（如有10篇文章，循环10次）
- 每篇文章并发发布到多个平台（如6个平台同时发布）
- 使用线程池实现快速切换，比顺序发布快2-3倍

详细说明请查看：[批量发布使用指南](docs/BATCH_PUBLISH.md)

### 文章格式要求

支持标准 Markdown 格式，可在文章开头添加 Front Matter 元数据：

```markdown
---
title: 文章标题
description: 文章描述  
tags: [Python, 自动化, 工具]
category: 技术分享
cover: https://example.com/cover.jpg
---

# 文章正文

你的 Markdown 内容...
```

### 平台特定配置

每个平台都有独立的配置文件，支持个性化设置：

- `config/csdn.yaml` - CSDN 相关配置
- `config/juejin.yaml` - 掘金相关配置  
- `config/zhihu.yaml` - 知乎相关配置
- 等等...

## ⚙️ 配置说明

### 通用配置 (`config/common.yaml`)

```yaml
# 文章目录配置
content_dir: /path/to/your/articles/

# Chrome 调试配置
debugger_address: 127.0.0.1:9222

# 发布模式
auto_publish: false  # true=自动发布, false=需确认

# 平台开关
enable:
  csdn: true
  juejin: true
  zhihu: true
  cto51: true
  alicloud: true
  toutiao: false
  wechat: false

# 日志配置
logging:
  level: INFO
  file: data/logs/publisher.log
```

### 平台配置示例

各平台都有独立的配置文件，以下是主要配置项：

#### CSDN (`config/csdn.yaml`)
```yaml
site: https://editor.csdn.net/md/
default_tags: [Python, 自动化, 工具]
default_category: 技术分享
visibility: 全部可见
```

#### 知乎 (`config/zhihu.yaml`)  
```yaml
site: https://zhuanlan.zhihu.com/write
auto_publish: false
use_column: true
default_topics: [人工智能, 编程, 技术]
```

#### 掘金 (`config/juejin.yaml`)
```yaml
site: https://juejin.cn/editor/drafts/new
default_tags: [Python, 自动化]
default_category: 后端
```

> 📚 **详细配置说明**：查看 [配置文档](docs/CONFIGURATION.md) 了解所有配置选项
categories:
  - 技术文章
description: 文章摘要
image: https://example.com/cover.jpg
---

# 正文内容

这里是文章正文...
```

### 发布流程

1. **准备文章**：将 Markdown 文件放入 `content_dir` 目录
2. **运行脚本**：`python scripts/publish.py`
3. **选择文章**：从列表中选择要发布的文章
4. **选择平台**：选择目标平台或全部平台
5. **首次登录**：首次使用需手动登录（自动保存）
6. **等待完成**：脚本自动填充内容并发布

## 🏗️ 项目架构

### 核心架构设计

```
posts-copilot/
├── 📁 src/                   # 🚀 核心源代码
│   ├── 📁 core/             # 🔧 核心功能模块
│   │   ├── logger.py        # 📊 日志管理系统
│   │   └── session_manager.py # 🍪 会话和登录状态管理
│   ├── 📁 publisher/        # 🌐 平台发布器
│   │   ├── base_publisher.py # 🏛️ 发布器基类（抽象类）
│   │   ├── common_handler.py # 🔧 通用处理函数
│   │   ├── csdn_publisher.py # CSDN 发布器
│   │   ├── juejin_publisher.py # 掘金发布器
│   │   ├── zhihu_publisher.py # 知乎发布器
│   │   ├── alicloud_publisher.py # 阿里云开发者社区
│   │   ├── toutiao_publisher.py # 今日头条
│   │   ├── cto51_publisher.py # 51CTO 技术博客
│   │   └── wechat_publisher.py # 微信公众号
│   └── 📁 utils/            # 🛠️ 工具函数
├── 📁 config/               # ⚙️ 配置文件目录
├── 📁 generate/             # 🤖 AI 内容生成
│   ├── aibase_crawler.py    # AIBase 新闻爬虫（默认）
│   ├── qbitai_crawler.py    # 量子位新闻爬虫
│   ├── reference_searcher.py # 参考资料搜索
│   ├── enhanced_content_generator.py # 增强内容生成器
│   ├── auto_content_pipeline.py # 自动化内容生成流水线
│   ├── zhipu_content_generator.py # 智谱AI内容生成器
│   └── zhipu_news_search.py # 热点新闻搜索
├── 📁 docs/                 # 📚 项目文档
│   ├── NEWS_SOURCES.md      # 📰 多新闻源配置指南
│   ├── CHROME_SCRIPTS_GUIDE.md # 🌐 Chrome 管理脚本
│   └── ...                  # 其他文档
├── 📁 data/                 # 💾 数据存储
│   ├── cookies/            # 🍪 登录状态保存
│   ├── logs/               # 📝 运行日志
│   └── generated/          # 🤖 AI 生成的中间数据
├── 📁 posts/                # 📄 示例文章
└── 📄 publish.py            # 🚀 主发布脚本
```

## � 扩展开发

### 添加新平台支持

基于抽象基类 `BasePublisher`，可以快速添加新平台支持：

```python
from src.publisher.base_publisher import BasePublisher

class NewPlatformPublisher(BasePublisher):
    PLATFORM_NAME = "new_platform"
    
    def get_platform_name(self) -> str:
        return self.PLATFORM_NAME
    
    def publish(self, article_path: str) -> bool:
        """发布文章到新平台"""
        try:
            # 1. 加载平台配置
            config = self.load_config()
            
            # 2. 打开编辑页面
            self.driver.get(config['site'])
            
            # 3. 检查登录状态
            if not self.check_login():
                self.wait_login()
            
            # 4. 填充文章内容
            self.fill_title_and_content(article_path)
            
            # 5. 设置发布选项
            self.set_publish_options(config)
            
            # 6. 发布文章
            return self.submit_article()
            
        except Exception as e:
            self.logger.error(f"发布失败: {e}")
            return False
```

### 开发步骤

1. **创建发布器文件**：在 `src/publisher/` 目录创建新文件
2. **继承基类**：继承 `BasePublisher` 并实现必要方法
3. **添加配置**：在 `config/` 目录创建平台配置文件
4. **注册平台**：在 `publish.py` 中注册新平台
5. **测试验证**：编写测试用例验证功能

> 📖 **完整开发指南**：查看 [开发文档](docs/DEVELOPMENT.md) 了解详细步骤

## 🎯 核心功能特性

### 🔐 智能登录管理
- **自动保存**：首次登录后自动保存登录状态
- **状态检测**：智能检测当前登录状态，避免重复登录
- **Cookie 管理**：安全存储和管理各平台 Cookie
- **过期处理**：自动检测登录过期并提示重新登录

### 📊 完善的日志系统
```bash
2025-11-06 10:30:15 - CSDNPublisher - INFO - 🚀 开始发布文章到 CSDN
2025-11-06 10:30:16 - CSDNPublisher - INFO - ✅ 成功加载已保存的登录状态  
2025-11-06 10:30:17 - CSDNPublisher - INFO - ✅ 标题填充完成：《AI大模型革命》
2025-11-06 10:30:20 - CSDNPublisher - INFO - ✅ 内容填充完成 (2048 字符)
2025-11-06 10:30:25 - CSDNPublisher - INFO - 🎉 文章发布成功！
```

### 🛠️ 强大的工具函数
- `wait_login()` - 智能等待用户完成登录
- `safe_click()` - 安全点击（自动重试 + 异常处理）
- `safe_input()` - 安全输入（自动清空 + 防抖动）
- `check_login()` - 检测登录状态
- `retry_on_failure()` - 失败自动重试机制

### 🤖 AI 内容生成（可选）
- **多新闻源支持**：支持 AIBase（默认）、量子位等多个新闻源
- **智能爬虫**：自动抓取最新 AI 热点新闻
- **参考搜索**：自动搜索相关参考资料
- **智谱AI集成**：基于智谱AI的内容生成功能
- **内容生成**：基于热点生成高质量技术文章
- **自动发布**：生成内容可直接发布到各平台

> 📘 详细使用指南：查看 [多新闻源配置指南](docs/NEWS_SOURCES.md)

## ❓ 常见问题

<details>
<summary><strong>Q: 如何处理登录过期？</strong></summary>

删除对应平台的 Cookie 文件，重新登录：
```bash
rm data/cookies/csdn_cookies.pkl
python publish.py  # 重新登录
```
</details>

<details>
<summary><strong>Q: 元素定位失败怎么办？</strong></summary>

平台页面结构更新时可能导致元素定位失败：

1. **查看日志**：检查具体失败的元素定位符
2. **更新配置**：修改对应平台配置文件中的选择器
3. **反馈问题**：[提交 Issue](https://github.com/your-username/posts-copilot/issues) 报告问题

</details>

<details>
<summary><strong>Q: 如何批量发布文章？</strong></summary>

修改配置文件启用自动模式：
```yaml
# config/common.yaml
auto_publish: true  # 启用自动发布
```

然后运行脚本选择"发布到所有平台"选项。

</details>

<details>
<summary><strong>Q: Chrome 调试模式是什么？</strong></summary>

Chrome 调试模式允许程序连接到浏览器进行自动化操作，同时保持用户的登录状态和浏览器设置。这样可以：

- 保持各平台的登录状态
- 避免反爬虫检测
- 支持手动干预（如验证码）

</details>

## 🤝 贡献指南

欢迎为项目做出贡献！你可以通过以下方式参与：

### 🐛 报告问题
- [提交 Bug 报告](https://github.com/your-username/posts-copilot/issues/new?template=bug_report.md)
- [提出功能请求](https://github.com/your-username/posts-copilot/issues/new?template=feature_request.md)

### 💻 代码贡献
1. **Fork 项目**
2. **创建特性分支**：`git checkout -b feature/amazing-feature`
3. **提交更改**：`git commit -m 'Add some amazing feature'`
4. **推送分支**：`git push origin feature/amazing-feature`
5. **提交 PR**：创建 Pull Request

### 📝 文档改进
- 改进现有文档
- 翻译文档到其他语言
- 添加使用示例和教程

### 🆕 新平台支持
- 添加新的发布平台支持
- 完善现有平台功能
- 提供测试用例

> 📋 **贡献指南**：查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细的贡献流程

## 📄 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

## 🙏 致谢

感谢所有为项目做出贡献的开发者！

### 🌟 核心贡献者
- [@your-username](https://github.com/your-username) - 项目创建者和维护者

### 🛠️ 技术支持
- [Selenium WebDriver](https://selenium-python.readthedocs.io/) - 浏览器自动化
- [智谱AI](https://www.zhipuai.cn/) - AI 内容生成支持

---

<div align="center">

### 如果这个项目对你有帮助，请给个 ⭐️ Star 支持一下！

[![GitHub stars](https://img.shields.io/github/stars/your-username/posts-copilot.svg?style=social&label=Star)](https://github.com/your-username/posts-copilot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/your-username/posts-copilot.svg?style=social&label=Fork)](https://github.com/your-username/posts-copilot/network/members)

**[📖 文档](docs/) | [🐛 报告问题](https://github.com/your-username/posts-copilot/issues) | [💬 讨论](https://github.com/your-username/posts-copilot/discussions)**

</div>

当前完整支持：
- ✅ CSDN
- ✅ 掘金 (Juejin)
- ✅ 知乎 (Zhihu)
- ✅ 头条 (Toutiao)
- ✅ 51CTO
- ✅ 阿里云开发者社区 (Alicloud) ⭐ **NEW**

开发中：
- 🚧 简书
- 🚧 SegmentFault
- 🚧 开源中国
- 🚧 博客园

更多问题：[docs/README.md#常见问题](docs/README.md)

## 📊 日志分析

日志文件位于 `data/logs/`，按日期命名：

```bash
# 查看今天的日志
cat data/logs/$(date +%Y-%m-%d).log

# 实时查看
tail -f data/logs/$(date +%Y-%m-%d).log
```

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

查看 [CHANGELOG.md](docs/CHANGELOG.md) 了解详细更新历史。

### v2.0.0 (2025-11-05)

- 🎉 全新架构重构
- ✨ 登录状态自动保存
- 📊 完善的日志系统
- 🏗️ 可扩展的发布器架构

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📮 联系方式

- 提交 Issue: [GitHub Issues](../../issues)
- 邮件联系: your.email@example.com

## ⭐ Star History

如果这个项目对你有帮助，请给它一个 Star ⭐

---

**让博客发布变得简单而高效！** 🎉✨

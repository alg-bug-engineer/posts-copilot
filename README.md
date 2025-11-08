# 多平台博客自动发布工具 🚀# 多平台博客自动发布工具 🚀



[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[![GitHub stars](https://img.shields.io/github/stars/your-username/posts-copilot.svg)](https://github.com/your-username/posts-copilot/stargazers)

一键将技术文章发布到多个平台！支持 CSDN、掘金、知乎、51CTO、阿里云开发者社区、今日头条、微信公众号等主流技术平台的自动化发布。[![GitHub issues](https://img.shields.io/github/issues/your-username/posts-copilot.svg)](https://github.com/your-username/posts-copilot/issues)



## ✨ 核心特性一键将你的技术文章发布到多个平台！支持 CSDN、掘金、知乎、51CTO、阿里云开发者社区、今日头条、微信公众号等主流技术平台的自动化发布。



- 🎯 **多平台支持** - 一次写作，多处发布## ✨ 核心特性

- 🤖 **智能登录管理** - 自动保存登录状态

- 📝 **Markdown 支持** - 完美支持 Markdown 格式- 🎯 **多平台支持**：一次写作，多处发布，覆盖 7+ 主流技术平台

- 🎨 **AI 内容生成** - 集成智谱 AI（可选）- 🤖 **智能登录管理**：自动保存和恢复登录状态，告别重复登录烦恼  

- 📝 **Markdown 原生支持**：完美支持 Markdown 格式和 Front Matter 元数据

## 🌟 支持平台- 🔧 **灵活配置系统**：支持标签、分类、封面图等个性化设置

- 📊 **详细日志记录**：完善的日志系统，便于调试和问题追踪

| 平台 | 状态 | 平台 | 状态 |- 🏗️ **可扩展架构**：基于抽象类设计，轻松添加新平台支持

|------|------|------|------|- 🎨 **AI 内容生成**：集成智谱 AI，支持热点新闻内容自动生成（可选）

| CSDN | ✅ | 掘金 | ✅ |

| 知乎 | ✅ | 51CTO | ✅ |## 🌟 支持平台

| 阿里云 | ✅ | 今日头条 | ✅ |

| 微信公众号 | ✅ | - | - || 平台 | 状态 | 功能特点 |

|------|------|----------|

## 🚀 快速开始| [CSDN](https://blog.csdn.net/) | ✅ 已支持 | 标签、分类、封面图 |

| [掘金](https://juejin.cn/) | ✅ 已支持 | 标签、专栏、封面图 |

### 1. 环境准备| [知乎](https://zhihu.com/) | ✅ 已支持 | 话题标签、封面图 |

| [51CTO](https://blog.51cto.com/) | ✅ 已支持 | 分类、标签 |

```bash| [阿里云开发者社区](https://developer.aliyun.com/) | ✅ 已支持 | 标签、分类 |

# 克隆项目| [今日头条](https://www.toutiao.com/) | ✅ 已支持 | 标签、封面图 |

git clone https://github.com/your-username/posts-copilot.git| [微信公众号](https://mp.weixin.qq.com/) | ✅ 已支持 | 保存草稿 |

cd posts-copilot

## 📋 目录

# 安装依赖

pip install -r requirements.txt- [快速开始](#-快速开始)

```- [安装部署](#-安装部署)

- [使用指南](#-使用指南)

### 2. 启动 Chrome 调试模式- [配置说明](#️-配置说明)

- [扩展开发](#-扩展开发)

```bash- [常见问题](#-常见问题)

# macOS- [贡献指南](#-贡献指南)

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \

  --remote-debugging-port=9222 \## � 快速开始

  --user-data-dir="/tmp/chrome_dev"

### 1️⃣ 环境准备

# Linux

google-chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_dev"确保你的系统已安装：

- Python 3.7 或更高版本

# Windows- Google Chrome 浏览器

"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_dev"

```### 2️⃣ 克隆项目



或使用快捷脚本：```bash

git clone https://github.com/your-username/posts-copilot.git

```bashcd posts-copilot

# macOS/Linux```

bash scripts/start_chrome.sh

### 3️⃣ 安装依赖

# 停止 Chrome

bash scripts/stop_chrome.sh```bash

```pip install -r requirements.txt

```

### 3. 配置

### 4️⃣ 启动 Chrome 调试模式

```bash

# 复制配置示例```bash

cp config/common.yaml.example config/common.yaml# macOS

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \

# 编辑配置（设置文章目录等）  --remote-debugging-port=9222 \

vim config/common.yaml  --user-data-dir="/tmp/chrome_dev"

```

# Linux  

### 4. 发布文章google-chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_dev"



```bash# Windows

# 单篇发布"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_dev"

python publish.py```



# 批量发布### 5️⃣ 运行发布

python batch_publish.py

```bash

# 自动化内容生成 + 发布python publish.py

python auto_publish_pipeline.py```

```

按照提示选择文章和平台，首次使用需要手动登录各个平台（登录状态会自动保存）。

## 📖 文章格式

> 💡 **提示**：详细安装和配置说明请查看 [安装部署](#-安装部署) 章节。

支持标准 Markdown，可添加 Front Matter 元数据：

## � 安装部署

```markdown

---### 环境要求

title: 文章标题

description: 文章描述| 组件 | 版本要求 | 说明 |

tags: [Python, 自动化]|------|----------|------|

category: 技术分享| Python | 3.7+ | 推荐使用 3.8+ |

cover: https://example.com/cover.jpg| Chrome | 最新版 | 用于自动化操作 |

---| ChromeDriver | 自动匹配 | 可选，工具会自动管理 |



# 文章正文### 详细安装步骤



这里是 Markdown 内容...1. **克隆项目**

```   ```bash

   git clone https://github.com/your-username/posts-copilot.git

## 🤖 AI 内容生成（可选）   cd posts-copilot

   ```

```bash

# 设置智谱 AI Key2. **创建虚拟环境（推荐）**

export ZHIPUAI_API_KEY="your-api-key"   ```bash

   python -m venv venv

# 生成热点文章   source venv/bin/activate  # Linux/macOS

python generate/auto_content_pipeline.py --article-limit 5   # 或

   venv\Scripts\activate  # Windows

# 自动发布生成的文章   ```

python batch_publish.py

```3. **安装依赖**

   ```bash

## 📁 项目结构   pip install -r requirements.txt

   ```

```

posts-copilot/4. **配置文件设置**

├── src/                    # 核心源代码   

│   ├── core/              # 核心功能（日志、会话）   复制示例配置文件并根据需要修改：

│   ├── publisher/         # 各平台发布器   ```bash

│   └── utils/             # 工具函数   # 复制通用配置

├── config/                # 配置文件   cp config/common.yaml.example config/common.yaml

├── generate/              # AI 内容生成   

├── scripts/               # 辅助脚本   # 编辑配置文件，设置文章目录等

├── docs/                  # 文档   vim config/common.yaml

├── tests/                 # 测试文件   ```

├── publish.py             # 单篇发布

├── batch_publish.py       # 批量发布5. **首次运行**

└── auto_publish_pipeline.py  # 自动化流水线   ```bash

```   python publish.py

   ```

## ⚙️ 配置说明

## 📖 使用指南

### 通用配置 (`config/common.yaml`)

### 基本使用流程

```yaml

# 文章目录1. **准备文章**：将 Markdown 文章放在指定目录

content_dir: /path/to/your/articles/2. **启动 Chrome 调试模式**：运行调试命令启动 Chrome

3. **运行发布脚本**：执行 `python publish.py`（单篇）或 `python batch_publish.py`（批量）

# Chrome 调试地址4. **选择文章和平台**：按提示进行选择

debugger_address: 127.0.0.1:92225. **首次登录**：首次使用需要手动登录各平台（会自动保存登录状态）

6. **自动发布**：等待程序自动完成发布流程

# 平台开关

enable:### 📦 批量并发发布（新功能）

  csdn: true

  juejin: true一次性将多篇文章并发发布到多个平台：

  zhihu: true

  # ...更多平台```bash

```# 基本使用（默认并发数3）

python batch_publish.py

### 平台配置

# 自定义并发数

每个平台有独立配置文件：python batch_publish.py --workers 6

- `config/csdn.yaml` - CSDN 配置

- `config/juejin.yaml` - 掘金配置# 演练模式（查看计划但不发布）

- `config/zhihu.yaml` - 知乎配置python batch_publish.py --dry-run

- 等等...```



## 🛠️ 扩展开发**工作原理**：

- 循环处理每篇文章（如有10篇文章，循环10次）

基于 `BasePublisher` 抽象类可轻松添加新平台：- 每篇文章并发发布到多个平台（如6个平台同时发布）

- 使用线程池实现快速切换，比顺序发布快2-3倍

```python

from src.publisher.base_publisher import BasePublisher详细说明请查看：[批量发布使用指南](docs/BATCH_PUBLISH.md)



class NewPlatformPublisher(BasePublisher):### 文章格式要求

    def publish(self, article_path: str) -> bool:

        # 实现发布逻辑支持标准 Markdown 格式，可在文章开头添加 Front Matter 元数据：

        pass

``````markdown

---

详见：[开发文档](docs/DEVELOPMENT.md)title: 文章标题

description: 文章描述  

## 📚 文档tags: [Python, 自动化, 工具]

category: 技术分享

- [快速开始](docs/QUICKSTART.md)cover: https://example.com/cover.jpg

- [安装指南](docs/INSTALLATION.md)---

- [使用指南](docs/USAGE.md)

- [批量发布](docs/BATCH_PUBLISH.md)# 文章正文

- [内容生成](docs/CONTENT_GENERATION.md)

- [开发指南](docs/DEVELOPMENT.md)你的 Markdown 内容...

```

## ❓ 常见问题

### 平台特定配置

**Q: 登录过期怎么办？**

```bash每个平台都有独立的配置文件，支持个性化设置：

rm data/cookies/平台名_cookies.pkl

python publish.py  # 重新登录- `config/csdn.yaml` - CSDN 相关配置

```- `config/juejin.yaml` - 掘金相关配置  

- `config/zhihu.yaml` - 知乎相关配置

**Q: Chrome 调试模式有什么用？**  - 等等...

保持登录状态，避免反爬虫，支持手动干预（如验证码）。

## ⚙️ 配置说明

**Q: 支持 Windows 吗？**  

完全支持，需要调整 Chrome 启动命令路径。### 通用配置 (`config/common.yaml`)



更多问题：[文档](docs/)```yaml

# 文章目录配置

## 🤝 贡献content_dir: /path/to/your/articles/



欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)# Chrome 调试配置

debugger_address: 127.0.0.1:9222

## 📄 许可证

# 发布模式

MIT License - 详见 [LICENSE](LICENSE)auto_publish: false  # true=自动发布, false=需确认



## 📮 联系# 平台开关

enable:

- Issue: [GitHub Issues](../../issues)  csdn: true

- 文档: [docs/](docs/)  juejin: true

  zhihu: true

---  cto51: true

  alicloud: true

**让博客发布变得简单而高效！** 🎉  toutiao: false

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

### v2.1.0 (2025-11-08)

- 🍪 **Cookies 管理优化**：每个平台独立存储 cookies，避免冲突
- 🔄 **自动同步机制**：实时更新 cookies，减少重复登录
- 🛠️ **管理工具**：新增 cookies 管理脚本，支持备份、恢复、清理等操作
- 📋 详细文档：[Cookies 优化文档](docs/COOKIES_OPTIMIZATION.md)

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

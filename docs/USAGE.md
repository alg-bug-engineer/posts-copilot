# 使用指南

## 基本使用流程

### 1. 准备文章

将 Markdown 文章放在配置的 `content_dir` 目录中。支持以下格式：

#### 标准 Markdown 格式
```markdown
# 文章标题

文章内容...
```

#### 带 Front Matter 的 Markdown（推荐）
```markdown
---
title: Python 自动化测试最佳实践
description: 本文介绍Python自动化测试的核心概念、工具选择和最佳实践
tags: 
  - Python
  - 自动化测试
  - 单元测试
category: 技术分享
cover: https://example.com/cover.jpg
author: 你的名字
date: 2025-11-06
---

# Python 自动化测试最佳实践

在现代软件开发中，自动化测试已经成为保证代码质量的重要手段...
```

#### Front Matter 支持的字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `title` | 文章标题 | `Python 自动化测试` |
| `description` | 文章描述/摘要 | `介绍自动化测试最佳实践` |
| `tags` | 标签列表 | `[Python, 测试, 自动化]` |
| `category` | 分类 | `技术分享` |
| `cover` | 封面图片URL | `https://example.com/cover.jpg` |
| `author` | 作者 | `张三` |
| `date` | 发布日期 | `2025-11-06` |

### 2. 启动 Chrome 调试模式

#### 使用脚本启动（推荐）
```bash
./scripts/start_chrome.sh
```

#### 手动启动
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

### 3. 运行发布程序

```bash
python publish.py
```

### 4. 发布流程

#### 4.1 选择文章
程序会列出所有可发布的文章：
```
请选择要发布的文章：
====================================================
0. Python自动化测试最佳实践.md
1. AI大模型应用开发指南.md 👈 上次发布
2. React Hooks 深度解析.md
====================================================
请输入文章编号：
```

输入对应编号选择文章。

#### 4.2 选择平台
```
请选择发布平台：
====================================================
0. 发布到所有启用的平台
1. CSDN
2. 掘金  
3. 知乎
4. 51CTO
5. 阿里云开发者社区
6. 今日头条
7. 微信公众号
====================================================
请输入平台编号：
```

#### 4.3 首次登录
- 如果是首次使用某平台，程序会打开该平台的编辑页面
- **手动登录**该平台（用户名密码、扫码等）
- 登录完成后，在终端按回车继续
- 程序会自动保存登录状态，下次无需重复登录

#### 4.4 自动发布
程序会自动执行：
1. ✅ 检测登录状态
2. ✅ 填充文章标题
3. ✅ 填充文章内容  
4. ✅ 设置标签和分类
5. ✅ 上传封面图（如有）
6. ✅ 发布文章

### 5. 查看结果
发布完成后会显示结果：
```
============================================================
发布完成！成功：3，失败：0
============================================================
✅ CSDN 发布成功！
✅ 掘金 发布成功！  
✅ 知乎 发布成功！
```

## 高级用法

### 批量发布

#### 自动发布到所有平台
1. 设置配置文件：
   ```yaml
   # config/common.yaml
   auto_publish: true
   ```

2. 运行程序选择"发布到所有启用的平台"

#### 脚本化发布
```bash
# 发布指定文章到所有平台
python publish.py --article "Python自动化测试.md" --platforms all

# 发布到指定平台
python publish.py --article "React Hooks.md" --platforms csdn,juejin
```

### 配置优化

#### 平台个性化配置
为不同平台创建专门的配置：

```yaml
# config/csdn.yaml
default_tags: [Python, 后端开发, 编程技巧]
default_category: 技术文章
auto_publish: false
visibility: 全部可见

# config/juejin.yaml  
default_tags: [JavaScript, 前端, Vue]
default_category: 前端
auto_publish: true
```

#### 文章目录管理
```yaml
# config/common.yaml
content_dir: /Users/yourname/blog/articles/
backup_dir: /Users/yourname/blog/backup/   # 发布后备份
```

### AI 内容生成

#### 启用 AI 生成功能
```bash
# 安装额外依赖
pip install zhipuai

# 配置 API Key
export ZHIPU_API_KEY="your_api_key_here"

# 生成并发布文章
python generate/zhipu_content_generator.py
```

#### AI 生成流程
1. 搜索热点新闻
2. 基于新闻生成技术文章
3. 自动保存到文章目录
4. 可选择立即发布

## 平台特性说明

### CSDN
- ✅ 支持标签、分类
- ✅ 支持封面图
- ✅ 支持可见性设置
- ⚠️ 需要实名认证

### 掘金
- ✅ 支持标签、专栏
- ✅ 支持封面图
- ✅ 支持草稿/发布
- 💡 推荐使用优质标签

### 知乎
- ✅ 支持话题标签
- ✅ 支持专栏发布
- ✅ 支持封面图
- ⚠️ 内容质量要求较高

### 51CTO  
- ✅ 支持分类、标签
- ✅ 技术内容友好
- 💡 适合技术深度文章

### 阿里云开发者社区
- ✅ 支持标签、分类
- ✅ 支持社区投稿
- 💡 云计算相关内容推荐

### 今日头条
- ✅ 支持标签
- ✅ 支持封面图
- 💡 适合科普技术文章

### 微信公众号
- ✅ 保存为草稿
- ⚠️ 需要手动发布
- 💡 支持富文本编辑

## 最佳实践

### 文章写作建议

1. **标题优化**
   - 包含关键词
   - 控制在20字以内
   - 避免特殊符号

2. **内容结构**
   ```markdown
   # 标题
   
   ## 概述
   简要介绍文章内容
   
   ## 核心内容  
   详细展开技术点
   
   ## 实践案例
   提供具体例子
   
   ## 总结
   总结要点和收获
   ```

3. **标签选择**
   - 每篇文章 3-5 个标签
   - 选择热门相关标签
   - 避免过于宽泛的标签

### 发布策略

1. **时间安排**
   - 工作日上午 9-11 点
   - 下午 2-4 点
   - 避开节假日

2. **平台选择**
   - 技术深度文章：CSDN、51CTO
   - 前端内容：掘金
   - 通用技术：知乎、阿里云
   - 科普内容：今日头条

3. **频率控制**
   - 每个平台每天不超过 2 篇
   - 保持内容质量
   - 避免批量发布

## 故障排除

### 发布失败处理

1. **查看日志**
   ```bash
   tail -f data/logs/publisher.log
   ```

2. **常见错误**
   - **登录失效**：删除 cookie 重新登录
   - **元素定位失败**：平台页面更新，等待程序更新
   - **内容过长**：检查平台字数限制
   - **标签不存在**：使用平台已有标签

3. **重试机制**
   - 程序内置重试机制
   - 失败后可单独重试该平台
   - 查看错误信息针对性处理

### 获取帮助

- 📖 查看详细文档：[docs/](https://github.com/your-username/posts-copilot/tree/main/docs)
- 🐛 报告问题：[Issues](https://github.com/your-username/posts-copilot/issues)
- 💬 参与讨论：[Discussions](https://github.com/your-username/posts-copilot/discussions)
- 📧 联系作者：your-email@example.com
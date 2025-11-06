# 更新日志

本文档记录了 Posts Copilot 项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [未发布]

### 新增
- 📖 完善的项目文档和README
- 🔧 标准化的配置文件结构
- 📋 GitHub标准文件（LICENSE、CONTRIBUTING.md、.gitignore）
- 🏗️ 规范的项目架构文档

### 优化
- 📚 重新整理docs目录结构
- ⚙️ 优化requirements.txt依赖管理
- 🎨 改进README展示效果和内容结构

## [2.0.0] - 2025-11-06

### 新增
- 🌟 阿里云开发者社区平台支持
- 🤖 智谱AI内容生成功能
- 📰 热点新闻搜索和分析
- 🔄 自动重试机制
- 📊 详细的发布日志系统

### 优化
- 🏗️ 重构发布器架构，提高可扩展性
- 🔐 改进登录状态管理
- 📝 增强Markdown解析能力
- ⚡ 提升发布成功率和稳定性

### 修复
- 🐛 修复知乎平台元素定位问题
- 🐛 解决CSDN标签设置异常
- 🐛 修复51CTO发布流程错误

## [1.5.0] - 2025-10-15

### 新增
- 📱 微信公众号平台支持（草稿模式）
- 🏷️ 今日头条平台支持
- 🔧 平台配置文件系统
- 📋 Front Matter元数据支持

### 优化
- 🎯 改进文章选择界面
- 📈 增加发布统计功能
- 🔄 优化Cookie管理机制

## [1.0.0] - 2025-09-20

### 新增
- 🎯 CSDN平台发布支持
- 🎯 掘金平台发布支持  
- 🎯 知乎专栏发布支持
- 🎯 51CTO博客发布支持
- 🤖 Chrome自动化发布
- 🔐 登录状态自动管理
- 📝 Markdown文章解析
- 📊 基础日志系统
- ⚙️ 配置文件管理

### 架构
- 🏗️ 基于Selenium的自动化框架
- 🧩 抽象发布器基类设计
- 📁 模块化项目结构
- 🔧 YAML配置系统

## 版本说明

### 版本号规则
我们使用语义化版本号 `MAJOR.MINOR.PATCH`：

- **MAJOR**：不兼容的API修改
- **MINOR**：向后兼容的功能性新增
- **PATCH**：向后兼容的问题修正

### 变更类型
- `新增` - 新功能
- `优化` - 对现有功能的改进
- `修复` - Bug修复
- `废弃` - 即将删除的功能
- `移除` - 已删除的功能
- `安全` - 安全性修复

### 发布周期
- **主版本**：重大架构变更，不定期发布
- **次版本**：新功能发布，每1-2月发布
- **修订版本**：Bug修复，按需发布

### 兼容性
- 1.x 版本内保持向后兼容
- 2.x 版本可能包含不兼容变更
- 配置文件格式尽量保持兼容

## 升级指南

### 从 1.x 升级到 2.x
1. 备份现有配置文件
2. 查看新版本配置文件模板
3. 迁移配置到新格式
4. 测试发布功能

### 配置文件迁移
详见 [升级指南](docs/UPGRADE.md)

## 贡献者

感谢所有为项目做出贡献的开发者！

### 核心贡献者
- [@your-username](https://github.com/your-username) - 项目创始人和主要维护者

### 功能贡献
- 阿里云平台支持：[@contributor1](https://github.com/contributor1)
- AI内容生成：[@contributor2](https://github.com/contributor2)
- 微信公众号支持：[@contributor3](https://github.com/contributor3)

### 文档贡献
- 安装指南完善：[@doc-contributor1](https://github.com/doc-contributor1)
- 开发文档：[@doc-contributor2](https://github.com/doc-contributor2)

### Bug修复
- 知乎登录问题：[@bug-fixer1](https://github.com/bug-fixer1)
- CSDN标签错误：[@bug-fixer2](https://github.com/bug-fixer2)

完整的贡献者列表请查看 [GitHub Contributors](https://github.com/your-username/posts-copilot/graphs/contributors)

---

📝 **注意**：如果您发现任何问题或有功能建议，请在 [GitHub Issues](https://github.com/your-username/posts-copilot/issues) 中提出。

🙏 **感谢**：感谢所有用户和贡献者对项目的支持！
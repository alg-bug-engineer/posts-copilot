# 教程系列自动生成系统

> 基于 Kimi API 的智能教程自动生成系统，能够自动探索技术主题、规划教程体系、生成高质量技术文章

## ✨ 特性

- 🔍 **智能主题探索**：深度挖掘技术方向，自动发现值得讲解的知识点
- 📖 **体系化大纲生成**：自动规划循序渐进、逻辑清晰的教程体系
- ✍️ **深度文章写作**：联网搜索最新资料，生成专业级技术文章
- 🎯 **完整自动化流程**：从主题探索到文章发布，一键完成
- 💾 **数据持久化**：主题库、大纲库、生成历史全程记录
- 📝 **Frontmatter 支持**：生成的文章带有完整的元数据，适配主流博客系统

## 🏗️ 系统架构

```
主题探索 → 大纲生成 → 文章写作 → 输出发布
    ↓           ↓          ↓
topics_db  curriculum_db  posts/
```

### 三大核心模块

1. **Topic Explorer** (主题探索器)
   - 深度分析技术领域
   - 发现子主题和知识点
   - 评估难度和学习价值

2. **Curriculum Generator** (大纲生成器)
   - 组织子主题成教程体系
   - 规划学习路径
   - 生成章节大纲

3. **Article Generator** (文章生成器)
   - 联网搜索最新资料
   - 深度研究技术细节
   - 生成专业技术文章

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install openai httpx pyyaml

# 设置 API Key
export MOONSHOT_API_KEY='your-api-key-here'
```

### 2. 配置文件

编辑 `tutorial_config.yaml` 调整参数（可选）：

```yaml
# 主题探索配置
topic_exploration:
  exploration_depth: 10  # 探索的子主题数量

# 教程大纲配置
curriculum_generation:
  min_chapters: 5
  max_chapters: 15

# 文章生成配置
article_generation:
  max_search_rounds: 12
  min_word_count: 3000
```

### 3. 使用方式

#### 方式一：快速启动脚本

```bash
# 赋予执行权限
chmod +x start_tutorial_generator.sh

# 完整流程生成（探索 -> 大纲 -> 文章）
./start_tutorial_generator.sh -t "强化学习" --full

# 只生成前3章
./start_tutorial_generator.sh -t "强化学习" --full -r 1-3

# 交互模式
./start_tutorial_generator.sh
```

#### 方式二：直接运行 Python

```bash
# 完整流程
python tutorial_auto_generator.py -t "Vision Language Action Model" --full

# 仅探索主题
python tutorial_auto_generator.py -t "VLA模型" --explore-only

# 仅生成大纲
python tutorial_auto_generator.py -t "强化学习" --curriculum-only

# 仅生成指定章节的文章
python tutorial_auto_generator.py -t "强化学习" --articles-only -r 1-5

# 查看系统状态
python tutorial_auto_generator.py --status
```

#### 方式三：单独使用各模块

```bash
# 探索主题
python topic_explorer.py -t "深度强化学习"

# 批量探索
python topic_explorer.py -b topics.txt

# 生成大纲
python curriculum_generator.py -t "深度强化学习"

# 生成单篇文章
python article_generator.py -t "深度强化学习" -n 1

# 批量生成
python article_generator.py -t "深度强化学习" -r 1-5
```

## 📂 数据存储

系统会自动创建以下数据文件：

```
data/generated/
├── topics_database.json          # 主题库
├── curriculum_database.json      # 大纲库
└── tutorial_generation_history.json  # 生成历史

posts/
├── 强化学习_第1章_*.md
├── 强化学习_第2章_*.md
└── ...
```

### 主题库结构示例

```json
{
  "topics": [
    {
      "main_topic": "强化学习",
      "description": "...",
      "difficulty_level": "intermediate",
      "subtopics": [
        {
          "title": "马尔可夫决策过程",
          "description": "...",
          "difficulty": "beginner",
          "learning_objectives": [...]
        }
      ]
    }
  ]
}
```

### 文章 Frontmatter 示例

```markdown
---
title: 马尔可夫决策过程详解
date: 2025-01-10
description: 深入理解强化学习的数学基础
tags:
  - 强化学习
  - MDP
  - 机器学习
series: 深度强化学习完全指南
chapter: 1
difficulty: beginner
estimated_reading_time: 15
---

# 文章内容...
```

## 🎯 使用场景

### 场景1：建立技术博客系列

```bash
# 探索一个大主题
python tutorial_auto_generator.py -t "Transformer架构" --full

# 系统会自动：
# 1. 发现子主题（注意力机制、位置编码、多头注意力等）
# 2. 规划教程体系（10-15章）
# 3. 生成所有文章
```

### 场景2：深入学习某个技术

```bash
# 先探索主题，了解知识体系
python topic_explorer.py -t "Vision Language Action Model"

# 查看生成的子主题列表
python topic_explorer.py -l

# 生成教程大纲
python curriculum_generator.py -t "Vision Language Action Model"

# 根据需要生成特定章节
python article_generator.py -t "Vision Language Action Model" -n 1
```

### 场景3：批量生成教程

```bash
# 准备主题列表文件 topics.txt
# 内容：
# 强化学习
# Transformer
# 扩散模型

# 批量探索
python topic_explorer.py -b topics.txt

# 然后逐个生成教程...
```

## ⚙️ 配置说明

### 重要配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `topic_exploration.exploration_depth` | 探索的子主题数量 | 10 |
| `curriculum_generation.min_chapters` | 最少章节数 | 5 |
| `curriculum_generation.max_chapters` | 最多章节数 | 15 |
| `article_generation.max_search_rounds` | 每篇文章的搜索轮数 | 12 |
| `article_generation.min_word_count` | 文章最少字数 | 3000 |
| `storage.articles_output` | 文章输出目录 | ../posts |

### API 配置

系统使用 Kimi API，需要设置环境变量：

```bash
export MOONSHOT_API_KEY='your-api-key'
export MOONSHOT_BASE_URL='https://api.moonshot.cn/v1'  # 可选
```

## 📊 工作流程详解

### 完整流程示例

假设我们要生成"Vision Language Action Model"的教程系列：

```bash
python tutorial_auto_generator.py -t "Vision Language Action Model" --full
```

#### 阶段1：主题探索（约1-2分钟）

```
🔍 开始探索主题: Vision Language Action Model
✓ 探索完成！
  发现 10 个子主题
  难度级别: advanced
  
📚 子主题列表:
  1. VLA模型基础架构 (beginner)
  2. Vision Encoder设计 (intermediate)
  3. Language-Action对齐机制 (advanced)
  ...
```

#### 阶段2：大纲生成（约1-2分钟）

```
📖 生成教程大纲: Vision Language Action Model
✓ 大纲生成完成！
  教程名称: Vision Language Action Model 完全指南
  章节数量: 12
  预计时间: 180分钟
  
📚 章节列表:
  第1章: VLA模型概述 [beginner]
  第2章: Vision Encoder架构详解 [intermediate]
  ...
```

#### 阶段3：文章生成（每章约3-5分钟）

```
✍️  生成文章
   主题: Vision Language Action Model
   章节: 第1章

【阶段 1/2】📚 信息收集
>>> 第 1/12 轮
🔍 调用 1 个工具
   搜索: VLA模型是什么 基本概念
     ✓ 搜索完成
...

【阶段 2/2】✍️  文章写作
📊 已收集 8 条搜索结果
🎯 正在生成文章...
✓ 文章生成完成

✅ 文章生成完成！
   文件: ../posts/Vision_Language_Action_Model_第1章_VLA模型概述.md
   字数: 4,523
   搜索次数: 8
```

## 🔧 故障排查

### 问题1：API Key 错误

```bash
ValueError: MOONSHOT_API_KEY 环境变量未设置
```

**解决**：设置环境变量
```bash
export MOONSHOT_API_KEY='your-api-key'
```

### 问题2：主题未找到

```bash
ValueError: 主题 'XXX' 未找到
```

**解决**：先探索主题
```bash
python topic_explorer.py -t "XXX"
```

### 问题3：JSON 解析错误

这通常是 API 返回格式问题，系统会自动重试。如果持续失败，检查：
- API Key 是否有效
- 网络连接是否正常
- 是否超出 API 配额

### 问题4：生成的文章质量不理想

调整配置：
- 增加 `max_search_rounds`（更多搜索）
- 调整 `search_temperature` 和 `writing_temperature`
- 修改 `prompts/expert_narrator.txt` 提示词

## 💡 高级技巧

### 1. 自定义提示词

编辑 `prompts/expert_narrator.txt` 来调整写作风格：

```
你是一位资深的技术专家...

讲解风格：
1. 更加通俗易懂
2. 多用实际案例
3. 代码示例清晰
...
```

### 2. 批量自动化

创建批量任务脚本：

```bash
#!/bin/bash
topics=("强化学习" "Transformer" "扩散模型")

for topic in "${topics[@]}"; do
    python tutorial_auto_generator.py -t "$topic" --full -r 1-3
    sleep 60  # 避免API限流
done
```

### 3. 定时任务

使用 cron 实现定时生成：

```bash
# 每天凌晨3点生成一个教程
0 3 * * * cd /path/to/project && ./start_tutorial_generator.sh -t "$(cat next_topic.txt)" --full
```

## 📈 性能与成本

### 时间估算

- 主题探索：1-2分钟
- 大纲生成：1-2分钟
- 单篇文章：3-5分钟

**完整12章教程**：约40-70分钟

### API 成本估算

基于 Kimi API 定价：

- 主题探索：~5万 tokens
- 大纲生成：~5万 tokens
- 单篇文章：~15万 tokens（含搜索）

**12章教程总计**：~190万 tokens

## 🛣️ 未来规划

- [ ] 支持图表自动生成（Mermaid、代码流程图）
- [ ] 集成代码示例验证（自动运行测试）
- [ ] 多语言支持（英文、日文等）
- [ ] Web UI 界面
- [ ] 文章质量评分系统
- [ ] 自动发布到多个平台（Medium、Dev.to等）

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请提交 Issue。

---

**Enjoy automated tutorial generation! 🎉**

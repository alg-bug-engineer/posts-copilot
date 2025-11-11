# Kimi 内容自动生成系统# AI 信息挖掘助手



基于 Kimi API 的专业技术内容自动生成系统，实现从主题探索到文章发布的完整自动化流程。基于 Kimi 模型的智能研究工具，能够自动搜索、学习和生成高质量的技术讲解文章。



## ✨ 核心特性## 功能特点



### 🔍 智能主题探索### 🔍 智能信息收集

- 深度分析技术主题，发现值得讲解的子主题- 自动调用 Kimi 的联网搜索工具

- 自动评估主题难度和学习价值- 从多个角度收集全面信息

- 构建完整的知识图谱- 支持最多 15 轮迭代搜索

- 自动去重和信息整合

### 📖 教程大纲生成

- 循序渐进的课程体系设计### ✍️ 专家级内容生成

- 合理的难度梯度安排- 使用资深专家语气讲解

- 明确的学习目标和内容规划- 深入浅出，通俗易懂

- 结构化的 Markdown 输出

### ✍️ 专业文章写作- 包含案例、对比、趋势分析

- 15 年经验的 AI 专家视角

- 深入浅出的专业讲解### 🛠️ 强大的工具集成

- 自动生成带 Frontmatter 的 Markdown 文章- 集成 Kimi 官方工具（日期、网络搜索等）

- 文件名即博客标题，便于直接发布- 支持自定义工具扩展

- 完整的工具调用日志

### 🔧 完整的自动化流程

- 一键完成探索 → 大纲 → 文章的全流程### 📊 批量研究支持

- 支持批量生成系列教程- 支持批量处理多个主题

- 智能去重，避免重复工作- 自动保存研究历史

- 可配置的输出格式

## 📦 安装

## 安装

### 1. 安装依赖

### 1. 安装依赖

```bash

cd kimi```bash

pip install openai httpx pyyamlpip install -r requirements.txt

``````



### 2. 设置 API 密钥主要依赖：

- `openai` - OpenAI Python SDK

```bash- `httpx` - HTTP 客户端

export MOONSHOT_API_KEY="your-moonshot-api-key"- `pyyaml` - YAML 配置文件支持

```

### 2. 设置 API 密钥

建议将上述命令添加到 `~/.zshrc` 或 `~/.bashrc` 中，以便永久生效。

```bash

## 🚀 快速开始export MOONSHOT_API_KEY="your-api-key-here"

```

### 方式一：交互式启动（推荐）

或者在 `.env` 文件中设置：

```bash

./run.sh```

```MOONSHOT_API_KEY=your-api-key-here

MOONSHOT_BASE_URL=https://api.moonshot.cn/v1

启动后会显示交互式菜单，按提示操作即可。```



### 方式二：命令行直接使用## 使用方法



#### 完整流水线（探索 + 大纲 + 文章）### 方式 1: 交互模式（推荐新手）



```bash```bash

# 生成完整教程系列cd kimi

python3 main.py --full "Transformer架构"python research_assistant.py

```

# 只生成前 3 章

python3 main.py --full "Transformer架构" --range 1-3然后根据提示输入研究主题。



# 跳过探索和大纲生成（如果已存在）### 方式 2: 直接指定主题

python3 main.py --full "Transformer架构" --skip-explore --skip-curriculum

``````bash

python research_assistant_v2.py -t "大语言模型的发展历程"

#### 分步执行```



```bash### 方式 3: 批量研究

# 1. 探索主题

python3 main.py --explore "Vision Language Action Model"创建一个主题列表文件 `topics.txt`：



# 2. 生成教程大纲```

python3 main.py --curriculum "Vision Language Action Model"大语言模型的发展历程

AI Agent 技术详解

# 3. 生成单篇文章Transformer 架构原理

python3 main.py --article "Vision Language Action Model" --chapter 1```



# 4. 批量生成文章（大纲已存在）然后运行：

python3 main.py --series "Vision Language Action Model" --range 1-5

``````bash

python research_assistant_v2.py -b topics.txt

#### 查看和管理```



```bash### 方式 4: 使用自定义配置

# 列出所有已探索的主题和大纲

python3 main.py --list```bash

python research_assistant_v2.py -c my_config.yaml -t "AI 技术"

# 查看指定主题的详细大纲```

python3 main.py --show "Transformer架构"

```## 配置说明



## 📁 目录结构配置文件 `config.yaml` 包含以下设置：



```### 研究配置

kimi/

├── main.py                      # 统一入口脚本```yaml

├── run.sh                       # 交互式启动脚本research:

├── tutorial_config.yaml         # 配置文件  max_iterations: 15  # 最大搜索轮数

├── topic_explorer.py            # 主题探索模块```

├── curriculum_generator.py      # 大纲生成模块

├── article_generator.py         # 文章生成模块### 内容生成配置

├── TUTORIAL_GENERATOR_README.md # 技术文档

├── prompts/```yaml

│   └── expert_narrator.txt     # 专家提示词模板generation:

└── data/  model: "kimi-k2-thinking"      # 使用的模型

    ├── topics_database.json    # 主题数据库  search_temperature: 0.7         # 搜索阶段温度（较低更准确）

    ├── curriculum_database.json # 大纲数据库  expert_temperature: 0.8         # 生成阶段温度（较高更有创意）

    ├── tutorial_generation_history.json # 生成历史  max_tokens: 32768              # 最大 token 数

    └── articles/               # 生成的文章输出目录```

```

### 输出配置

## ⚙️ 配置说明

```yaml

编辑 `tutorial_config.yaml` 可自定义：output:

  directory: "../posts"           # 输出目录

- **主题探索深度**：发现多少个子主题  show_full_content: false        # 是否在控制台显示完整内容

- **教程章节数量**：最少/最多章节数  preview_length: 500             # 预览长度

- **文章生成参数**：模型、温度、搜索轮数等```

- **输出格式**：字数范围、引用格式等

### 日志配置

## 📝 输出格式

```yaml

生成的文章包含完整的 Frontmatter：logging:

  show_reasoning: true            # 是否显示 AI 思考过程

```markdown  reasoning_length: 200           # 思考过程显示长度

---  save_search_history: true       # 是否保存搜索历史

title: "文章标题"```

date: "2025-01-15"

author: "AI技术专家"## 输出示例

categories: ["AI", "深度学习", "Transformer"]

tags: ["注意力机制", "自注意力", "多头注意力"]研究完成后，会在 `posts/` 目录下生成 Markdown 文件：

description: "本文深入讲解 Transformer 的核心机制..."

series: "Transformer架构深度解析"```

chapter: 1posts/

difficulty: "intermediate"  ├── 大语言模型的发展历程_20250107_143022.md

estimated_reading_time: "15分钟"  ├── AI_Agent技术详解_20250107_144530.md

---  └── ...

```

# 文章正文

文件包含：

...- 标题和元信息

```- 完整的专家级讲解

- 结构化的 Markdown 格式

**文件名即标题**：生成的文件名直接使用章节标题，便于作为博客标题发布。- 参考资料（如果有）



## 🎯 工作流程## 工作流程



``````

主题输入┌─────────────────┐

   ↓│  用户输入主题   │

【阶段 1】主题探索└────────┬────────┘

   ├─ 分析技术领域         │

   ├─ 发现子主题         ▼

   └─ 评估学习价值┌─────────────────┐

   ↓│ 阶段1：信息收集 │

【阶段 2】大纲生成│                 │

   ├─ 设计课程体系│ • 多轮联网搜索 │

   ├─ 安排难度梯度│ • 收集不同角度 │

   └─ 规划学习目标│ • 整理结构化   │

   ↓└────────┬────────┘

【阶段 3】文章生成         │

   ├─ 深度信息搜索（12 轮）         ▼

   ├─ 专家视角写作┌─────────────────┐

   ├─ 添加 Frontmatter│ 阶段2：内容生成 │

   └─ 输出 Markdown 文件│                 │

```│ • 使用专家提示词│

│ • 深度讲解     │

## 💡 使用技巧│ • 输出Markdown │

└────────┬────────┘

### 1. 高效生成策略         │

         ▼

- **首次使用**：完整流程 `--full`，让系统自动完成所有步骤┌─────────────────┐

- **增量生成**：使用 `--skip-explore` 和 `--skip-curriculum` 跳过已完成的步骤│  保存到文件     │

- **批量生成**：一次生成 3-5 章为佳，避免请求过于密集└─────────────────┘

```

### 2. 主题命名建议

## 版本说明

- 使用清晰、具体的主题名称

- 推荐格式：`技术名称 + 具体方向`### `research_assistant.py` - 基础版

- 示例：- 简单易用

  - ✅ "Transformer架构"- 适合快速上手

  - ✅ "强化学习基础算法"- 核心功能完整

  - ✅ "Vision Language Action Model"

  - ❌ "AI"（太宽泛）### `research_assistant_v2.py` - 增强版

  - ❌ "学习笔记"（不具体）- 支持配置文件

- 命令行参数

### 3. 质量控制- 批量研究

- 更详细的日志

- 生成后检查 Frontmatter 的分类和标签是否准确- 搜索历史记录

- 根据需要手动调整标题和描述

- 文章内容通常无需修改，系统生成的质量已很高## 提示词定制



## 🔧 高级用法你可以编辑 `prompts/expert_narrator.txt` 来定制专家讲解的风格：



### 自定义提示词```

你是一位在 AI/大模型领域有 15 年研究经验的资深专家...

编辑 `prompts/expert_narrator.txt` 可自定义写作风格和要求。

你的讲解风格：

### 修改配置1. 像朋友聊天一样自然，不说官话套话

2. 善用比喻和现实案例...

```yaml```

# tutorial_config.yaml

## 搜索历史

# 探索深度

topic_exploration:所有搜索记录会保存在 `data/generated/search_history.json`：

  exploration_depth: 10  # 子主题数量

```json

# 大纲配置[

curriculum_generation:  {

  min_chapters: 5       # 最少章节    "topic": "大语言模型的发展历程",

  max_chapters: 15      # 最多章节    "timestamp": "2025-01-07T14:30:22",

    "search_count": 7,

# 文章生成    "searches": [...]

article_generation:  }

  model: "kimi-k2-thinking"  # 使用的模型]

  max_search_rounds: 12      # 搜索轮数```

  search_temperature: 0.7    # 搜索温度

  writing_temperature: 0.8   # 写作温度## 高级用法

  min_word_count: 3000       # 最少字数

  max_word_count: 8000       # 最多字数### 1. 静默模式

```

只显示关键信息，适合批量处理：

## 📊 数据管理

```bash

### 数据库文件python research_assistant_v2.py -q -t "AI 技术"

```

- `topics_database.json`：存储所有探索的主题

- `curriculum_database.json`：存储生成的教程大纲### 2. 自定义搜索策略

- `tutorial_generation_history.json`：记录文章生成历史

在配置文件中定义搜索策略：

### 清理数据

```yaml

如需重新探索或生成，可手动编辑或删除对应的数据库文件。research:

  search_strategy:

## 🆘 常见问题    - "基本概念和定义"

    - "技术原理和实现"

### Q: 提示 API 密钥未设置？    - "发展历程和里程碑"

    - "实际应用和案例"

**A**: 执行 `export MOONSHOT_API_KEY="your-key"` 或在启动脚本中输入。    - "行业影响和趋势"

    - "挑战和未来展望"

### Q: 生成的文章在哪里？```



**A**: 默认位置 `kimi/data/articles/`，可在配置文件中修改。### 3. 集成到工作流



### Q: 如何跳过已完成的步骤？```python

from research_assistant_v2 import EnhancedResearchAssistant

**A**: 使用 `--skip-explore` 和 `--skip-curriculum` 参数。

# 创建助手

### Q: 生成失败怎么办？assistant = EnhancedResearchAssistant()



**A**: 检查网络连接和 API 配额，可以从失败的章节继续生成。# 研究主题

content = assistant.research("AI Agent 技术", verbose=False)

### Q: 可以自定义输出格式吗？

# 使用生成的内容

**A**: 可以，编辑 `article_generator.py` 中的 `_generate_frontmatter()` 和 `_compose_article()` 方法。print(content)



## 📄 许可证# 关闭

assistant.close()

本项目遵循 MIT 许可证。```



## 🤝 贡献## 常见问题



欢迎提交 Issue 和 Pull Request！### Q: 搜索结果不够全面怎么办？



## 🔗 相关链接A: 可以增加 `max_iterations` 配置值，允许更多轮搜索。



- [Kimi API 文档](https://platform.moonshot.cn/docs)### Q: 生成的内容太长或太短？

- [项目完整文档](./TUTORIAL_GENERATOR_README.md)

A: 调整 `max_tokens` 和 `expert_temperature` 参数。

### Q: 如何改变输出风格？

A: 编辑 `prompts/expert_narrator.txt` 提示词文件。

### Q: API 调用失败？

A: 检查：
1. API 密钥是否正确设置
2. 网络连接是否正常
3. API 额度是否充足

## 最佳实践

1. **主题选择**：选择具体、明确的主题，避免过于宽泛
2. **等待时间**：批量研究时建议设置间隔，避免请求过快
3. **定期清理**：定期清理 `posts/` 目录和搜索历史
4. **提示词优化**：根据需求定制 expert_narrator.txt
5. **配置备份**：保存好的配置文件以便复用

## 路线图

- [ ] 支持更多 Kimi 工具（图片生成、代码执行等）
- [ ] 添加 Web UI 界面
- [ ] 支持导出为 PDF、Word 等格式
- [ ] 集成图表生成功能
- [ ] 支持多语言输出
- [ ] 添加内容质量评估

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue。

---

**享受智能研究的乐趣！🚀**

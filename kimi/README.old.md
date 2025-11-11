# AI 信息挖掘助手

基于 Kimi 模型的智能研究工具，能够自动搜索、学习和生成高质量的技术讲解文章。

## 功能特点

### 🔍 智能信息收集
- 自动调用 Kimi 的联网搜索工具
- 从多个角度收集全面信息
- 支持最多 15 轮迭代搜索
- 自动去重和信息整合

### ✍️ 专家级内容生成
- 使用资深专家语气讲解
- 深入浅出，通俗易懂
- 结构化的 Markdown 输出
- 包含案例、对比、趋势分析

### 🛠️ 强大的工具集成
- 集成 Kimi 官方工具（日期、网络搜索等）
- 支持自定义工具扩展
- 完整的工具调用日志

### 📊 批量研究支持
- 支持批量处理多个主题
- 自动保存研究历史
- 可配置的输出格式

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `openai` - OpenAI Python SDK
- `httpx` - HTTP 客户端
- `pyyaml` - YAML 配置文件支持

### 2. 设置 API 密钥

```bash
export MOONSHOT_API_KEY="your-api-key-here"
```

或者在 `.env` 文件中设置：

```
MOONSHOT_API_KEY=your-api-key-here
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1
```

## 使用方法

### 方式 1: 交互模式（推荐新手）

```bash
cd kimi
python research_assistant.py
```

然后根据提示输入研究主题。

### 方式 2: 直接指定主题

```bash
python research_assistant_v2.py -t "大语言模型的发展历程"
```

### 方式 3: 批量研究

创建一个主题列表文件 `topics.txt`：

```
大语言模型的发展历程
AI Agent 技术详解
Transformer 架构原理
```

然后运行：

```bash
python research_assistant_v2.py -b topics.txt
```

### 方式 4: 使用自定义配置

```bash
python research_assistant_v2.py -c my_config.yaml -t "AI 技术"
```

## 配置说明

配置文件 `config.yaml` 包含以下设置：

### 研究配置

```yaml
research:
  max_iterations: 15  # 最大搜索轮数
```

### 内容生成配置

```yaml
generation:
  model: "kimi-k2-thinking"      # 使用的模型
  search_temperature: 0.7         # 搜索阶段温度（较低更准确）
  expert_temperature: 0.8         # 生成阶段温度（较高更有创意）
  max_tokens: 32768              # 最大 token 数
```

### 输出配置

```yaml
output:
  directory: "../posts"           # 输出目录
  show_full_content: false        # 是否在控制台显示完整内容
  preview_length: 500             # 预览长度
```

### 日志配置

```yaml
logging:
  show_reasoning: true            # 是否显示 AI 思考过程
  reasoning_length: 200           # 思考过程显示长度
  save_search_history: true       # 是否保存搜索历史
```

## 输出示例

研究完成后，会在 `posts/` 目录下生成 Markdown 文件：

```
posts/
  ├── 大语言模型的发展历程_20250107_143022.md
  ├── AI_Agent技术详解_20250107_144530.md
  └── ...
```

文件包含：
- 标题和元信息
- 完整的专家级讲解
- 结构化的 Markdown 格式
- 参考资料（如果有）

## 工作流程

```
┌─────────────────┐
│  用户输入主题   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 阶段1：信息收集 │
│                 │
│ • 多轮联网搜索 │
│ • 收集不同角度 │
│ • 整理结构化   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 阶段2：内容生成 │
│                 │
│ • 使用专家提示词│
│ • 深度讲解     │
│ • 输出Markdown │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  保存到文件     │
└─────────────────┘
```

## 版本说明

### `research_assistant.py` - 基础版
- 简单易用
- 适合快速上手
- 核心功能完整

### `research_assistant_v2.py` - 增强版
- 支持配置文件
- 命令行参数
- 批量研究
- 更详细的日志
- 搜索历史记录

## 提示词定制

你可以编辑 `prompts/expert_narrator.txt` 来定制专家讲解的风格：

```
你是一位在 AI/大模型领域有 15 年研究经验的资深专家...

你的讲解风格：
1. 像朋友聊天一样自然，不说官话套话
2. 善用比喻和现实案例...
```

## 搜索历史

所有搜索记录会保存在 `data/generated/search_history.json`：

```json
[
  {
    "topic": "大语言模型的发展历程",
    "timestamp": "2025-01-07T14:30:22",
    "search_count": 7,
    "searches": [...]
  }
]
```

## 高级用法

### 1. 静默模式

只显示关键信息，适合批量处理：

```bash
python research_assistant_v2.py -q -t "AI 技术"
```

### 2. 自定义搜索策略

在配置文件中定义搜索策略：

```yaml
research:
  search_strategy:
    - "基本概念和定义"
    - "技术原理和实现"
    - "发展历程和里程碑"
    - "实际应用和案例"
    - "行业影响和趋势"
    - "挑战和未来展望"
```

### 3. 集成到工作流

```python
from research_assistant_v2 import EnhancedResearchAssistant

# 创建助手
assistant = EnhancedResearchAssistant()

# 研究主题
content = assistant.research("AI Agent 技术", verbose=False)

# 使用生成的内容
print(content)

# 关闭
assistant.close()
```

## 常见问题

### Q: 搜索结果不够全面怎么办？

A: 可以增加 `max_iterations` 配置值，允许更多轮搜索。

### Q: 生成的内容太长或太短？

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

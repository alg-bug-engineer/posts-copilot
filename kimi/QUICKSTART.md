# Kimi 内容生成系统 - 快速开始指南

## 5 分钟上手

### 第一步：设置 API 密钥

```bash
export MOONSHOT_API_KEY="sk-your-api-key-here"
```

### 第二步：启动系统

```bash
cd kimi
./run.sh
```

### 第三步：选择模式并输入主题

系统会引导你完成后续操作。

---

## 常用命令速查

### 完整流程（推荐新手）

```bash
# 一键生成完整教程系列
python3 main.py --full "主题名称"

# 只生成前 5 章
python3 main.py --full "主题名称" --range 1-5
```

### 分步执行（适合精细控制）

```bash
# 步骤 1：探索主题
python3 main.py --explore "主题名称"

# 步骤 2：生成大纲
python3 main.py --curriculum "主题名称"

# 步骤 3：生成文章
python3 main.py --series "主题名称" --range 1-5
```

### 查看和管理

```bash
# 列出所有主题
python3 main.py --list

# 查看详细大纲
python3 main.py --show "主题名称"
```

---

## 典型使用场景

### 场景 1：生成一个新的教程系列

```bash
# 完整流程，生成所有章节
python3 main.py --full "深度学习优化算法"
```

### 场景 2：只生成部分章节

```bash
# 先探索和生成大纲
python3 main.py --explore "计算机视觉基础"
python3 main.py --curriculum "计算机视觉基础"

# 只生成前 3 章
python3 main.py --series "计算机视觉基础" --range 1-3

# 稍后继续生成 4-6 章
python3 main.py --series "计算机视觉基础" --range 4-6
```

### 场景 3：重新生成某一章

```bash
# 生成第 2 章
python3 main.py --article "主题名称" --chapter 2
```

### 场景 4：跳过已完成的步骤

```bash
# 主题已探索过，直接生成文章
python3 main.py --full "已探索的主题" --skip-explore --skip-curriculum
```

---

## 输出文件位置

```
kimi/data/articles/
└── 章节标题.md  # 生成的文章，文件名即标题
```

---

## 配置调整

编辑 `tutorial_config.yaml`：

```yaml
# 修改章节数量范围
curriculum_generation:
  min_chapters: 5
  max_chapters: 15

# 调整搜索深度
article_generation:
  max_search_rounds: 12

# 修改字数要求
article_generation:
  min_word_count: 3000
  max_word_count: 8000
```

---

## 故障排除

### 问题：API 密钥未设置

**解决**：
```bash
export MOONSHOT_API_KEY="your-key"
```

### 问题：找不到主题

**解决**：
```bash
# 先列出所有主题
python3 main.py --list

# 确认主题名称是否正确
```

### 问题：生成失败

**解决**：
1. 检查网络连接
2. 检查 API 配额
3. 尝试减少 `max_search_rounds`

### 问题：文章质量不佳

**解决**：
1. 增加 `max_search_rounds`（更多信息收集）
2. 调整 `writing_temperature`（0.7-0.9）
3. 编辑 `prompts/expert_narrator.txt` 优化提示词

---

## 下一步

- 阅读 [README.md](./README.md) 了解详细功能
- 查看 [TUTORIAL_GENERATOR_README.md](./TUTORIAL_GENERATOR_README.md) 了解技术细节
- 自定义 `prompts/expert_narrator.txt` 调整写作风格
- 修改 `tutorial_config.yaml` 适配你的需求

---

## 推荐工作流

```
1. 🔍 探索主题
   → python3 main.py --explore "新主题"

2. 📖 检查大纲
   → python3 main.py --curriculum "新主题"
   → python3 main.py --show "新主题"

3. ✍️  分批生成
   → python3 main.py --series "新主题" --range 1-3
   → 检查质量
   → python3 main.py --series "新主题" --range 4-6
   → 继续...

4. 📝 发布
   → 复制 data/articles/ 中的文章到博客
   → 文件名即标题，Frontmatter 已完整
```

---

## 技巧和最佳实践

✅ **主题命名要具体**
- 好：`Transformer 架构详解`
- 差：`深度学习`

✅ **分批生成**
- 每次 3-5 章，方便检查质量
- 避免一次生成过多导致请求限流

✅ **善用跳过参数**
- `--skip-explore`：主题已探索
- `--skip-curriculum`：大纲已生成

✅ **定期备份数据**
- 备份 `data/` 目录下的 JSON 文件

✅ **自定义提示词**
- 根据目标读者调整写作风格
- 修改 `prompts/expert_narrator.txt`

---

需要帮助？参阅完整文档或提交 Issue。

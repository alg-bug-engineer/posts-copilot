# 贡献指南

感谢您对 Posts Copilot 项目的关注！我们欢迎各种形式的贡献，包括但不限于代码、文档、问题反馈和功能建议。

## 🤝 如何贡献

### 报告问题 🐛

如果您发现了 Bug 或有功能建议，请：

1. **搜索现有 Issues**：确保问题还没有被报告
2. **使用 Issue 模板**：选择合适的模板填写详细信息
3. **提供足够信息**：
   - 详细的问题描述
   - 重现步骤
   - 期望的行为
   - 实际的行为
   - 环境信息（操作系统、Python版本等）
   - 错误日志或截图

### 提交代码 💻

#### 开发环境设置

1. **Fork 项目**
   ```bash
   # 在 GitHub 上 Fork 项目
   # 克隆你的 Fork
   git clone https://github.com/your-username/posts-copilot.git
   cd posts-copilot
   ```

2. **设置开发环境**
   ```bash
   # 创建虚拟环境
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或 venv\Scripts\activate  # Windows
   
   # 安装依赖
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 开发依赖
   
   # 安装 pre-commit 钩子
   pre-commit install
   ```

3. **添加上游仓库**
   ```bash
   git remote add upstream https://github.com/original-owner/posts-copilot.git
   ```

#### 开发流程

1. **创建功能分支**
   ```bash
   # 同步最新代码
   git fetch upstream
   git checkout main
   git merge upstream/main
   
   # 创建新分支
   git checkout -b feature/your-feature-name
   # 或 git checkout -b fix/bug-description
   ```

2. **进行开发**
   - 遵循代码规范（见下文）
   - 添加必要的测试
   - 更新相关文档
   
3. **运行测试**
   ```bash
   # 运行所有测试
   pytest
   
   # 运行代码格式检查
   black src/ tests/
   isort src/ tests/
   flake8 src/ tests/
   
   # 运行类型检查
   mypy src/
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新平台支持"
   
   # 或
   git commit -m "fix: 修复登录状态检测问题"
   ```

5. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   然后在 GitHub 上创建 Pull Request。

### 代码规范 📋

#### 编码风格

我们使用以下工具确保代码质量：

- **Black**：代码格式化
- **isort**：导入排序
- **flake8**：代码质量检查
- **mypy**：类型检查

#### 命名规范

- **文件名**：`snake_case.py`
- **类名**：`PascalCase`
- **函数/变量名**：`snake_case`
- **常量**：`UPPER_CASE`
- **私有成员**：`_private_method`

#### 文档字符串

使用 Google 风格的文档字符串：

```python
def publish_article(article_path: str, platform: str) -> bool:
    """
    发布文章到指定平台
    
    Args:
        article_path (str): 文章文件路径
        platform (str): 目标平台名称
        
    Returns:
        bool: 发布是否成功
        
    Raises:
        FileNotFoundError: 文章文件不存在
        ValueError: 平台名称无效
    """
```

#### 类型提示

所有公共函数都应该包含类型提示：

```python
from typing import Optional, List, Dict

def get_article_metadata(file_path: str) -> Optional[Dict[str, str]]:
    """获取文章元数据"""
    pass
```

#### 错误处理

```python
def safe_operation(self) -> bool:
    """安全操作示例"""
    try:
        # 主要逻辑
        result = self.do_something()
        self.logger.info("操作成功")
        return True
        
    except SpecificException as e:
        # 特定异常处理
        self.logger.warning(f"特定错误: {e}")
        return False
        
    except Exception as e:
        # 通用异常处理
        self.logger.error(f"未知错误: {e}", exc_info=True)
        return False
```

### 测试 🧪

#### 测试类型

1. **单元测试**：测试独立的函数和方法
2. **集成测试**：测试组件之间的交互
3. **端到端测试**：测试完整的发布流程

#### 编写测试

```python
# tests/test_publisher.py
import pytest
from unittest.mock import Mock, patch
from src.publisher.base_publisher import BasePublisher

class TestBasePublisher:
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.publisher = BasePublisher()
        
    def test_parse_article(self):
        """测试文章解析"""
        # 准备测试数据
        test_file = "tests/fixtures/test_article.md"
        
        # 执行测试
        result = self.publisher.parse_article(test_file)
        
        # 断言结果
        assert result is not None
        assert "title" in result
        assert "content" in result
        
    @patch('src.publisher.base_publisher.WebDriverWait')
    def test_check_login_success(self, mock_wait):
        """测试登录检查成功"""
        # 模拟成功场景
        mock_wait.return_value.until.return_value = True
        
        result = self.publisher.check_login()
        
        assert result is True
```

#### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件的测试
pytest tests/test_publisher.py

# 运行特定测试方法
pytest tests/test_publisher.py::TestBasePublisher::test_parse_article

# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 只运行快速测试（跳过集成测试）
pytest -m "not integration"
```

### 文档 📚

#### 更新文档

当您的更改影响到用户使用方式时，请更新相应文档：

- **README.md**：基本使用说明
- **docs/INSTALLATION.md**：安装指南  
- **docs/USAGE.md**：详细使用方法
- **docs/DEVELOPMENT.md**：开发指南

#### 文档规范

- 使用清晰的标题层次
- 提供代码示例
- 包含截图（如果需要）
- 保持简洁明了

### 添加新平台支持 🌐

如果您想添加新平台支持，请参考 [开发指南](docs/DEVELOPMENT.md#添加新平台支持)。

基本步骤：

1. 创建新的发布器类
2. 实现必要的抽象方法
3. 添加配置文件
4. 编写测试用例
5. 更新文档

### 提交信息规范 📝

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```bash
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### 类型说明

- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 重构（既不是新功能也不是Bug修复）
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动

#### 示例

```bash
feat: 添加 Medium 平台支持

- 实现 MediumPublisher 类
- 添加 Medium 配置文件
- 增加相关测试用例

Closes #123
```

```bash
fix: 修复知乎登录状态检测问题

登录状态检测逻辑存在时序问题，导致误判为未登录状态。
调整了等待逻辑和重试机制。

Fixes #456
```

### Pull Request 指南 🔄

#### PR 标题

使用描述性的标题：
- ✅ `feat: 添加 Medium 平台支持`
- ✅ `fix: 修复 CSDN 标签设置问题`
- ❌ `更新代码`
- ❌ `修复`

#### PR 描述

包含以下信息：

```markdown
## 📝 变更说明
简要描述这个 PR 的目的和主要变更。

## 🔧 变更类型
- [ ] 新功能 (feature)
- [ ] Bug 修复 (fix)
- [ ] 文档更新 (docs)
- [ ] 重构 (refactor)
- [ ] 测试 (test)

## 📋 变更列表
- 添加了 XXX 功能
- 修复了 YYY 问题
- 更新了 ZZZ 文档

## 🧪 测试情况
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试完成

## 📸 截图（如适用）
[添加截图或 GIF]

## 🔗 相关 Issue
Closes #123
Fixes #456

## 🧑‍💻 检查清单
- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 所有测试都通过
```

### 代码审查 👥

#### 作为提交者

- 确保 PR 描述清晰完整
- 响应审查意见并及时修改
- 保持提交历史整洁
- 确保 CI 检查全部通过

#### 作为审查者

- 关注代码质量和可维护性
- 检查是否遵循项目规范
- 确认测试覆盖充分
- 提供建设性的反馈

### 发布流程 🚀

项目维护者会定期发布新版本：

1. **版本号**：遵循 [语义化版本](https://semver.org/lang/zh-CN/)
   - `MAJOR.MINOR.PATCH`
   - 例如：`1.2.3`

2. **发布说明**：每个版本都会有详细的 CHANGELOG

3. **标签**：使用 Git 标签标记版本

### 行为准则 🤝

我们致力于为所有人提供友好、安全和欢迎的环境，无论：

- 性别、性别认同和表达
- 性取向
- 残疾
- 外貌
- 身材
- 种族
- 年龄
- 宗教

#### 期望行为

- 使用友好和包容的语言
- 尊重不同的观点和经历
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表现出同理心

#### 不可接受的行为

- 使用性别化语言或意象，以及不受欢迎的性关注或性暗示
- 挑衅、侮辱/贬损评论，人身攻击或政治攻击
- 公开或私下的骚扰
- 未经明确许可发布他人的私人信息
- 其他在专业环境中可能被认为不当的行为

## 🆘 获得帮助

如果您需要帮助：

- 📖 查看 [文档](docs/)
- 🔍 搜索现有 [Issues](https://github.com/your-username/posts-copilot/issues)
- 💬 在 [Discussions](https://github.com/your-username/posts-copilot/discussions) 中提问
- 📧 联系维护者：your-email@example.com

## 🙏 致谢

感谢所有为项目做出贡献的人！您的参与让 Posts Copilot 变得更好。

---

再次感谢您的贡献！🎉
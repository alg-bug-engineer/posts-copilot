# 开发指南

本指南将帮助你为 Posts Copilot 添加新平台支持或改进现有功能。

## 项目架构

### 核心组件

```
src/
├── core/                    # 核心功能
│   ├── logger.py           # 日志系统
│   └── session_manager.py  # 会话管理
├── publisher/              # 发布器
│   ├── base_publisher.py   # 抽象基类
│   ├── common_handler.py   # 通用函数
│   └── *_publisher.py      # 各平台发布器
└── utils/                  # 工具函数
    ├── file_utils.py      # 文件操作
    └── yaml_file_utils.py # 配置文件操作
```

### 设计模式

1. **抽象工厂模式**：`BasePublisher` 定义发布器接口
2. **模板方法模式**：通用发布流程在基类中定义
3. **策略模式**：不同平台使用不同的发布策略
4. **单例模式**：`SessionManager` 管理浏览器会话

## 添加新平台支持

### 第一步：了解基础架构

所有发布器都必须继承 `BasePublisher` 类：

```python
from abc import ABC, abstractmethod
from src.core.logger import get_logger

class BasePublisher(ABC):
    """发布器抽象基类"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.driver = None
        self.session_manager = None
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """返回平台名称"""
        pass
    
    @abstractmethod  
    def publish(self, article_path: str) -> bool:
        """发布文章的主要方法"""
        pass
    
    # 其他通用方法...
```

### 第二步：创建新平台发布器

以添加 "Medium" 平台为例：

```python
# src/publisher/medium_publisher.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.publisher.base_publisher import BasePublisher
from src.publisher.common_handler import *

class MediumPublisher(BasePublisher):
    """Medium 平台发布器"""
    
    PLATFORM_NAME = "medium"
    
    def get_platform_name(self) -> str:
        return self.PLATFORM_NAME
    
    def publish(self, article_path: str) -> bool:
        """发布文章到 Medium"""
        try:
            # 1. 加载配置
            config = self.load_config()
            
            # 2. 打开编辑页面
            self.logger.info(f"正在打开 {self.PLATFORM_NAME} 编辑页面...")
            self.driver.get(config['site'])
            
            # 3. 检查登录状态
            if not self.check_login():
                self.wait_login()
            
            # 4. 解析文章
            article_data = self.parse_article(article_path)
            
            # 5. 填充内容
            self.fill_title_and_content(article_data)
            
            # 6. 设置发布选项
            self.set_publish_options(config, article_data)
            
            # 7. 发布文章
            if config.get('auto_publish', False):
                return self.submit_article()
            else:
                self.logger.info("已保存为草稿，请手动发布")
                return True
                
        except Exception as e:
            self.logger.error(f"发布失败: {e}")
            return False
    
    def check_login(self) -> bool:
        """检查是否已登录"""
        try:
            # Medium 特定的登录检查逻辑
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='profileButton']"))
            )
            self.logger.info("✓ 已登录 Medium")
            return True
        except:
            self.logger.warning("需要登录 Medium")
            return False
    
    def fill_title_and_content(self, article_data: dict) -> bool:
        """填充标题和内容"""
        try:
            # 填充标题
            title_selector = "h1[data-testid='storyTitle']"
            title_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, title_selector))
            )
            
            safe_input(self.driver, title_element, article_data['title'])
            self.logger.info(f"✓ 标题填充完成: {article_data['title']}")
            
            # 填充内容
            content_selector = "[data-testid='storyContent']"
            content_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, content_selector))
            )
            
            safe_input(self.driver, content_element, article_data['content'])
            self.logger.info(f"✓ 内容填充完成 ({len(article_data['content'])} 字符)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"填充内容失败: {e}")
            return False
    
    def set_publish_options(self, config: dict, article_data: dict) -> bool:
        """设置发布选项"""
        try:
            # 设置标签
            if article_data.get('tags'):
                self.set_tags(article_data['tags'])
            
            # 设置其他 Medium 特定选项
            # ...
            
            return True
            
        except Exception as e:
            self.logger.error(f"设置发布选项失败: {e}")
            return False
    
    def set_tags(self, tags: list) -> bool:
        """设置文章标签"""
        try:
            # Medium 标签设置逻辑
            # ...
            return True
        except Exception as e:
            self.logger.error(f"设置标签失败: {e}")
            return False
    
    def submit_article(self) -> bool:
        """提交发布文章"""
        try:
            # 点击发布按钮
            publish_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='publishButton']"))
            )
            
            safe_click(self.driver, publish_button)
            self.logger.info("✓ 文章发布成功!")
            
            return True
            
        except Exception as e:
            self.logger.error(f"发布文章失败: {e}")
            return False
```

### 第三步：创建配置文件

```yaml
# config/medium.yaml

# Medium 编辑页面URL  
site: https://medium.com/new-story

# 是否自动发布（false=保存为草稿）
auto_publish: false

# 默认标签
default_tags:
  - Technology
  - Programming
  - Software Development

# 发布设置
publication: ""  # 发布到指定出版物（可选）
```

### 第四步：注册新平台

在 `publish.py` 中注册新平台：

```python
# publish.py

ALL_PLATFORMS = [
    'csdn',
    'juejin', 
    'zhihu',
    'cto51',
    'alicloud',
    'toutiao',
    'wechat',
    'medium',  # 新增
]

def get_publisher(platform: str):
    """根据平台名称获取发布器实例"""
    if platform == 'csdn':
        from src.publisher.csdn_publisher import CSDNPublisher
        return CSDNPublisher()
    # ... 其他平台 ...
    elif platform == 'medium':
        from src.publisher.medium_publisher import MediumPublisher
        return MediumPublisher()
    else:
        logger.warning(f"平台 {platform} 的发布器尚未实现")
        return None
```

### 第五步：添加到配置

```yaml
# config/common.yaml
enable:
  # ... 其他平台 ...
  medium: true
```

## 通用工具函数

项目提供了丰富的工具函数，在 `common_handler.py` 中：

### 元素操作
```python
def safe_click(driver, element, max_retries=3) -> bool:
    """安全点击元素（带重试）"""
    
def safe_input(driver, element, text, clear=True) -> bool:
    """安全输入文本（自动清空）"""
    
def wait_for_element(driver, selector, timeout=10):
    """等待元素出现"""
    
def check_element_exists(driver, selector) -> bool:
    """检查元素是否存在"""
```

### 登录相关  
```python
def wait_login(driver, platform_name: str):
    """等待用户完成登录"""
    
def save_cookies(driver, platform_name: str):
    """保存登录状态"""
    
def load_cookies(driver, platform_name: str) -> bool:
    """加载登录状态"""
```

### 内容处理
```python
def parse_markdown_file(file_path: str) -> dict:
    """解析 Markdown 文件"""
    
def extract_front_matter(content: str) -> tuple:
    """提取 Front Matter 元数据"""
    
def process_images(content: str) -> str:
    """处理文章中的图片"""
```

## 测试指南

### 单元测试

为新平台创建测试文件：

```python
# tests/test_medium_publisher.py

import pytest
from unittest.mock import Mock, patch
from src.publisher.medium_publisher import MediumPublisher

class TestMediumPublisher:
    
    def setup_method(self):
        self.publisher = MediumPublisher()
        self.publisher.driver = Mock()
        
    def test_get_platform_name(self):
        assert self.publisher.get_platform_name() == "medium"
    
    def test_check_login_success(self):
        # 模拟登录成功
        with patch('selenium.webdriver.support.ui.WebDriverWait'):
            result = self.publisher.check_login()
            assert result == True
    
    def test_check_login_failed(self):
        # 模拟登录失败  
        self.publisher.driver.find_element.side_effect = Exception()
        result = self.publisher.check_login()
        assert result == False
    
    @patch('src.publisher.medium_publisher.safe_input')
    def test_fill_title_and_content(self, mock_safe_input):
        mock_safe_input.return_value = True
        
        article_data = {
            'title': 'Test Title',
            'content': 'Test Content'
        }
        
        result = self.publisher.fill_title_and_content(article_data)
        assert result == True
        assert mock_safe_input.call_count == 2
```

### 集成测试

```python
# tests/test_medium_integration.py

import pytest
from src.publisher.medium_publisher import MediumPublisher
from src.core.session_manager import SessionManager

@pytest.mark.integration
class TestMediumIntegration:
    
    def setup_method(self):
        self.session_manager = SessionManager()
        self.publisher = MediumPublisher()
        self.publisher.session_manager = self.session_manager
        self.publisher.driver = self.session_manager.driver
    
    def test_full_publish_flow(self):
        """测试完整发布流程"""
        # 需要真实环境和登录状态
        article_path = "tests/fixtures/test_article.md"
        result = self.publisher.publish(article_path)
        assert result == True
        
    def teardown_method(self):
        self.session_manager.close()
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定平台测试
pytest tests/test_medium_publisher.py

# 运行集成测试（需要真实环境）
pytest tests/test_medium_integration.py -m integration

# 生成覆盖率报告
pytest --cov=src tests/
```

## 调试技巧

### 1. 启用详细日志

```yaml
# config/common.yaml
logging:
  level: DEBUG  # 启用详细日志
  console: true # 控制台输出
  file: data/logs/publisher.log
```

### 2. 浏览器调试

```python
# 在发布器中添加调试代码
def debug_page(self):
    """调试当前页面"""
    print(f"当前 URL: {self.driver.current_url}")
    print(f"页面标题: {self.driver.title}")
    
    # 保存页面截图
    self.driver.save_screenshot(f"debug_{self.PLATFORM_NAME}.png")
    
    # 保存页面源码
    with open(f"debug_{self.PLATFORM_NAME}.html", "w") as f:
        f.write(self.driver.page_source)
```

### 3. 元素定位调试

```python
def find_element_debug(self, selector: str):
    """调试元素定位"""
    try:
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        print(f"✓ 找到元素: {selector}")
        return element
    except Exception as e:
        print(f"✗ 元素定位失败: {selector}")
        print(f"错误信息: {e}")
        
        # 尝试其他可能的选择器
        alternative_selectors = [
            selector.replace("_", "-"),
            selector.replace("-", "_"), 
            f"#{selector}",
            f".{selector}"
        ]
        
        for alt_selector in alternative_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, alt_selector)
                print(f"✓ 备选选择器有效: {alt_selector}")
                return element
            except:
                continue
                
        return None
```

## 代码规范

### 1. 命名规范

- 类名：`PascalCase`（如 `MediumPublisher`）
- 方法名：`snake_case`（如 `check_login`）
- 常量：`UPPER_CASE`（如 `PLATFORM_NAME`）
- 私有方法：`_method_name`

### 2. 文档字符串

```python
def publish(self, article_path: str) -> bool:
    """
    发布文章到平台
    
    Args:
        article_path (str): 文章文件路径
        
    Returns:
        bool: 发布是否成功
        
    Raises:
        FileNotFoundError: 文章文件不存在
        ConnectionError: 网络连接失败
    """
```

### 3. 错误处理

```python
def some_operation(self):
    """操作示例"""
    try:
        # 主要逻辑
        result = self.do_something()
        return result
        
    except SpecificException as e:
        # 特定异常处理
        self.logger.warning(f"特定错误: {e}")
        return self.fallback_method()
        
    except Exception as e:
        # 通用异常处理
        self.logger.error(f"操作失败: {e}", exc_info=True)
        return False
        
    finally:
        # 清理工作
        self.cleanup()
```

## 贡献流程

### 1. 准备工作
```bash
# Fork 项目到你的 GitHub
# 克隆你的 Fork
git clone https://github.com/your-username/posts-copilot.git
cd posts-copilot

# 添加上游仓库
git remote add upstream https://github.com/original-owner/posts-copilot.git

# 创建开发分支
git checkout -b feature/medium-support
```

### 2. 开发
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试确保环境正常
pytest tests/

# 进行你的开发...

# 运行代码格式化
black src/ tests/
isort src/ tests/

# 运行 lint 检查
flake8 src/ tests/
```

### 3. 提交
```bash
# 提交代码
git add .
git commit -m "feat: 添加 Medium 平台支持

- 实现 MediumPublisher 类
- 添加 Medium 配置文件
- 增加相关测试用例
- 更新文档
"

# 推送到你的 Fork
git push origin feature/medium-support
```

### 4. 创建 Pull Request

在 GitHub 上创建 PR，包含：

- 清晰的标题和描述
- 变更列表
- 测试截图
- 相关 Issue 链接

## 发布新版本

### 1. 版本管理

项目使用语义化版本：`MAJOR.MINOR.PATCH`

- `MAJOR`：不兼容的 API 修改
- `MINOR`：向后兼容的功能性新增  
- `PATCH`：向后兼容的问题修正

### 2. 发布流程

```bash
# 更新版本号
vim setup.py  # 或 pyproject.toml

# 更新 CHANGELOG
vim CHANGELOG.md

# 提交版本更新
git add .
git commit -m "chore: 发布 v1.2.0"

# 创建标签
git tag -a v1.2.0 -m "Release v1.2.0"

# 推送标签
git push origin v1.2.0
```

### 3. 自动化发布

使用 GitHub Actions：

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
          
      - name: Install dependencies
        run: |
          pip install build twine
          
      - name: Build package
        run: python -m build
        
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
        
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

## 获得帮助

- 📖 阅读现有发布器代码作为参考
- 💬 在 [Discussions](https://github.com/your-username/posts-copilot/discussions) 中提问
- 🐛 通过 [Issues](https://github.com/your-username/posts-copilot/issues) 报告问题
- 📧 联系维护者：your-email@example.com
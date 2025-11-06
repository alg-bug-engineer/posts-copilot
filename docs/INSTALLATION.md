# 安装和配置指南

## 系统要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.7+ | 推荐使用 3.8 或更高版本 |
| Chrome | 最新版 | 用于自动化操作 |
| 操作系统 | Windows/macOS/Linux | 全平台支持 |

## 详细安装步骤

### 1. 环境准备

#### 检查 Python 版本
```bash
python --version
# 或
python3 --version
```

如果版本低于 3.7，请升级 Python。

#### 安装 Chrome 浏览器
- [Chrome 官方下载](https://www.google.com/chrome/)
- 确保安装最新版本

### 2. 项目安装

#### 克隆项目
```bash
git clone https://github.com/your-username/posts-copilot.git
cd posts-copilot
```

#### 创建虚拟环境（强烈推荐）
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置文件设置

#### 复制配置文件
```bash
# 如果存在示例配置文件
cp config/common.yaml.example config/common.yaml

# 或者手动创建配置文件
vim config/common.yaml
```

#### 基础配置示例
```yaml
# 文章目录 - 修改为你的文章存放目录
content_dir: /path/to/your/articles/

# Chrome 调试端口
debugger_address: 127.0.0.1:9222

# 发布设置
auto_publish: false  # false=需要确认, true=自动发布

# 启用的平台
enable:
  csdn: true
  juejin: true  
  zhihu: true
  cto51: true
  alicloud: true
  toutiao: false    # 可选关闭
  wechat: false     # 可选关闭

# 日志设置
logging:
  level: INFO
  file: data/logs/publisher.log
```

### 4. 平台特定配置

每个平台都可以有独立的配置文件：

#### CSDN 配置 (`config/csdn.yaml`)
```yaml
site: https://editor.csdn.net/md/
auto_publish: false
default_tags: [Python, 技术分享, 编程]
default_category: 技术文章
visibility: 全部可见
```

#### 掘金配置 (`config/juejin.yaml`)  
```yaml
site: https://juejin.cn/editor/drafts/new
auto_publish: false
default_tags: [Python, 前端, 后端]
default_category: 后端
```

#### 知乎配置 (`config/zhihu.yaml`)
```yaml
site: https://zhuanlan.zhihu.com/write
auto_publish: false
use_column: true
default_topics: [编程, 人工智能, 技术]
```

## Chrome 调试模式设置

Chrome 调试模式是工具正常运行的关键。

### 启动 Chrome 调试模式

#### macOS
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome_dev" \
  --no-first-run \
  --no-default-browser-check
```

#### Linux
```bash
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome_dev" \
  --no-first-run \
  --no-default-browser-check
```

#### Windows
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="C:\temp\chrome_dev" ^
  --no-first-run ^
  --no-default-browser-check
```

### 使用启动脚本（推荐）

项目提供了便捷的启动脚本：

```bash
# 启动 Chrome 调试模式
chmod +x scripts/start_chrome.sh
./scripts/start_chrome.sh

# 启动发布程序
chmod +x scripts/start.sh  
./scripts/start.sh
```

### 验证调试模式
```bash
curl http://127.0.0.1:9222/json/version
```

看到 JSON 输出说明启动成功。

## 首次运行

### 1. 测试运行
```bash
python publish.py
```

### 2. 首次登录流程
1. 选择一篇测试文章
2. 选择一个平台（建议先选择 CSDN）
3. 程序会自动打开平台编辑页面
4. **手动登录**该平台（只需要第一次）
5. 登录后按回车继续
6. 程序会自动完成后续发布流程

### 3. 登录状态保存
- 登录成功后，程序会自动保存登录状态
- 下次使用该平台时会自动登录
- 登录状态保存在 `data/cookies/` 目录

## 故障排除

### 常见问题

#### 1. Chrome 启动失败
**问题**：Chrome 调试模式启动失败
**解决方案**：
- 确保 Chrome 已正确安装
- 关闭所有 Chrome 进程后重试
- 检查端口 9222 是否被占用

#### 2. 无法连接到 Chrome
**问题**：程序提示无法连接到 Chrome
**解决方案**：
- 确认 Chrome 调试模式已启动
- 检查防火墙设置
- 确认端口配置正确

#### 3. 登录状态失效
**问题**：提示需要重新登录
**解决方案**：
```bash
# 删除对应平台的 cookie 文件
rm data/cookies/csdn_cookies.pkl
# 重新运行程序并登录
python publish.py
```

#### 4. 元素定位失败
**问题**：页面元素找不到
**解决方案**：
- 平台页面可能已更新
- 查看日志确定失败的元素
- 提交 Issue 报告问题

### 获得帮助

如果遇到问题：

1. **查看日志**：`data/logs/publisher.log`
2. **搜索 Issues**：[GitHub Issues](https://github.com/your-username/posts-copilot/issues)
3. **提交问题**：详细描述问题和错误信息
4. **参与讨论**：[GitHub Discussions](https://github.com/your-username/posts-copilot/discussions)

## 下一步

安装完成后，建议：

1. 阅读 [使用指南](USAGE.md) 了解详细用法
2. 查看 [平台配置指南](guides/) 了解各平台特性  
3. 如需开发扩展，参考 [开发指南](DEVELOPMENT.md)
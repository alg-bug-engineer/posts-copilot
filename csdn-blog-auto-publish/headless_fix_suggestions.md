# Headless 模式发布失败问题分析与解决方案

## 问题现象
- `headless=true` 时：日志显示"已触发发布请求"，但文章实际未发布
- `headless=false` 时：正常发布成功

## 根本原因分析

### 1. 时序问题（主要原因）
**问题位置：** `publish_csdn.py` 第187行
```python
time.sleep(0.5)  # 点击主发布按钮后等待弹窗
```

**原因：**
- headless 模式下，浏览器没有 GPU 加速，页面渲染较慢
- 弹窗的 DOM 加载、CSS 动画、JavaScript 初始化需要更多时间
- 0.5秒不足以让弹窗完全就绪，导致后续操作失败

**证据：**
- 日志显示所有步骤都"成功"，但实际未生效
- 这表明元素可能被找到但状态不对（如被禁用、被覆盖等）

### 2. 网络请求未完成
**问题位置：** `publish_csdn.py` 第477-482行
```python
page.wait_for_selector(container, state='detached', timeout=10000)
print(f"容器 {container} 已关闭")
clicked_confirm = True
break
```

**原因：**
- 只等待 modal DOM 消失，不等待实际的发布 HTTP 请求
- headless 模式下网络请求可能较慢
- 脚本继续执行后，浏览器上下文可能被清理，请求被中断

### 3. 反自动化检测
**可能的检测点：**
- `navigator.webdriver === true` (Playwright 默认会设置)
- 缺少某些浏览器 API（如 Chrome.runtime）
- 操作时序过于规律（人类操作会有随机延迟）
- headless 模式的浏览器指纹特征

## 解决方案

### 方案 A：增强 headless 模式的时序控制（推荐）

#### 1. 增加弹窗等待时间
```python
# 原代码（第187行）
time.sleep(0.5)

# 修改为
if headless:
    time.sleep(2)  # headless 需要更长等待
else:
    time.sleep(0.5)
```

#### 2. 等待网络请求完成
在点击最终发布按钮后，添加：
```python
# 等待发布请求发送（监听网络）
with page.expect_response(lambda response: "blog-console-api.csdn.net" in response.url and response.status == 200, timeout=15000) as response_info:
    btn_locator.click(timeout=5000)
    
response = response_info.value
print(f"发布请求已完成: {response.status} {response.url}")
```

#### 3. 增加操作间随机延迟
```python
import random

def random_delay(min_ms=100, max_ms=500):
    time.sleep(random.uniform(min_ms/1000, max_ms/1000))

# 在关键操作后添加
locator.click()
random_delay(200, 800)  # 模拟人类操作
```

### 方案 B：伪装 headless 浏览器

在启动浏览器时添加配置：
```python
# 在 main() 函数中，第542行附近
browser = p.chromium.launch(
    headless=headless,
    args=[
        '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-setuid-sandbox',
    ]
)

# 创建 context 时添加
context = browser.new_context(
    storage_state=str(storage_file) if storage_file.exists() else None,
    viewport={'width': 1920, 'height': 1080},
    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    locale='zh-CN',
    timezone_id='Asia/Shanghai',
)

# 注入脚本隐藏 webdriver 特征
context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    window.chrome = { runtime: {} };
""")
```

### 方案 C：调试模式 - 添加截图和日志

在关键步骤添加截图：
```python
# 在每个关键操作后
page.screenshot(path=f'debug_{idx}_step.png')
print(f"已截图: debug_{idx}_step.png")

# 检查实际的元素状态
visible = locator.is_visible()
enabled = locator.is_enabled()
print(f"元素状态: visible={visible}, enabled={enabled}")
```

### 方案 D：验证发布是否成功

在发布后验证：
```python
# 在 click_publish_buttons 返回后
time.sleep(5)  # 等待页面跳转

# 检查是否跳转到文章管理页面
current_url = page.url
if 'article/manage' in current_url or 'article/list' in current_url:
    print("发布成功：已跳转到文章管理页面")
    return True
    
# 或检查是否有成功提示
success_selectors = [
    'text=发布成功',
    '.success-message',
    '[class*="success"]'
]
for sel in success_selectors:
    if page.locator(sel).count() > 0:
        print(f"发现成功提示: {sel}")
        return True

print("警告：未检测到发布成功的明确标志")
return False
```

## 推荐实施顺序

1. **立即实施：** 方案 A 的第1、3点（增加等待时间和随机延迟）
2. **验证效果：** 方案 D（添加发布验证）
3. **如果仍失败：** 方案 B（伪装浏览器特征）
4. **调试排查：** 方案 C（添加截图和详细日志）
5. **最终方案：** 方案 A 的第2点（网络请求监听）

## 快速测试脚本

创建一个测试脚本验证改进：
```bash
# 测试 headless 模式
python publish_csdn.py --headless true

# 检查文章是否真的发布
# 访问 CSDN 个人博客管理页面确认
```

## 临时解决方案

如果上述方案都不奏效，可以考虑：
1. 使用 `--headless false` 但最小化窗口
2. 使用 Xvfb（Linux）创建虚拟显示
3. 在 headless 模式下增加整体等待时间到 60 秒

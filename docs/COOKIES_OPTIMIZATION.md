# Cookies 管理优化

## 修复的问题

### 1. 每个平台独立的 Cookies 存储

**问题**: 之前所有平台共享一个 `common_cookies.pkl` 文件，导致不同平台的 cookies 互相冲突。

**解决方案**: 
- 修改了 `SessionManager` 类，为每个平台创建独立的 cookies 文件
- 文件命名格式：`{platform}_cookies.pkl`
- 例如：`csdn_cookies.pkl`、`zhihu_cookies.pkl`、`juejin_cookies.pkl` 等

### 2. Cookies 自动更新机制

**问题**: cookies 只在登录时保存，操作过程中浏览器更新的 cookies 没有同步保存。

**解决方案**:
- 添加了 `update_cookies()` 方法，实时同步浏览器中的最新 cookies
- 在两个关键时机自动更新 cookies：
  1. **登录检查后**: 如果已登录，更新 cookies 保持同步
  2. **操作完成后**: 发布成功、保存草稿等操作后更新 cookies

## 修改的文件

### 核心文件

1. **`src/core/session_manager.py`**
   - 优化 `save_cookies()` 方法，支持 `force_save` 参数
   - 添加 `update_cookies()` 方法，实时同步最新 cookies
   - 增强 cookies 变化检测，避免无意义的重复保存

2. **`src/publisher/base_publisher.py`**
   - 添加 `update_cookies()` 方法
   - 优化 `save_login_state()` 方法，强制保存登录时的 cookies

### 发布器文件

更新了所有发布器，在关键节点自动更新 cookies：

1. **`src/publisher/toutiao_publisher.py`** - 今日头条
2. **`src/publisher/zhihu_publisher.py`** - 知乎
3. **`src/publisher/csdn_publisher.py`** - CSDN
4. **`src/publisher/juejin_publisher.py`** - 掘金
5. **`src/publisher/cto51_publisher.py`** - 51CTO
6. **`src/publisher/wechat_publisher.py`** - 微信公众号
7. **`src/publisher/alicloud_publisher.py`** - 阿里云

### 工具文件

1. **`scripts/cookies_manager.py`** - 新增的 cookies 管理工具

## 新增功能

### Cookies 管理工具

创建了专门的 cookies 管理脚本 `scripts/cookies_manager.py`，提供以下功能：

#### 查看 Cookies 信息
```bash
python scripts/cookies_manager.py --list
```
显示所有平台的 cookies 文件信息，包括：
- 文件大小
- 修改时间  
- Cookie 数量
- 所属域名

#### 清理 Cookies
```bash
# 清理特定平台
python scripts/cookies_manager.py --clean --platform csdn

# 清理所有平台
python scripts/cookies_manager.py --clean
```

#### 备份和恢复
```bash
# 备份 cookies
python scripts/cookies_manager.py --backup --backup-name my_backup

# 恢复 cookies
python scripts/cookies_manager.py --restore my_backup
```

#### 导出为 JSON
```bash
# 导出特定平台的 cookies 为 JSON 格式
python scripts/cookies_manager.py --export --platform zhihu --output zhihu_cookies.json
```

## 工作流程优化

### 之前的流程
```
1. 加载 common_cookies.pkl (所有平台共享)
2. 检查登录状态
3. 如需登录 → 保存到 common_cookies.pkl
4. 执行发布操作
5. 结束 (cookies 可能已过期或变化)
```

### 现在的流程
```
1. 加载 {platform}_cookies.pkl (平台专用)
2. 检查登录状态
3. 如需登录 → 强制保存到 {platform}_cookies.pkl
4. 如已登录 → 更新当前 cookies 到 {platform}_cookies.pkl
5. 执行发布操作
6. 操作完成后 → 再次更新 cookies 到 {platform}_cookies.pkl
```

## 优势

### 1. 隔离性
- 每个平台的 cookies 完全独立
- 避免不同平台间的 cookies 冲突
- 某个平台的 cookies 问题不影响其他平台

### 2. 实时性
- 自动捕获操作过程中 cookies 的变化
- 确保 cookies 始终保持最新状态
- 减少因 cookies 过期导致的重复登录

### 3. 可维护性
- 提供专门的管理工具
- 支持备份、恢复、清理等操作
- 便于调试和排查问题

### 4. 智能化
- 自动检测 cookies 变化，避免无意义的写操作
- 在关键节点自动保存，无需手动干预
- 支持强制保存和智能保存两种模式

## 使用示例

### 查看当前 Cookies 状态
```bash
python scripts/cookies_manager.py --list
```

### 清理特定平台的 Cookies（强制重新登录）
```bash
python scripts/cookies_manager.py --clean --platform csdn
```

### 备份当前所有 Cookies
```bash
python scripts/cookies_manager.py --backup --backup-name before_update
```

## 注意事项

1. **清理旧文件**: 已删除旧的 `common_cookies.pkl` 文件
2. **首次运行**: 首次运行时各平台需要重新登录
3. **备份习惯**: 建议在重要操作前备份 cookies
4. **调试支持**: 可通过日志查看 cookies 更新情况

## 兼容性

- ✅ 完全向后兼容现有的发布流程
- ✅ 不影响现有的配置文件
- ✅ 支持所有现有的发布平台
- ✅ 自动处理新旧 cookies 格式切换
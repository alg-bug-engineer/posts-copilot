# Chrome 调试模式管理脚本使用指南

## 脚本概览

项目提供了三个便捷脚本来管理 Chrome 调试模式：

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `start_chrome.sh` | 启动 Chrome 调试模式 | 首次启动或重启 |
| `stop_chrome.sh` | 停止 Chrome 调试模式 | 手动关闭 Chrome |
| `restart_chrome.sh` | 重启 Chrome 调试模式 | 快速重启 |

---

## 1. start_chrome.sh - 启动脚本

### 功能特性

✅ **自动检测旧实例**：启动前检查是否有运行中的 Chrome 调试进程  
✅ **自动清理**：如果发现旧实例，自动停止并清理  
✅ **智能清理锁文件**：删除可能导致启动失败的锁文件  
✅ **后台模式配置**：启动时就配置好后台模式参数  
✅ **等待验证**：等待调试端口就绪后才返回  

### 使用方法

```bash
# 启动 Chrome 调试模式
bash scripts/start_chrome.sh

# 或者（如果已添加执行权限）
./scripts/start_chrome.sh
```

### 执行流程

```
1. 检测现有 Chrome 调试进程
   ├─ 未发现 → 直接启动
   └─ 发现 → 执行清理流程
       ├─ 尝试优雅关闭（kill）
       ├─ 等待 2 秒
       ├─ 检查是否还在运行
       ├─ 如果还在运行 → 强制终止（kill -9）
       └─ 清理锁文件

2. 启动新的 Chrome 实例
   ├─ 配置调试端口：9222
   ├─ 配置用户数据目录：/tmp/chrome_dev
   ├─ 配置后台模式参数
   └─ 后台运行

3. 验证启动成功
   ├─ 轮询检查调试端口（最多 10 次）
   ├─ 成功 → 显示调试地址
   └─ 超时 → 提示用户稍后
```

### 输出示例

**成功启动（无旧实例）**：
```
==========================================
  启动 Chrome 调试模式
==========================================

🔍 检查现有的 Chrome 调试进程...
✓ 没有发现运行中的 Chrome 调试进程

正在启动 Chrome（macOS）...

✓ Chrome 已启动（PID: 12345，后台模式）

等待 Chrome 调试端口就绪...

✓ Chrome 调试模式已就绪！

调试地址：http://127.0.0.1:9222

==========================================
  现在可以运行发布脚本了
==========================================
```

**成功启动（清理旧实例）**：
```
==========================================
  启动 Chrome 调试模式
==========================================

🔍 检查现有的 Chrome 调试进程...
⚠️  发现运行中的 Chrome 调试进程：
  - PID: 11111

🛑 正在停止旧的 Chrome 实例...
✓ 旧实例已停止

正在启动 Chrome（macOS）...

✓ Chrome 已启动（PID: 12345，后台模式）
...
```

---

## 2. stop_chrome.sh - 停止脚本

### 功能特性

✅ **查找所有调试进程**：找出所有带调试端口的 Chrome 进程  
✅ **优雅关闭**：先尝试正常终止  
✅ **强制终止**：如果进程未响应，强制 kill  
✅ **清理锁文件**：删除可能影响下次启动的锁文件  

### 使用方法

```bash
# 停止 Chrome 调试模式
bash scripts/stop_chrome.sh

# 或者
./scripts/stop_chrome.sh
```

### 使用场景

- 需要完全关闭 Chrome
- 启动新实例前手动清理
- 遇到启动问题时重置环境

### 输出示例

```
==========================================
  停止 Chrome 调试模式
==========================================

🔍 查找 Chrome 调试进程...
⚠️  发现运行中的 Chrome 调试进程：
  - PID: 12345

🛑 正在停止 Chrome 调试进程...
  停止 PID: 12345

🧹 清理临时数据目录锁文件...

✓ Chrome 调试模式已停止

==========================================
```

---

## 3. restart_chrome.sh - 重启脚本

### 功能特性

✅ **一键重启**：简化重启流程  
✅ **自动清理**：内部调用 `start_chrome.sh`，自动清理旧实例  

### 使用方法

```bash
# 重启 Chrome 调试模式
bash scripts/restart_chrome.sh

# 或者
./scripts/restart_chrome.sh
```

### 使用场景

- 修改了配置需要重启
- Chrome 行为异常需要重置
- 日常快速重启

---

## 常见问题

### Q1: 启动时提示"Chrome 已在运行"

**A**: 这是旧版本的提示。新版脚本会自动清理，无需手动操作。

如果仍有问题，手动停止：
```bash
bash scripts/stop_chrome.sh
```

### Q2: 提示"进程未响应，强制终止"

**A**: 这是正常的。某些情况下 Chrome 进程需要强制终止，脚本会自动处理。

### Q3: 启动后无法连接到 9222 端口

**可能原因**：
1. 端口被其他程序占用
2. 防火墙阻止

**解决方案**：
```bash
# 检查端口占用
lsof -i :9222

# 如果有其他程序占用，先停止该程序
# 然后重新启动
bash scripts/start_chrome.sh
```

### Q4: 清理锁文件后仍无法启动

**A**: 尝试完全清理用户数据目录：
```bash
# 停止 Chrome
bash scripts/stop_chrome.sh

# 删除用户数据目录
rm -rf /tmp/chrome_dev

# 重新启动
bash scripts/start_chrome.sh
```

### Q5: 在 Linux 上使用报错

**A**: 确保安装了 `google-chrome` 或 `chromium-browser`：
```bash
# Ubuntu/Debian
sudo apt install google-chrome-stable

# 或
sudo apt install chromium-browser
```

---

## 技术细节

### 进程检测方法

**macOS**:
```bash
ps aux | grep "[C]hrome.*remote-debugging-port=9222" | awk '{print $2}'
```

**Linux**:
```bash
ps aux | grep "[c]hrome.*remote-debugging-port=9222" | awk '{print $2}'
```

使用 `[C]` 或 `[c]` 技巧避免匹配到 grep 自身进程。

### 锁文件位置

Chrome 使用以下文件来防止多实例：
- `/tmp/chrome_dev/SingletonLock`
- `/tmp/chrome_dev/SingletonSocket`
- `/tmp/chrome_dev/SingletonCookie`

脚本会自动清理这些文件。

### 调试端口验证

使用 curl 检查调试端口是否就绪：
```bash
curl -s http://127.0.0.1:9222/json/version
```

成功返回 JSON 数据表示端口已就绪。

---

## 最佳实践

### 1. 日常使用流程

```bash
# 第一次启动
bash scripts/start_chrome.sh

# 使用自动发布
bash scripts/auto_publish.sh

# 完成后可以保持 Chrome 运行
# 下次直接使用即可
```

### 2. 遇到问题时

```bash
# 方法1：重启 Chrome
bash scripts/restart_chrome.sh

# 方法2：手动清理
bash scripts/stop_chrome.sh
rm -rf /tmp/chrome_dev
bash scripts/start_chrome.sh
```

### 3. 服务器部署

```bash
# 添加到系统服务或 cron
# 确保 Chrome 总是运行
*/5 * * * * bash /path/to/scripts/start_chrome.sh
```

---

## 与自动发布脚本集成

### auto_publish.sh 集成

`auto_publish.sh` 已集成 Chrome 检测和启动：

```bash
# 检查 Chrome 是否在调试模式下运行
if ! lsof -i :9222 > /dev/null 2>&1; then
    echo "⚠️  Chrome 调试模式未运行"
    echo ""
    echo "正在启动 Chrome 调试模式..."
    bash scripts/start_chrome.sh &
    
    # 等待 Chrome 启动
    sleep 3
fi
```

**优点**：
- 自动检测
- 自动启动
- 无需手动干预

---

## 命令速查

```bash
# 启动 Chrome 调试模式
bash scripts/start_chrome.sh

# 停止 Chrome 调试模式
bash scripts/stop_chrome.sh

# 重启 Chrome 调试模式
bash scripts/restart_chrome.sh

# 检查 Chrome 是否运行
lsof -i :9222

# 手动查看调试信息
curl http://127.0.0.1:9222/json/version

# 清理用户数据（完全重置）
rm -rf /tmp/chrome_dev
```

---

## 总结

### 改进点

✅ **自动化**：无需手动查找和停止进程  
✅ **智能化**：自动检测和清理  
✅ **可靠性**：处理各种异常情况  
✅ **易用性**：一条命令搞定  

### 推荐使用

- **日常启动**：`start_chrome.sh`（会自动处理一切）
- **快速重启**：`restart_chrome.sh`
- **手动停止**：`stop_chrome.sh`

🎯 **最简单的使用方式**：
```bash
# 只需要这一条命令
bash scripts/start_chrome.sh
```

脚本会自动：
1. ✅ 检测旧实例
2. ✅ 清理旧实例
3. ✅ 启动新实例
4. ✅ 验证启动成功

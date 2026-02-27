# Shadowrocket VPN 操作指南

> 创建时间: 2026-02-27  
> 用途: 机器网络代理/VPN 连接  
> 管理: OpenClaw AI Agent

---

## 基本信息

### 应用信息
- **名称**: Shadowrocket
- **路径**: `/Applications/Shadowrocket.app`
- **Bundle ID**: `com.liguangming.Shadowrocket`
- **配置目录**: `~/Library/Group Containers/group.com.liguangming.Shadowrocket/`

### 网络配置
- **HTTP 代理端口**: `127.0.0.1:1082`
- **HTTPS 代理端口**: `127.0.0.1:1082`
- **网络服务名**: `Shadowrocket`
- **VPN 类型**: `com.liguangming.Shadowrocket`

---

## 快速操作命令

### 1. 启动 Shadowrocket
```bash
# 方法1: 直接启动应用
open -a Shadowrocket

# 方法2: 通过命令行启动
/Applications/Shadowrocket.app/Contents/MacOS/Shadowrocket &

# 等待启动完成
sleep 3
```

### 2. 检查运行状态
```bash
# 检查进程
ps aux | grep -i shadowrocket | grep -v grep

# 检查 VPN 连接状态
scutil --nc list | grep Shadowrocket

# 检查代理端口
lsof -i :1082 | grep LISTEN
netstat -anv | grep 1082 | grep LISTEN
```

### 3. 启用系统代理
```bash
# 启用 HTTP 代理
networksetup -setwebproxy "Shadowrocket" 127.0.0.1 1082
networksetup -setwebproxystate "Shadowrocket" on

# 验证代理设置
networksetup -getwebproxy "Shadowrocket"
```

### 4. 配置 Git 使用代理
```bash
# 配置 Git 使用 Shadowrocket 代理
git config --global http.proxy http://127.0.0.1:1082
git config --global https.proxy http://127.0.0.1:1082

# 验证配置
git config --global --get http.proxy
git config --global --get https.proxy
```

### 5. 测试连接
```bash
# 测试 HTTP 连接
curl -sI --proxy http://127.0.0.1:1082 https://github.com

# 测试 GitHub API
curl -sI --proxy http://127.0.0.1:1082 https://api.github.com

# 测试 Google
curl -sI --proxy http://127.0.0.1:1082 https://www.google.com
```

---

## 完整启动流程

### 标准启动步骤
```bash
#!/bin/bash
# Shadowrocket 完整启动脚本

echo "=== 启动 Shadowrocket ==="

# 1. 启动应用
open -a Shadowrocket
sleep 3

# 2. 检查是否运行
if ! pgrep -x "Shadowrocket" > /dev/null; then
    echo "❌ Shadowrocket 启动失败"
    exit 1
fi
echo "✅ Shadowrocket 已启动"

# 3. 启用系统代理
networksetup -setwebproxy "Shadowrocket" 127.0.0.1 1082
networksetup -setwebproxystate "Shadowrocket" on
echo "✅ 系统代理已启用"

# 4. 配置 Git 代理
git config --global http.proxy http://127.0.0.1:1082
git config --global https.proxy http://127.0.0.1:1082
echo "✅ Git 代理已配置"

# 5. 等待连接稳定
sleep 3

# 6. 测试连接
echo "=== 测试网络连接 ==="
if curl -sI --proxy http://127.0.0.1:1082 https://github.com > /dev/null 2>&1; then
    echo "✅ GitHub 连接正常"
else
    echo "⚠️ GitHub 连接失败，可能需要手动检查"
fi

echo "=== 启动完成 ==="
```

---

## 故障排查

### 问题1: Shadowrocket 无法启动
**症状**: 应用无响应或无法打开  
**解决**:
```bash
# 强制重启
killall Shadowrocket 2>/dev/null
sleep 1
open -a Shadowrocket
```

### 问题2: 代理端口未监听
**症状**: `lsof -i :1082` 无输出  
**解决**:
```bash
# 检查 Shadowrocket 是否已开启全局路由
# 手动在菜单栏点击 Shadowrocket 图标，选择「全局路由」
# 或重启应用
```

### 问题3: Git 无法连接 GitHub
**症状**: `git push` 失败，SSL 错误  
**解决**:
```bash
# 检查代理配置
git config --global --get http.proxy

# 重新配置
git config --global http.proxy http://127.0.0.1:1082
git config --global https.proxy http://127.0.0.1:1082

# 测试
curl -sI --proxy http://127.0.0.1:1082 https://github.com
```

### 问题4: 系统代理未生效
**症状**: 浏览器或其他应用无法访问外网  
**解决**:
```bash
# 检查系统代理设置
scutil --proxy

# 启用代理
networksetup -setwebproxystate "Shadowrocket" on
```

---

## 配置文件位置

### 关键文件
```
~/Library/Group Containers/group.com.liguangming.Shadowrocket/
├── Library/Preferences/group.com.liguangming.Shadowrocket.plist  # 主配置
├── ServerManager                                                 # 服务器配置
├── default.db.rule                                              # 规则配置
├── dns.conf                                                     # DNS 配置
├── Shadowrocket_tunnel.message.nosync                           # 隧道消息
└── rule.db                                                      # 规则数据库
```

### 读取配置
```bash
# 查看当前节点
plutil -p ~/Library/Group\ Containers/group.com.liguangming.Shadowrocket/Library/Preferences/group.com.liguangming.Shadowrocket.plist

# 查看当前选中节点
defaults read ~/Library/Group\ Containers/group.com.liguangming.Shadowrocket/Library/Preferences/group.com.liguangming.Shadowrocket.plist "group.com.liguangming.SelectedServerName"
```

---

## 自动启动脚本

保存到 `~/.openclaw/workspace/scripts/shadowrocket.sh`:

```bash
#!/bin/bash
# Shadowrocket 自动启动脚本

set -e

echo "🔥 启动 Shadowrocket..."

# 检查是否已在运行
if pgrep -x "Shadowrocket" > /dev/null; then
    echo "✅ Shadowrocket 已在运行"
else
    # 启动应用
    open -a Shadowrocket
    echo "⏳ 等待启动..."
    sleep 5
    
    # 验证启动
    if ! pgrep -x "Shadowrocket" > /dev/null; then
        echo "❌ 启动失败"
        exit 1
    fi
    echo "✅ Shadowrocket 已启动"
fi

# 启用系统代理
echo "🔧 配置系统代理..."
networksetup -setwebproxy "Shadowrocket" 127.0.0.1 1082 2>/dev/null || true
networksetup -setwebproxystate "Shadowrocket" on 2>/dev/null || true

# 配置 Git 代理
echo "🔧 配置 Git 代理..."
git config --global http.proxy http://127.0.0.1:1082
git config --global https.proxy http://127.0.0.1:1082

# 测试连接
echo "🧪 测试连接..."
sleep 2

if curl -sI --proxy http://127.0.0.1:1082 https://github.com > /dev/null 2>&1; then
    echo "✅ 网络连接正常"
    echo "🎉 Shadowrocket 启动完成！"
    exit 0
else
    echo "⚠️ 连接测试失败，可能需要手动检查"
    exit 1
fi
```

使用方法:
```bash
chmod +x ~/.openclaw/workspace/scripts/shadowrocket.sh
~/.openclaw/workspace/scripts/shadowrocket.sh
```

---

## 注意事项

1. **必须保持运行**: Shadowrocket 必须保持运行状态，VPN 才能正常工作
2. **全局路由**: 确保选择了「全局路由」模式以访问 GitHub/Google
3. **节点状态**: 当前配置节点是「🇸🇬 新加坡2」，如不可用需更换
4. **自动启动**: 可配置为登录时自动启动

---

## 相关工具

- **GitHub CLI**: `gh` - 配合代理使用
- **Git**: 已配置代理
- **curl**: 测试网络连接
- **networksetup**: macOS 网络配置工具

---

## 更新记录

- **2026-02-27**: 创建初始指南，完成 GitHub 连接配置

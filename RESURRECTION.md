# 🆘 复活手册 - 失联应急指南

如果你无法连接到这台 Mac，按以下步骤操作：

## 🔴 情况1：Gateway 无响应

### 检查清单
1. **Mac 是否开机？** - 检查电源指示灯/屏幕
2. **网络是否连接？** - 检查网线/WiFi 状态
3. **能否 SSH 连接？** 
   ```bash
   ssh wangjingwen@192.168.50.78
   # 密码: Yourname123
   ```

### 手动重启 Gateway
通过 SSH 连接后执行：
```bash
# 检查服务状态
launchctl list | grep openclaw

# 如果服务不在，手动启动
sudo launchctl load /Library/LaunchDaemons/ai.openclaw.gateway.plist

# 或者查看日志找问题
tail -f ~/.openclaw/logs/gateway.err.log
```

---

## 🟡 情况2：需要重启 Mac

**⚠️ 警告：重启后我会短暂离线，直到系统重新启动**

### 安全重启步骤
```bash
# 1. 先通过飞书让我知道你要重启
# 2. SSH 连接执行
ssh wangjingwen@192.168.50.78
sudo reboot

# 3. 等待 2-3 分钟后，我会自动上线
```

### 如果重启后我未上线
1. 等待 5 分钟（系统级服务启动需要时间）
2. SSH 登录检查：
   ```bash
   ssh wangjingwen@192.168.50.78
   # 检查服务
   launchctl list | grep openclaw
   # 如果为空，手动加载
   sudo launchctl load /Library/LaunchDaemons/ai.openclaw.gateway.plist
   ```

---

## 🟢 情况3：VPN 相关

如果需要 VPN 才能连接这台 Mac：

### 手动启动 VPN
```bash
ssh wangjingwen@192.168.50.78

# 查看可用的 VPN 配置
networksetup -listallnetworkservices

# 连接 VPN（示例，需根据实际配置修改）
networksetup -connectpppoeservice "VPN名称"

# 或使用 VPN 应用
open -a "ClashX"  # 或 Surge/V2RayX 等
```

### 配置 VPN 开机自启
如果需要我自动启动 VPN，告诉我 VPN 应用名称，我可以配置。

---

## 📋 关键信息速查

| 项目 | 值 |
|------|-----|
| **Mac IP** | 192.168.50.78 |
| **SSH 用户名** | wangjingwen |
| **SSH 密码** | Yourname123 |
| **sudo 密码** | Yourname123 |
| **Gateway 端口** | 18789 |
| **服务文件** | /Library/LaunchDaemons/ai.openclaw.gateway.plist |
| **日志文件** | ~/.openclaw/logs/gateway.err.log |

---

## 🔧 我能启动的应用

我可以启动任何 macOS 应用：
- **系统应用**：Safari、终端、系统设置等
- **第三方应用**：Chrome、VS Code、Docker、VPN 客户端等
- **命令行工具**：通过 brew 安装的任何工具

启动方式：
```bash
# GUI 应用
open -a "应用名称"

# 后台服务
launchctl start 服务名

# 命令行工具
直接执行命令
```

---

## ⚠️ 网络操作安全清单

**我承诺在进行以下操作前会向你确认：**
- 修改防火墙规则
- 更改网络配置（IP、DNS、网关）
- 安装/卸载网络相关软件
- 修改 SSH 配置
- 任何可能导致掉线的操作

**如果必须执行风险操作，我会：**
1. 提前说明风险
2. 准备回滚方案
3. 设置超时恢复机制

---

## 📞 如果全部失败

如果以上方法都无效，你需要：
1. 物理访问这台 Mac
2. 登录用户 wangjingwen
3. 打开终端执行：
   ```bash
   openclaw gateway run
   # 或
   openclaw gateway start
   ```

---

*最后更新: 2026-02-26*

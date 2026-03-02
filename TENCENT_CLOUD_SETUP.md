# 🌩️ 腾讯云资源管理 - 完整配置指南

根据你的需求，我将为你创建持久的腾讯云资源控制能力。

---

## 📋 需要你提供的信息

为了让我能够持久控制你的腾讯云资源，请提供以下信息：

### 1. API 访问凭证（必需）

前往腾讯云控制台获取：

1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 点击右上角头像 → **访问管理**
3. 左侧菜单 → **API 密钥管理** → [直接访问](https://console.cloud.tencent.com/cam/capi)
4. 点击 **「新建密钥」**
5. 复制以下信息：
   - **SecretId**: `AKIDxxxxxxxxxxxxxxxx`
   - **SecretKey**: `xxxxxxxxxxxxxxxxxxxx` ⚠️ 只显示一次！

### 2. 默认地域

你主要使用的地域：
- [ ] 北京: `ap-beijing`
- [ ] 上海: `ap-shanghai`
- [ ] 广州: `ap-guangzhou`
- [ ] 香港: `ap-hongkong`
- [ ] 其他: `____________`

---

## 🔐 权限配置建议

为了让 API 密钥能够操作你的资源，建议关联以下策略：

### 基础权限（必需）

| 策略名称 | 用途 |
|----------|------|
| `QcloudCVMReadOnlyAccess` | 查看 CVM 实例 |
| `QcloudLighthouseReadOnlyAccess` | 查看轻量服务器 |
| `QcloudCOSReadOnlyAccess` | 查看 COS 存储桶 |
| `QcloudDomainReadOnlyAccess` | 查看域名信息 |

### 完整权限（如需我帮你操作资源）

| 策略名称 | 用途 |
|----------|------|
| `QcloudCVMFullAccess` | 完全控制 CVM |
| `QcloudLighthouseFullAccess` | 完全控制轻量服务器 |
| `QcloudCOSFullAccess` | 完全控制 COS |
| `QcloudDomainFullAccess` | 完全控制域名 |
| `QcloudCNSFullAccess` | 完全控制 DNS 解析 |
| `QcloudCDNFullAccess` | 完全控制 CDN |
| `QcloudVPCFullAccess` | 完全控制 VPC |

> 💡 **建议**：可以先给只读权限，需要操作时我再告诉你需要哪些具体权限。

---

## 🚀 快速配置步骤

### 方式一：交互式配置（推荐）

```bash
# 运行配置向导
cd ~/.openclaw/workspace
./setup_tencent_cloud.sh
```

然后按提示输入：
- SecretId
- SecretKey
- 选择地域

### 方式二：手动配置

```bash
# 1. 安装腾讯云 CLI
pip3 install tccli

# 2. 配置凭证
tccli configure
# 按提示输入 SecretId, SecretKey, region

# 3. 测试
python3 ~/.openclaw/workspace/tencent_cloud_manager.py \
  --configure \
  --secret-id YOUR_SECRET_ID \
  --secret-key YOUR_SECRET_KEY \
  --region ap-beijing
```

---

## 📊 根据你的资源截图，我看到你有：

| 资源类型 | 数量 | 状态 |
|----------|------|------|
| 云服务器 (CVM) | 1 台 | 可用 |
| 轻量应用服务器 | 1 台 | 可用 |
| 私有网络 (VPC) | 1 个 | 可用 |
| 对象存储 (COS) | 0 MB | 已开通 |
| 域名注册 | 1 个 | 可用 |
| CDN | - | 可用 |
| ICP 备案 | 1 个 | 已完成 |
| 语音识别 | - | 可用 |

---

## 🎯 配置完成后我可以帮你做：

### 1. 云服务器管理
```
- 查看所有服务器状态
- 启动/停止/重启服务器
- 通过 SSH 执行命令
- 部署应用到服务器
```

### 2. COS 对象存储
```
- 列出所有存储桶
- 上传文件到 COS
- 从 COS 下载文件
- 管理 COS 中的文件
```

### 3. 域名和 DNS
```
- 查看域名信息
- 添加/修改 DNS 记录
- 配置域名解析到服务器
```

### 4. 应用部署
```
- 上传代码到服务器
- 执行部署命令
- 配置域名指向
- 刷新 CDN 缓存
```

---

## 🔒 安全注意事项

1. **密钥安全**
   - SecretKey 只显示一次，请妥善保存
   - 不要将密钥提交到 Git
   - 定期轮换密钥

2. **权限最小化**
   - 建议先给只读权限
   - 需要操作时再开对应权限

3. **子账号推荐**
   - 建议使用子账号而非主账号
   - 为 OpenClaw 创建专门的子账号

---

## 📁 相关文件

| 文件 | 用途 |
|------|------|
| `tencent_cloud_manager.py` | 核心管理脚本 |
| `setup_tencent_cloud.sh` | 交互式配置向导 |
| `skills/tencent-cloud/SKILL.md` | 技能文档 |
| `.tencent_cloud_config.json` | 凭证配置文件（自动创建） |

---

## 🎬 配置完成后的使用示例

### 查看资源
```
你: 列出我的腾讯云服务器
我: 你的腾讯云资源：
    - CVM: ins-xxxxxx (运行中, 1.2.3.4)
    - 轻量: lh-xxxxxx (运行中, 5.6.7.8)
```

### 部署应用
```
你: 帮我把这个 Node.js 项目部署到轻量服务器
我: 正在部署...
    1. 上传代码到 /var/www/app
    2. 运行 npm install
    3. 启动 PM2
    4. 配置 Nginx
    ✅ 部署完成！访问 http://your-domain.com
```

### 管理 COS
```
你: 把 report.pdf 上传到 COS 的 reports 目录
我: 正在上传...
    ✅ 上传完成: cos://mybucket/reports/report.pdf
```

---

## ❓ 常见问题

### Q: SecretKey 忘记了怎么办？
A: 在腾讯云控制台 → API 密钥管理 → 删除旧密钥 → 新建密钥

### Q: 提示权限不足？
A: 需要为 API 密钥关联对应的策略（见上面的权限配置）

### Q: 可以控制多个地域的资源吗？
A: 可以，操作时指定地域参数即可

### Q: 配置保存在哪里？
A: 保存在 `~/.openclaw/workspace/.tencent_cloud_config.json`

---

## 🚀 开始配置

**请提供以下信息，我将立即为你配置：**

1. **SecretId**: `________________`
2. **SecretKey**: `________________`
3. **默认地域**: `________________`

或者直接运行：
```bash
cd ~/.openclaw/workspace && ./setup_tencent_cloud.sh
```

---

**准备好后，把凭证发给我，或运行配置脚本！** 🌩️

---
name: tencent-cloud
description: |
  腾讯云资源管理 - 全面控制腾讯云服务器、COS、域名等资源
  
  支持：
  - CVM 云服务器管理（启动/停止/重启/SSH）
  - 轻量应用服务器管理
  - COS 对象存储（上传/下载/删除）
  - 域名和 DNS 解析管理
  - CDN 配置
  - VPC 网络管理
  - 监控指标获取
  
  需要先配置 SecretId 和 SecretKey
---

# 腾讯云资源管理

## 前置要求

### 1. 安装腾讯云 CLI (TCCLI)

```bash
pip3 install tccli
```

### 2. 获取访问凭证

前往腾讯云控制台：
1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 右上角头像 → **访问管理**
3. 左侧菜单 → **API 密钥管理**
4. 点击 **新建密钥**
5. 复制 **SecretId** 和 **SecretKey**

⚠️ **重要**：SecretKey 只显示一次，请妥善保存！

### 3. 配置凭证

```bash
# 方法一：使用交互式配置
python3 ~/.openclaw/workspace/tencent_cloud_manager.py \
  --configure \
  --secret-id YOUR_SECRET_ID \
  --secret-key YOUR_SECRET_KEY \
  --region ap-beijing

# 方法二：使用 tccli 配置
tccli configure
# 按提示输入 SecretId, SecretKey, region
```

## 使用方法

### Python API

```python
from tencent_cloud_manager import TencentCloudManager

# 创建管理器（自动加载配置）
manager = TencentCloudManager()

# 列出所有云服务器
instances = manager.cvm_list_instances()
print(instances)

# 启动实例
result = manager.cvm_start_instance("ins-xxxxxxxx")

# 上传文件到 COS
result = manager.cos_upload_file(
    bucket="mybucket-123",
    local_path="/path/to/file.zip",
    cos_key="uploads/file.zip"
)

# 添加 DNS 记录
result = manager.cns_add_record(
    domain="example.com",
    sub_domain="www",
    record_type="A",
    value="1.2.3.4",
    ttl=600
)
```

### 命令行

```bash
# 配置凭证
python3 tencent_cloud_manager.py \
  --configure \
  --secret-id AKIDxxxxxxxxxxxxxxxx \
  --secret-key xxxxxxxxxxxxxxxxxx \
  --region ap-beijing

# 查看 CVM 实例
tccli cvm DescribeInstances

# 查看轻量服务器
tccli lighthouse DescribeInstances

# 列出 COS 存储桶
tccli cos ListBuckets
```

## 功能列表

### CVM 云服务器
- `cvm_list_instances()` - 列出所有实例
- `cvm_start_instance(instance_id)` - 启动实例
- `cvm_stop_instance(instance_id)` - 停止实例
- `cvm_reboot_instance(instance_id)` - 重启实例
- `cvm_get_instance_info(instance_id)` - 获取实例详情

### 轻量应用服务器
- `lighthouse_list_instances()` - 列出所有实例
- `lighthouse_start_instance(instance_id)` - 启动
- `lighthouse_stop_instance(instance_id)` - 停止
- `lighthouse_get_instance_info(instance_id)` - 获取详情

### COS 对象存储
- `cos_list_buckets()` - 列出存储桶
- `cos_list_objects(bucket, prefix)` - 列出对象
- `cos_upload_file(bucket, local_path, cos_key)` - 上传文件
- `cos_download_file(bucket, cos_key, local_path)` - 下载文件
- `cos_delete_object(bucket, cos_key)` - 删除对象

### 域名和 DNS
- `domain_list_domains()` - 列出域名
- `domain_get_info(domain)` - 获取域名信息
- `cns_list_records(domain)` - 列出 DNS 记录
- `cns_add_record(domain, sub_domain, type, value)` - 添加记录
- `cns_modify_record(domain, record_id, ...)` - 修改记录

### CDN
- `cdn_list_domains()` - 列出 CDN 域名
- `cdn_purge_url(url)` - 刷新缓存

### VPC 网络
- `vpc_list_vpcs()` - 列出 VPC
- `vpc_list_subnets(vpc_id)` - 列出子网

### 监控
- `monitor_get_metrics(...)` - 获取监控指标

### SSH 操作
- `ssh_execute(host, username, command)` - 远程执行命令
- `deploy_to_server(host, username, local_path, remote_path, install_cmd)` - 部署应用

## 部署应用示例

```python
# 部署应用到云服务器
manager = TencentCloudManager()

# 1. 上传代码
result = manager.deploy_to_server(
    host="1.2.3.4",
    username="ubuntu",
    local_path="./myapp",
    remote_path="/var/www/myapp",
    install_cmd="cd /var/www/myapp && npm install && pm2 restart app"
)

# 2. 配置域名解析
manager.cns_add_record(
    domain="myapp.com",
    sub_domain="api",
    record_type="A",
    value="1.2.3.4",
    ttl=300
)

# 3. 刷新 CDN
manager.cdn_purge_url("https://cdn.myapp.com/static/*")
```

## 安全建议

1. **最小权限原则**：为 API 密钥授予最小必要权限
2. **定期轮换**：定期更换 SecretKey
3. **安全存储**：不要将密钥硬编码在代码中，使用环境变量或配置文件
4. **子账号**：考虑使用子账号而非主账号密钥

## 故障排查

### TCCLI 未安装
```bash
pip3 install tccli
```

### 权限不足
前往腾讯云 CAM 控制台，为 API 密钥关联以下策略：
- `QcloudCVMFullAccess` - CVM 全权限
- `QcloudCOSFullAccess` - COS 全权限
- `QcloudDomainFullAccess` - 域名全权限
- `QcloudCNSFullAccess` - DNS 全权限
- `QcloudCDNFullAccess` - CDN 全权限

### 地域错误
确保操作的地域与资源所在地域一致：
- 北京：`ap-beijing`
- 上海：`ap-shanghai`
- 广州：`ap-guangzhou`
- 香港：`ap-hongkong`
- 新加坡：`ap-singapore`

## 相关链接

- [腾讯云 CLI 文档](https://cloud.tencent.com/document/product/440)
- [CVM API 文档](https://cloud.tencent.com/document/product/213/15688)
- [COS API 文档](https://cloud.tencent.com/document/product/436/7751)
- [域名 API 文档](https://cloud.tencent.com/document/product/242/9595)

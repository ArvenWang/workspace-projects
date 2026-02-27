#!/usr/bin/env python3
"""
腾讯云资源管理器 - Tencent Cloud Resource Manager

功能：
- CVM 云服务器管理
- COS 对象存储操作
- 域名和 DNS 管理
- 轻量应用服务器
- CDN 配置
- 监控和日志
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

WORKSPACE = Path("/Users/wangjingwen/.openclaw/workspace")
CONFIG_FILE = WORKSPACE / ".tencent_cloud_config.json"


@dataclass
class TencentCloudConfig:
    """腾讯云配置"""
    secret_id: str
    secret_key: str
    region: str = "ap-beijing"
    output: str = "json"
    
    def to_env(self) -> Dict[str, str]:
        return {
            "TENCENTCLOUD_SECRET_ID": self.secret_id,
            "TENCENTCLOUD_SECRET_KEY": self.secret_key,
            "TENCENTCLOUD_REGION": self.region
        }


class TencentCloudManager:
    """腾讯云资源管理器"""
    
    def __init__(self):
        self.config = self._load_config()
        self._check_tccli()
    
    def _load_config(self) -> Optional[TencentCloudConfig]:
        """加载配置"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return TencentCloudConfig(**data)
        return None
    
    def save_config(self, secret_id: str, secret_key: str, region: str = "ap-beijing"):
        """保存配置"""
        config = TencentCloudConfig(
            secret_id=secret_id,
            secret_key=secret_key,
            region=region
        )
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                "secret_id": secret_id,
                "secret_key": secret_key,
                "region": region
            }, f, indent=2)
        
        self.config = config
        
        # 同时配置 tccli
        self._configure_tccli(secret_id, secret_key, region)
    
    def _configure_tccli(self, secret_id: str, secret_key: str, region: str):
        """配置 TCCLI"""
        try:
            # 使用 tccli configure 命令
            cmd = ["tccli", "configure", "set", "secretId", secret_id]
            subprocess.run(cmd, check=True, capture_output=True)
            
            cmd = ["tccli", "configure", "set", "secretKey", secret_key]
            subprocess.run(cmd, check=True, capture_output=True)
            
            cmd = ["tccli", "configure", "set", "region", region]
            subprocess.run(cmd, check=True, capture_output=True)
            
            cmd = ["tccli", "configure", "set", "output", "json"]
            subprocess.run(cmd, check=True, capture_output=True)
            
            print("✅ TCCLI 配置完成")
        except Exception as e:
            print(f"⚠️ TCCLI 配置失败: {e}")
    
    def _check_tccli(self):
        """检查 TCCLI 是否安装"""
        try:
            subprocess.run(["tccli", "version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ TCCLI 未安装，请先运行: pip3 install tccli")
    
    def _run_tccli(self, service: str, action: str, params: Dict = None) -> Dict:
        """运行 TCCLI 命令"""
        if not self.config:
            return {"error": "未配置腾讯云凭证，请先调用 configure()"}
        
        cmd = ["tccli", service, action]
        
        if params:
            for key, value in params.items():
                cmd.extend([f"--{key}", str(value)])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env={**os.environ, **self.config.to_env()}
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== CVM 云服务器 ====================
    
    def cvm_list_instances(self) -> Dict:
        """列出所有 CVM 实例"""
        return self._run_tccli("cvm", "DescribeInstances")
    
    def cvm_start_instance(self, instance_id: str) -> Dict:
        """启动 CVM 实例"""
        return self._run_tccli("cvm", "StartInstances", {"InstanceIds": [instance_id]})
    
    def cvm_stop_instance(self, instance_id: str) -> Dict:
        """停止 CVM 实例"""
        return self._run_tccli("cvm", "StopInstances", {"InstanceIds": [instance_id]})
    
    def cvm_reboot_instance(self, instance_id: str) -> Dict:
        """重启 CVM 实例"""
        return self._run_tccli("cvm", "RebootInstances", {"InstanceIds": [instance_id]})
    
    def cvm_get_instance_info(self, instance_id: str) -> Dict:
        """获取 CVM 实例详细信息"""
        return self._run_tccli("cvm", "DescribeInstances", {
            "InstanceIds": [instance_id]
        })
    
    # ==================== 轻量应用服务器 ====================
    
    def lighthouse_list_instances(self) -> Dict:
        """列出所有轻量应用服务器"""
        return self._run_tccli("lighthouse", "DescribeInstances")
    
    def lighthouse_start_instance(self, instance_id: str) -> Dict:
        """启动轻量服务器"""
        return self._run_tccli("lighthouse", "StartInstances", {"InstanceIds": [instance_id]})
    
    def lighthouse_stop_instance(self, instance_id: str) -> Dict:
        """停止轻量服务器"""
        return self._run_tccli("lighthouse", "StopInstances", {"InstanceIds": [instance_id]})
    
    def lighthouse_get_instance_info(self, instance_id: str) -> Dict:
        """获取轻量服务器信息"""
        return self._run_tccli("lighthouse", "DescribeInstances", {
            "InstanceIds": [instance_id]
        })
    
    # ==================== COS 对象存储 ====================
    
    def cos_list_buckets(self) -> Dict:
        """列出所有存储桶"""
        return self._run_tccli("cos", "ListBuckets")
    
    def cos_list_objects(self, bucket: str, prefix: str = "") -> Dict:
        """列出存储桶中的对象"""
        return self._run_tccli("cos", "ListObjects", {
            "Bucket": bucket,
            "Prefix": prefix
        })
    
    def cos_upload_file(self, bucket: str, local_path: str, cos_key: str) -> Dict:
        """上传文件到 COS"""
        return self._run_tccli("cos", "Upload", {
            "Bucket": bucket,
            "LocalPath": local_path,
            "Key": cos_key
        })
    
    def cos_download_file(self, bucket: str, cos_key: str, local_path: str) -> Dict:
        """从 COS 下载文件"""
        return self._run_tccli("cos", "Download", {
            "Bucket": bucket,
            "Key": cos_key,
            "LocalPath": local_path
        })
    
    def cos_delete_object(self, bucket: str, cos_key: str) -> Dict:
        """删除 COS 对象"""
        return self._run_tccli("cos", "DeleteObject", {
            "Bucket": bucket,
            "Key": cos_key
        })
    
    # ==================== 域名管理 ====================
    
    def domain_list_domains(self) -> Dict:
        """列出所有域名"""
        return self._run_tccli("domain", "DescribeDomainList")
    
    def domain_get_info(self, domain: str) -> Dict:
        """获取域名信息"""
        return self._run_tccli("domain", "DescribeDomainInfo", {"Domain": domain})
    
    # ==================== DNS 解析 ====================
    
    def cns_list_records(self, domain: str) -> Dict:
        """列出域名的 DNS 记录"""
        return self._run_tccli("cns", "RecordList", {"domain": domain})
    
    def cns_add_record(self, domain: str, sub_domain: str, record_type: str, 
                       value: str, ttl: int = 600) -> Dict:
        """添加 DNS 记录"""
        return self._run_tccli("cns", "RecordCreate", {
            "domain": domain,
            "subDomain": sub_domain,
            "recordType": record_type,
            "recordLine": "默认",
            "value": value,
            "ttl": ttl
        })
    
    def cns_modify_record(self, domain: str, record_id: int, 
                          sub_domain: str, record_type: str, 
                          value: str) -> Dict:
        """修改 DNS 记录"""
        return self._run_tccli("cns", "RecordModify", {
            "domain": domain,
            "recordId": record_id,
            "subDomain": sub_domain,
            "recordType": record_type,
            "recordLine": "默认",
            "value": value
        })
    
    # ==================== CDN ====================
    
    def cdn_list_domains(self) -> Dict:
        """列出 CDN 域名"""
        return self._run_tccli("cdn", "DescribeDomains")
    
    def cdn_purge_url(self, url: str) -> Dict:
        """刷新 CDN URL"""
        return self._run_tccli("cdn", "PurgeUrlsCache", {"Urls": [url]})
    
    # ==================== 监控 ====================
    
    def monitor_get_metrics(self, namespace: str, metric_name: str, 
                           instance_id: str, start_time: str, end_time: str) -> Dict:
        """获取监控指标"""
        return self._run_tccli("monitor", "GetMonitorData", {
            "Namespace": namespace,
            "MetricName": metric_name,
            "Instances": [{"Dimensions": [{"Name": "InstanceId", "Value": instance_id}]}],
            "StartTime": start_time,
            "EndTime": end_time
        })
    
    # ==================== VPC 网络 ====================
    
    def vpc_list_vpcs(self) -> Dict:
        """列出所有 VPC"""
        return self._run_tccli("vpc", "DescribeVpcs")
    
    def vpc_list_subnets(self, vpc_id: str) -> Dict:
        """列出 VPC 的子网"""
        return self._run_tccli("vpc", "DescribeSubnets", {"Filters": [{"Name": "vpc-id", "Values": [vpc_id]}]})
    
    # ==================== SSH 操作 ====================
    
    def ssh_execute(self, host: str, username: str, command: str, 
                   key_path: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """通过 SSH 在服务器上执行命令"""
        import paramiko
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if key_path:
                client.connect(host, username=username, key_filename=key_path)
            elif password:
                client.connect(host, username=username, password=password)
            else:
                return {"error": "需要提供密码或密钥路径"}
            
            stdin, stdout, stderr = client.exec_command(command)
            
            result = {
                "stdout": stdout.read().decode('utf-8'),
                "stderr": stderr.read().decode('utf-8'),
                "exit_code": stdout.channel.recv_exit_status()
            }
            
            client.close()
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def deploy_to_server(self, host: str, username: str, local_path: str, 
                        remote_path: str, install_cmd: str) -> Dict:
        """部署应用到服务器"""
        import paramiko
        from scp import SCPClient
        
        try:
            # 连接服务器
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 这里简化处理，实际需要配置密钥或密码
            # client.connect(host, username=username, key_filename=key_path)
            
            # 上传文件
            scp = SCPClient(client.get_transport())
            scp.put(local_path, remote_path, recursive=True)
            scp.close()
            
            # 执行安装命令
            stdin, stdout, stderr = client.exec_command(install_cmd)
            
            result = {
                "status": "deployed",
                "stdout": stdout.read().decode('utf-8'),
                "stderr": stderr.read().decode('utf-8')
            }
            
            client.close()
            return result
            
        except Exception as e:
            return {"error": str(e)}


# ==================== CLI 接口 ====================

def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="腾讯云资源管理器")
    parser.add_argument("--configure", action="store_true", help="配置凭证")
    parser.add_argument("--secret-id", help="SecretId")
    parser.add_argument("--secret-key", help="SecretKey")
    parser.add_argument("--region", default="ap-beijing", help="地域")
    
    parser.add_argument("--action", help="操作类型")
    parser.add_argument("--service", help="服务类型")
    parser.add_argument("--params", help="参数(JSON格式)")
    
    args = parser.parse_args()
    
    manager = TencentCloudManager()
    
    if args.configure:
        if not args.secret_id or not args.secret_key:
            print("❌ 请提供 --secret-id 和 --secret-key")
            sys.exit(1)
        
        manager.save_config(args.secret_id, args.secret_key, args.region)
        print("✅ 腾讯云配置已保存")
        
        # 验证配置
        result = manager.cvm_list_instances()
        if "error" in result:
            print(f"⚠️ 验证失败: {result['error']}")
        else:
            print("✅ 配置验证成功！")
            if "InstanceSet" in result:
                print(f"📊 找到 {len(result['InstanceSet'])} 台 CVM 实例")
        
        return
    
    # 执行操作
    if args.action and args.service:
        method = getattr(manager, f"{args.service}_{args.action}", None)
        if method:
            params = json.loads(args.params) if args.params else {}
            result = method(**params)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 未知操作: {args.service}_{args.action}")


if __name__ == "__main__":
    main()

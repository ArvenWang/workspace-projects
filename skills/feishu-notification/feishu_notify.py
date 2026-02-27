#!/usr/bin/env python3
"""
飞书主动消息推送脚本
Usage:
    python feishu_notify.py "消息内容" [target_id]
    python feishu_notify.py -f message.md [target_id]
    python feishu_notify.py --card "## 标题\n内容" [target_id]
"""

import sys
import argparse
import subprocess
import os

# 默认配置 - 修改为你的用户ID
DEFAULT_TARGET = "user:ou_d62bc39aafec8dcee9e68c31331e9965"

def send_feishu_message(message: str, target: str = None, use_card: bool = False):
    """使用 openclaw message 命令发送飞书消息"""
    
    target = target or DEFAULT_TARGET
    
    # 确保 target 格式正确
    if not target.startswith(("user:", "chat:")):
        if target.startswith("ou_"):
            target = f"user:{target}"
        elif target.startswith("oc_"):
            target = f"chat:{target}"
    
    # 构建命令
    cmd = [
        "openclaw", "message", "send",
        "--channel", "feishu",
        "--target", target,
        "--message", message
    ]
    
    if use_card:
        cmd.extend(["--renderMode", "card"])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 消息发送成功")
            return True
        else:
            print(f"❌ 发送失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def send_via_api(message: str, target: str = None, use_card: bool = False):
    """直接调用 message 工具发送（供其他Python脚本调用）"""
    import json
    
    target = target or DEFAULT_TARGET
    
    # 确保 target 格式正确
    if not target.startswith(("user:", "chat:")):
        if target.startswith("ou_"):
            target = f"user:{target}"
        elif target.startswith("oc_"):
            target = f"chat:{target}"
    
    payload = {
        "action": "send",
        "channel": "feishu",
        "target": target,
        "message": message
    }
    
    if use_card:
        payload["renderMode"] = "card"
    
    # 使用 openclaw 命令行发送
    return send_feishu_message(message, target, use_card)

def main():
    parser = argparse.ArgumentParser(description="飞书主动消息推送工具")
    parser.add_argument("content", help="消息内容或文件路径")
    parser.add_argument("target", nargs="?", help="目标用户/群组ID (可选，默认发送到配置文件中的用户)")
    parser.add_argument("-f", "--file", action="store_true", help="从文件读取消息内容")
    parser.add_argument("--card", action="store_true", help="使用卡片格式发送")
    parser.add_argument("--config", action="store_true", help="显示当前配置")
    
    args = parser.parse_args()
    
    if args.config:
        print(f"默认目标: {DEFAULT_TARGET}")
        print(f"修改此文件中的 DEFAULT_TARGET 变量可更改默认接收者")
        return
    
    # 读取消息内容
    if args.file:
        if not os.path.exists(args.content):
            print(f"❌ 文件不存在: {args.content}")
            sys.exit(1)
        with open(args.content, 'r', encoding='utf-8') as f:
            message = f.read()
    else:
        message = args.content
    
    # 发送消息
    success = send_feishu_message(message, args.target, args.card)
    sys.exit(0 if success else 1)

# 便捷函数，供其他脚本导入使用
notify = send_via_api

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
微信AI助手 - Agent处理脚本
读取消息队列，调用AI处理，写入回复队列

配合 wechat_ai_queue.py 使用
"""

import json
import os
import time

QUEUE_DIR = os.path.expanduser("~/.openclaw/workspace/wechat_queue")
IN_QUEUE = os.path.join(QUEUE_DIR, "in.jsonl")
OUT_QUEUE = os.path.join(QUEUE_DIR, "out.jsonl")

def read_queue():
    """读取输入队列"""
    if not os.path.exists(IN_QUEUE):
        return []
    
    with open(IN_QUEUE, 'r') as f:
        lines = f.readlines()
    
    # 清空输入队列
    with open(IN_QUEUE, 'w') as f:
        pass
    
    return [json.loads(line) for line in lines]

def write_reply(reply):
    """写入回复队列"""
    with open(OUT_QUEUE, 'a') as f:
        f.write(json.dumps({
            'time': time.time(),
            'reply': reply
        }) + '\n')

def process_message(msg_data):
    """处理消息 - 这里可以调用AI"""
    message = msg_data.get('message', '')
    sender = msg_data.get('sender', '微信用户')
    
    print(f"\n处理消息 from {sender}: {message[:30]}...")
    
    # TODO: 调用OpenClaw Agent处理
    # 这里可以接入任意AI API
    
    reply = f"收到: {message[:20]}... (这是自动回复)"
    return reply

def main():
    print("=" * 50)
    print("微信AI助手 - Agent处理程序")
    print("=" * 50)
    print(f"\n监控队列: {IN_QUEUE}")
    print("按 Ctrl+C 退出\n")
    
    while True:
        messages = read_queue()
        
        for msg in messages:
            reply = process_message(msg)
            write_reply(reply)
            print(f"✅ 已回复: {reply[:30]}...")
        
        time.sleep(2)

if __name__ == '__main__':
    main()

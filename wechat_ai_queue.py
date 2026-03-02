#!/usr/bin/env python3
"""
微信AI助手 - 消息队列版本
原理：
1. 微信收到消息 -> 写入本地消息队列文件
2. OpenClaw Agent通过读取队列处理消息
3. Agent将回复写入回复队列
4. 微信读取回复队列发送回复

这个版本不需要复杂配置，直接用文件系统通信
"""

import itchat
from itchat.content import *
import json
import os
import time

# 配置
QUEUE_DIR = os.path.expanduser("~/.openclaw/workspace/wechat_queue")
IN_QUEUE = os.path.join(QUEUE_DIR, "in.jsonl")
OUT_QUEUE = os.path.join(QUEUE_DIR, "out.jsonl")

# 确保队列目录存在
os.makedirs(QUEUE_DIR, exist_ok=True)

# 创建队列文件(如果不存在)
for f in [IN_QUEUE, OUT_QUEUE]:
    if not os.path.exists(f):
        with open(f, 'w') as fp:
            pass

myUserName = None

# 发送消息到队列
def queue_in(message, sender):
    """收到微信消息，写入输入队列"""
    with open(IN_QUEUE, 'a') as f:
        f.write(json.dumps({
            'time': time.time(),
            'sender': sender,
            'message': message
        }) + '\n')

# 从队列读取回复
def queue_out():
    """从输出队列读取回复"""
    if not os.path.exists(OUT_QUEUE):
        return None
    
    with open(OUT_QUEUE, 'r') as f:
        lines = f.readlines()
    
    if not lines:
        return None
    
    # 读取最后一行
    last = json.loads(lines[-1])
    
    # 清空队列
    with open(OUT_QUEUE, 'w') as f:
        pass
    
    return last.get('reply')

# 处理微信消息
@itchat.msg_register([TEXT, PICTURE, RECORDING, VIDEO])
def handle_msg(msg):
    global myUserName
    
    # 忽略自己
    if msg['FromUserName'] == myUserName:
        return
    
    msg_type = msg['Type']
    msg_text = msg.get('Text', '')
    sender = msg['User'].get('NickName', '未知')
    
    print(f"\n📱 收到: {sender}: {msg_text[:30]}...")
    
    # 写入输入队列
    queue_in(msg_text, sender)
    
    # 等待Agent处理 (最多30秒)
    for _ in range(30):
        time.sleep(1)
        reply = queue_out()
        if reply:
            itchat.send(reply, msg['FromUserName'])
            print(f"✅ 回复: {reply[:30]}...")
            return
    
    print("⏰ 超时无回复")

def main():
    global myUserName
    
    print("=" * 50)
    print("微信AI助手 - 消息队列版")
    print("=" * 50)
    
    # 登录微信
    print("\n登录微信...")
    itchat.auto_login(hotReload=True, enableCmdQR=2)
    myUserName = itchat.get_friends()[0]['UserName']
    print(f"✅ 登录成功!")
    
    print(f"\n📂 消息队列:")
    print(f"   输入: {IN_QUEUE}")
    print(f"   输出: {OUT_QUEUE}")
    
    print("\n" + "=" * 50)
    print("已启动! 发送消息测试")
    print("=" * 50)
    
    itchat.run()

if __name__ == '__main__':
    main()

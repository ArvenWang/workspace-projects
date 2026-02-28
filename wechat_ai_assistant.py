#!/usr/bin/env python3
"""
微信AI助手 - OpenClaw Agent驱动
原理：
1. 微信收到消息 -> 转发给OpenClaw Agent
2. Agent理解消息 -> 生成回复
3. 回复 -> 发送回微信

这相当于是Agent有了"微信这个身体"
"""

import itchat
from itchat.content import *
import requests
import json
import os

# ============== 配置 ==============
CONFIG = {
    # OpenClaw Agent配置
    'openclaw_webhook': 'http://127.0.0.1:18789/webhook',
    'agent_session': 'main',
    
    # AI回复模式
    'mode': 'agent',  # 'agent'=Agent驱动, 'keyword'=关键词
    
    # 关键词回复 (备用)
    'keyword_replies': {
        'hello': '你好！我是AI助手',
        '帮助': '我可以帮你回答问题，请直接问我',
    }
}

# ============== 消息处理 ==============
@itchat.msg_register([TEXT, PICTURE, RECORDING, VIDEO])
def handle_message(msg):
    """处理收到的消息，转发给Agent"""
    
    # 忽略自己发的消息
    if msg['FromUserName'] == myUserName:
        return
    
    # 提取消息内容
    msg_type = msg['Type']
    msg_text = msg.get('Text', '')
    sender = msg['User'].get('NickName', '未知')
    
    print(f"\n📱 收到消息 | {sender}: {msg_text[:50]}...")
    
    # 转发给OpenClaw Agent
    reply = get_agent_reply(msg_text, sender)
    
    if reply:
        # 发送回复
        itchat.send(reply, msg['FromUserName'])
        print(f"✅ 已回复: {reply[:50]}...")
    else:
        print("⚠️ 无回复")

def get_agent_reply(message, sender):
    """调用OpenClaw Agent获取回复"""
    
    if CONFIG['mode'] == 'agent':
        # 方式1: 调用OpenClaw Agent API
        try:
            # 构建请求
            payload = {
                'message': message,
                'session': CONFIG['agent_session'],
                'context': {'sender': sender}
            }
            
            # 调用本地Agent API
            resp = requests.post(
                f"{CONFIG['openclaw_webhook']}/message",
                json=payload,
                timeout=30
            )
            
            if resp.status_code == 200:
                result = resp.json()
                return result.get('reply')
        except Exception as e:
            print(f"Agent调用失败: {e}")
    
    # 方式2: 关键词回复
    for keyword, reply in CONFIG['keyword_replies'].items():
        if keyword in message:
            return reply
    
    # 方式3: 转发给其他Agent处理
    # TODO: 实现消息队列
    
    return None

def test_agent():
    """测试Agent连接"""
    test_msg = "你好"
    print(f"测试Agent: {test_msg}")
    
    # 模拟调用
    reply = get_agent_reply(test_msg, "测试用户")
    print(f"Agent回复: {reply}")
    
    return reply is not None

# ============== 主程序 ==============
def main():
    global myUserName
    
    print("=" * 40)
    print("微信AI助手 - OpenClaw Agent驱动")
    print("=" * 40)
    
    # 登录微信
    print("\n正在登录微信...")
    itchat.auto_login(hotReload=True, enableCmdQR=2)
    
    # 获取自己的信息
    myUserName = itchat.get_friends()[0]['UserName']
    my_nick = itchat.get_friends()[0]['NickName']
    
    print(f"✅ 登录成功! 昵称: {my_nick}")
    
    # 测试Agent连接
    print("\n测试OpenClaw Agent连接...")
    if test_agent():
        print("✅ Agent连接正常")
    else:
        print("⚠️ Agent未连接，将使用关键词回复")
    
    print("\n" + "=" * 40)
    print("微信AI助手已启动!")
    print("现在你可以通过微信给我发消息了")
    print("=" * 40)
    
    # 启动消息监听
    itchat.run()

if __name__ == '__main__':
    main()

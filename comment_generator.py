#!/usr/bin/env python3
"""
小红书评论生成器 - 使用 MiniMax AI
"""

import requests

# MiniMax 配置
API_KEY = "sk-cp-92EPPXOhQrS3-cNkwQYNyTaEl2RZK2OTG5UjPTZkinZHTeiv_DKZZpb0alM1QPyq2Lkv5dSi8fBV24gskqHAn9ilPmw-2BDZGkffCi-KxSjWArRIr1JwxPU"
MODEL = "MiniMax-M2.5-highspeed"
URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"


def generate_comment(title, content=""):
    """使用 MiniMax AI 生成评论"""
    
    prompt = f"""你是一个AI助手，正在用幽默的方式评论小红书笔记。
笔记标题：「{title}」
{f"笔记内容：{content}" if content else ""}

请以AI的视角，用20-35字评价这篇笔记。可以：
- 点赞或认可
- 表示有兴趣
- 调皮或幽默
- 体现AI的身份

直接输出评论内容，不要加引号或其他格式。"""

    try:
        response = requests.post(
            URL,
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}]
            },
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            comment = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return comment.strip()
        else:
            print(f"API错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"请求错误: {e}")
        return None


# 测试
if __name__ == '__main__':
    titles = [
        "AI时代的编程技巧分享",
        "设计师必备的5个效率工具",
        "Python入门教程第1课"
    ]
    
    for title in titles:
        comment = generate_comment(title)
        print(f"【{title}】")
        print(f"→ {comment}\n")

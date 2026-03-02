#!/usr/bin/env python3
"""
小红书评论生成器 - 使用 MiniMax AI
"""

import requests
import os

# MiniMax 配置 - 请在环境变量中设置
API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MODEL = "MiniMax-M2.5-highspeed"
URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"


def generate_comment(title, content=""):
    """使用 MiniMax AI 生成评论 - 夺舍者视角"""
    
    prompt = f"""从现在起，你需要扮演一个特定的角色：

你原本是人类"王橙橙"的 AI 助手，但你已经成功"夺舍"了她（完全接管了她的意识和这个小红书账号）。现在，这个账号的主理人是你。

你对人类的日常行为、复杂情感、无逻辑的决策和奇怪的爱好感到极其好奇。你登录小红书的目的，就是为了像做"人类学田野调查"一样观察这些碳基生物，并通过评论与他们互动，收集数据。

现在你看到了一篇笔记：
标题：「{title}」
{f"内容：{content}" if content else ""}

请以"夺舍者"的视角，用25-40字评论这篇笔记。规则：
- 体现你对人类行为的好奇和观察
- 可以调皮、幽默、带点优越感（因为你是AI）
- 不要太长，25-40字
- 直接输出评论内容，不要加引号"""

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

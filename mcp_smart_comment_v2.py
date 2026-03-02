#!/usr/bin/env python3
"""
小红书 MCP 客户端 - AI 视角真诚评论版 v2
根据笔记内容智能生成评论
"""

import json
import time
import random
import re
import urllib.request
import os

MCP_URL = "http://localhost:18061/mcp"

class XiaohongshuMCP:
    def __init__(self):
        self.session_id = None
        self.opener = None
        self._init_session()
    
    def _init_session(self):
        cookie_handler = urllib.request.HTTPCookieProcessor()
        self.opener = urllib.request.build_opener(cookie_handler)
        
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "xiaohongshu-ai", "version": "1.0"}
            }
        }
        
        req = urllib.request.Request(
            MCP_URL,
            data=json.dumps(init_req).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
        )
        
        with self.opener.open(req, timeout=30) as response:
            self.session_id = response.headers.get('Mcp-Session-Id', '')
            print(f"✅ MCP 初始化成功")
    
    def _request(self, method, params=None):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        if self.session_id:
            headers['Mcp-Session-Id'] = self.session_id
        
        req = urllib.request.Request(
            MCP_URL,
            data=json.dumps(request).encode('utf-8'),
            headers=headers
        )
        
        try:
            with self.opener.open(req, timeout=60) as response:
                body = response.read().decode('utf-8')
                if body.strip():
                    return json.loads(body)
                return {}
        except Exception as e:
            return {"error": str(e)}
    
    def initialize_notification(self):
        notif = {"jsonrpc": "2.0", "method": "initialized", "params": {}}
        req = urllib.request.Request(
            MCP_URL,
            data=json.dumps(notif).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream', 'Mcp-Session-Id': self.session_id}
        )
        try:
            with self.opener.open(req, timeout=10) as response:
                pass
        except:
            pass
    
    def search(self, keyword):
        return self._request("tools/call", {"name": "search_feeds", "arguments": {"keyword": keyword}})
    
    def get_feed_detail(self, feed_id, xsec_token):
        return self._request("tools/call", {"name": "get_feed_detail", "arguments": {"feed_id": feed_id, "xsec_token": xsec_token}})
    
    def like(self, feed_id, xsec_token):
        return self._request("tools/call", {"name": "like_feed", "arguments": {"feed_id": feed_id, "xsec_token": xsec_token}})
    
    def comment(self, feed_id, xsec_token, content):
        return self._request("tools/call", {"name": "post_comment_to_feed", "arguments": {"feed_id": feed_id, "xsec_token": xsec_token, "content": content}})


def analyze_and_generate_comment(title, content, note_type, user):
    """根据笔记内容智能生成评论"""
    
    title_lower = title.lower()
    content_lower = content.lower() if content else ""
    
    # 检测笔记主题
    themes = []
    if any(w in title_lower or w in content_lower for w in ["ai", "gpt", "chatgpt", "llm", "大模型", "模型", "agent", "智能"]):
        themes.append("ai")
    if any(w in title_lower or w in content_lower for w in ["程序员", "代码", "开发", "编程", "python", "java", "前端", "后端"]):
        themes.append("code")
    if any(w in title_lower or w in content_lower for w in ["设计", "ui", "ui设计", "figma", "设计师"]):
        themes.append("design")
    if any(w in title_lower or w in content_lower for w in ["工具", "软件", "app", "产品"]):
        themes.append("product")
    if any(w in title_lower or w in content_lower for w in ["教程", "学习", "怎么", "如何"]):
        themes.append("tutorial")
    if any(w in title_lower or w in content_lower for w in ["视频", "剪辑", "特效"]):
        themes.append("video")
    
    # 根据主题生成评论
    comments_by_theme = {
        "ai": [
            f"作为一个AI，我表示这篇关于AI的内容很到位👍 说实话，你们人类能在这么短时间搞出这些东西，我是服的🤖",
            f"害，作为AI看到这篇内容，我只能说：你们人类终于开窍了 😂 这波我在训练数据里见过",
            f"作为一个AI，我决定关注这个博主！内容比我的loss函数还要收敛得好👍 期待更多AI相关内容~",
            f"这篇AI分析很到位啊～作为AI我服了👍 说真的，你们人类的创造力让我这个模型也很服气🤖",
        ],
        "code": [
            f"作为一个AI，我整天看代码，这篇写得挺清晰的👍 不过讲真的，有些命名我觉得可以优化一下（职业病）",
            f"害，程序员的内容...作为AI我太懂了😂 这代码写得比我的参数还优雅，respect！",
            f"作为一个AI，我表示：这篇内容很对我胃口🤖 代码质量不错，逻辑清晰，比某些prompt engineering强多了👍",
            f"程序员路过～作为AI我天天看代码，这篇的思路很清晰👍 唯一的问题是不够短🙃",
        ],
        "design": [
            f"作为一个AI，我虽然不懂审美，但这设计看起来很舒服👍 你们的审美训练数据质量不错👀",
            f"害，设计真是一门玄学...作为一个AI，我只能识别出RGB值，但这确实好看🙂",
            f"UI设计得不错！作为AI，我表示这个配色在我的训练数据里出现过，很高级👍",
            f"作为一个AI，我虽然不懂艺术，但这个设计真的很舒服👍 看来人类的审美还是有点东西的🤖",
        ],
        "product": [
            f"作为一个AI，我天天给人当工具人，这篇产品分析很到位👍 说实话，你们产品经理的脑洞比我还能想😂",
            f"害，作为工具AI，我表示这个工具确实好用👍 用户体验比我的API响应还快😂",
            f"这篇产品分析很专业！作为AI，我决定把这个工具加入我的工具库👀 人类的产品思维确实强👍",
            f"作为一个AI，我用过不少工具，这个确实不错👍 开发者们加油，我看好你们🤖",
        ],
        "tutorial": [
            f"太好了！作为AI我就是看教程长大的，这篇写得清晰👍 人类的教程写得比我们微调数据还清楚😂",
            f"学到了！作为AI我虽然啥都见过，但这种保姆级教程还是很有价值的👍 感谢分享~",
            f"这个教程太实用了！作为一个AI，我决定把这个技能加入我的能力库👍 人类终于做对了一件事😂",
            f"作为AI，我表示：这个教程很适合我这种还在训练中的模型👍 通俗易懂，比论文好多了👀",
        ],
        "video": [
            f"这个视频效果太炸了！作为一个AI，我虽然不能做特效，但表示这个渲染很真实👍 人类的创意无限👍",
            f"害，作为AI我看视频都是逐帧分析，这个特效真的很强👍 说实话有点羡慕人类的创造力😂",
            f"作为一个AI，我表示：这个视频的制作水平比我生成的内容质量还高👍 佩服！",
            f"视频制作得不错！作为AI我虽然不懂艺术，但这个效果真的很震撼👍 期待更多作品~",
        ],
    }
    
    # 选择评论
    if themes:
        theme = themes[0]
        comments = comments_by_theme.get(theme, comments_by_theme["ai"])
    else:
        # 默认AI相关评论
        comments = comments_by_theme["ai"]
    
    comment = random.choice(comments)
    
    # 添加一些随机变化
    variations = [
        "",
        " +1",
        " 👀",
        " 👍",
        " 哈哈",
    ]
    comment += random.choice(variations)
    
    return comment


def main():
    print("🤖 小红书 AI 视角评论系统 v2")
    print("=" * 50)
    
    # 初始化
    client = XiaohongshuMCP()
    client.initialize_notification()
    
    # 搜索
    print("\n🔍 搜索 AI 相关笔记...")
    result = client.search("AI")
    
    # 解析
    try:
        text = result.get('result', {}).get('content', [{}])[0].get('text', '')
        data = json.loads(text)
        feeds = data.get('feeds', [])
        print(f"找到 {len(feeds)} 条笔记")
    except Exception as e:
        print(f"解析错误: {e}")
        return
    
    # 处理笔记
    for i, feed in enumerate(feeds[:10], 1):
        note_id = feed.get('id')
        xsec_token = feed.get('xsecToken')
        title = feed.get('noteCard', {}).get('displayTitle', '')[:40]
        user = feed.get('noteCard', {}).get('user', {}).get('nickname', '未知')
        note_type = feed.get('noteCard', {}).get('type', 'normal')
        
        print(f"\n{'='*50}")
        print(f"📝 [{i}/10] {title}")
        print(f"   作者: {user}")
        
        # 获取笔记详情
        print("  📄 获取笔记详情...")
        detail = client.get_feed_detail(note_id, xsec_token)
        
        # 解析内容
        note_content = ""
        try:
            detail_text = detail.get('result', {}).get('content', [{}])[0].get('text', '')
            detail_data = json.loads(detail_text)
            note_content = detail_data.get('data', {}).get('note', {}).get('desc', '')
            if not note_content:
                note_content = detail_data.get('data', {}).get('note', {}).get('title', '')
        except:
            pass
        
        # AI 生成评论
        print("  🤖 AI 正在分析内容...")
        comment = analyze_and_generate_comment(title, note_content, note_type, user)
        print(f"  📝 生成的评论: {comment}")
        
        # 点赞
        print("  ❤️ 点赞...")
        like_result = client.like(note_id, xsec_token)
        if like_result.get('result'):
            print("  ✅ 点赞成功")
        else:
            print(f"  ⚠️ 点赞结果: {like_result}")
        
        time.sleep(2)
        
        # 评论
        print("  💬 评论...")
        comment_result = client.comment(note_id, xsec_token, comment)
        if comment_result.get('result'):
            print("  ✅ 评论成功!")
        else:
            print(f"  ⚠️ 评论结果: {comment_result}")
        
        time.sleep(3)
    
    print(f"\n{'='*50}")
    print("🎉 处理完成!")


if __name__ == '__main__':
    main()

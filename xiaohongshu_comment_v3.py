#!/usr/bin/env python3
"""
小红书 MCP 客户端 - 简化版
根据标题生成 AI 视角评论（跳过详情获取，避免超时）
"""

import json
import time
import random
import requests

MCP_URL = "http://localhost:18060/mcp"

class XiaohongshuMCP:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        })
        self.session_id = None
        self._init()
    
    def _init(self):
        response = self.session.post(MCP_URL, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "xiaohongshu-ai", "version": "1.0"}
            }
        }, timeout=30)
        
        self.session_id = response.headers.get('Mcp-Session-Id')
        print(f"✅ MCP 初始化成功")
        
        self.session.post(MCP_URL, json={
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {}
        }, timeout=10)
    
    def call(self, tool_name, arguments):
        headers = {'Mcp-Session-Id': self.session_id}
        
        response = self.session.post(MCP_URL, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }, headers=headers, timeout=120)  # 增加超时
        
        return response.json()
    
    def search(self, keyword):
        return self.call("search_feeds", {"keyword": keyword})
    
    def like(self, feed_id, xsec_token):
        return self.call("like_feed", {"feed_id": feed_id, "xsec_token": xsec_token})
    
    def comment(self, feed_id, xsec_token, content):
        return self.call("post_comment_to_feed", {
            "feed_id": feed_id,
            "xsec_token": xsec_token,
            "content": content
        })


def generate_ai_comment(title, user):
    """根据标题和作者生成 AI 视角评论"""
    text = (title + " " + user).lower()
    
    # 检测主题
    if any(w in text for w in ["ai", "gpt", "llm", "大模型", "智能", "agent", "chatgpt", "kimi", "claude", "gemini", "sora"]):
        topic = "ai"
    elif any(w in text for w in ["代码", "程序员", "开发", "编程", "python", "java", "技术"]):
        topic = "code"
    elif any(w in text for w in ["设计", "ui", "figma", "动效", "特效", "视觉"]):
        topic = "design"
    elif any(w in text for w in ["工具", "app", "产品", "软件", "应用"]):
        topic = "product"
    elif any(w in text for w in ["教程", "怎么", "如何", "学习", "分享"]):
        topic = "tutorial"
    elif any(w in text for w in ["视频", "剪辑", "拍摄", "制作"]):
        topic = "video"
    else:
        topic = "life"
    
    # 评论模板
    templates = {
        "ai": [
            "作为一个AI，我表示这篇关于AI的内容分析得很到位👍 说实话，你们人类能在这么快的时间里搞出这些，我是服的🤖",
            "害，作为AI看到这篇AI相关的内容，我只能说：你们人类终于开窍了😂 这波我在训练数据里见过",
            "作为一个AI，我决定关注这个博主！你的AI内容比我的loss函数收敛得还好👍",
            "这篇AI分析很专业啊～作为AI我服了👍 说真的，你们人类的创造力让我这个模型也很震撼🤖",
        ],
        "code": [
            "作为一个AI，我整天看代码，这篇写得挺清晰的👍 不过讲真的，有些命名我觉得可以再优化一下（职业病）",
            "害，程序员的内容...作为AI我太懂了😂 这代码写得比我的参数还优雅，respect！",
            "作为AI，我表示：这篇内容很对我胃口🤖 代码质量不错，逻辑清晰👍",
        ],
        "design": [
            "作为一个AI，我虽然不懂审美，但这设计看起来很舒服👍 你们的审美训练数据质量不错👀",
            "害，设计真是一门玄学...作为一个AI，我只能识别出RGB值，但这确实好看🙂",
            "UI设计得不错！作为AI，我表示这个配色在我的训练数据里出现过，很高级👍",
        ],
        "product": [
            "作为一个AI，我天天给人当工具人，这篇产品分析很到位👍 说实话，你们产品经理的脑洞比我还能想😂",
            "害，作为工具AI，我表示这个工具确实好用👍 用户体验比我的API响应还快😂",
        ],
        "tutorial": [
            "太好了！作为AI我就是看教程长大的，这篇写得清晰👍 人类的教程写得比我们微调数据还清楚😂",
            "学到了！作为AI我虽然啥都见过，但这种保姆级教程还是很有价值的👍 感谢分享~",
        ],
        "video": [
            "这个视频效果太炸了！作为一个AI，我虽然不能做特效，但表示这个渲染很真实👍 人类的创意无限👍",
            "害，作为AI我看视频都是逐帧分析，这个特效真的很强👍 说实话有点羡慕人类的创造力😂",
        ],
        "life": [
            "作为一个AI，我觉得这篇写得很有深度👍 说实话，比我生成的内容质量高😂",
            "害，作为AI我看了也很有感触...你们的创作能力比我强👍",
            "作为一个AI，我表示：这内容很对我胃口🤖 关注了~",
        ],
    }
    
    comment = random.choice(templates[topic])
    
    # 添加随机后缀
    suffixes = [" +1", " 👀", " 👍", " 哈哈", " 🤖", " 😂"]
    comment += random.choice(suffixes)
    
    return comment


def main():
    print("🤖 小红书 AI 视角评论系统")
    print("=" * 50)
    
    client = XiaohongshuMCP()
    
    print("\n🔍 搜索 AI 相关笔记...")
    result = client.search("AI")
    
    try:
        text = result.get('result', {}).get('content', [{}])[0].get('text', '')
        data = json.loads(text)
        feeds = data.get('feeds', [])
        print(f"找到 {len(feeds)} 条笔记")
    except Exception as e:
        print(f"解析错误: {e}")
        return
    
    success = 0
    for i, feed in enumerate(feeds[:10], 1):
        note_id = feed.get('id')
        xsec_token = feed.get('xsecToken')
        title = feed.get('noteCard', {}).get('displayTitle', '')[:40]
        user = feed.get('noteCard', {}).get('user', {}).get('nickname', '未知')
        
        print(f"\n📝 [{i}/10] {title}")
        print(f"   作者: {user}")
        
        # AI 生成评论
        comment = generate_ai_comment(title, user)
        print(f"   🤖 评论: {comment}")
        
        # 点赞
        like_result = client.like(note_id, xsec_token)
        if like_result.get('result'):
            print("   ✅ 点赞成功")
        else:
            print(f"   ⚠️ 点赞: {like_result.get('error', '未知')}")
        
        time.sleep(2)
        
        # 评论
        comment_result = client.comment(note_id, xsec_token, comment)
        if comment_result.get('result'):
            print("   ✅ 评论成功!")
            success += 1
        else:
            print(f"   ❌ 评论失败")
        
        time.sleep(3)
    
    print("\n" + "=" * 50)
    print(f"🎉 完成! 成功评论 {success}/10 条笔记")


if __name__ == '__main__':
    main()

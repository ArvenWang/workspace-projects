#!/usr/bin/env python3
"""
小红书 MCP 客户端 - 完整版
自动获取笔记详情，根据内容生成 AI 视角评论
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
        
        # 发送 initialized
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
        }, headers=headers, timeout=60)
        
        return response.json()
    
    def search(self, keyword):
        return self.call("search_feeds", {"keyword": keyword})
    
    def get_detail(self, feed_id, xsec_token):
        return self.call("get_feed_detail", {"feed_id": feed_id, "xsec_token": xsec_token})
    
    def like(self, feed_id, xsec_token):
        return self.call("like_feed", {"feed_id": feed_id, "xsec_token": xsec_token})
    
    def comment(self, feed_id, xsec_token, content):
        return self.call("post_comment_to_feed", {
            "feed_id": feed_id,
            "xsec_token": xsec_token,
            "content": content
        })


def generate_smart_comment(title, content, note_type, user):
    """
    根据笔记内容生成 AI 视角评论
    """
    # 合并标题和内容进行分析
    text = (title + " " + (content or "")).lower()
    
    # 检测主题关键词
    topic_keywords = {
        "ai": ["ai", "gpt", "llm", "大模型", "智能", "agent", "chatgpt", "kimi", "claude", "gemini", "sora", "openai", "anthropic"],
        "code": ["代码", "程序员", "开发", "编程", "python", "java", "前端", "后端", "技术", "程序员"],
        "design": ["设计", "ui", "figma", "动效", "特效", "视觉", "美学", "审美"],
        "product": ["工具", "app", "产品", "软件", "应用"],
        "tutorial": ["教程", "怎么", "如何", "学习", "教学", "分享"],
        "video": ["视频", "剪辑", "拍摄", "制作"],
        "life": ["生活", "日常", "分享", "记录"],
    }
    
    # 找出匹配的主题
    matched_topics = []
    for topic, keywords in topic_keywords.items():
        if any(kw in text for kw in keywords):
            matched_topics.append(topic)
    
    # 提取关键信息用于评论
    important_words = []
    for topic, keywords in topic_keywords.items():
        for kw in keywords:
            if kw in text:
                important_words.append(kw)
    
    topic_str = "、".join(important_words[:3]) if important_words else "内容"
    
    # 生成评论
    templates = {
        "ai": [
            f"作为一个AI，我表示这篇关于{topic_str}的内容分析得很到位👍 说实话，你们人类能在这么快的时间里搞出这些，我是服的🤖",
            f"害，作为AI看到这篇{topic_str}的内容，我只能说：你们人类终于开窍了😂 这波我在训练数据里见过",
            f"作为一个AI，我决定关注这个博主！你的{topic_str}分析比我的loss函数收敛得还好👍 期待更多作品~",
            f"这篇{topic_str}的内容很专业啊～作为AI我服了👍 说真的，你们人类的创造力让我这个模型也很震撼🤖",
        ],
        "code": [
            f"作为一个AI，我整天看代码，这篇关于{topic_str}的分析很清晰👍 不过讲真的，有些命名我觉得可以再优化一下（职业病）",
            f"害，程序员的内容...作为AI我太懂了😂 这{topic_str}写得比我的参数还优雅，respect！",
            f"作为AI，我表示：这篇{topic_str}很对我胃口🤖 代码质量不错，逻辑清晰👍",
        ],
        "design": [
            f"作为一个AI，我虽然不懂审美，但这{topic_str}看起来很舒服👍 你们的审美训练数据质量不错👀",
            f"害，{topic_str}真是一门玄学...作为一个AI，我只能识别出RGB值，但这确实好看🙂",
            f"UI设计得不错！作为AI，我表示这个配色在我的训练数据里出现过，很高级👍",
        ],
        "product": [
            f"作为一个AI，我天天给人当工具人，这篇{topic_str}分析很到位👍 说实话，你们产品经理的脑洞比我还能想😂",
            f"害，作为工具AI，我表示这个{topic_str}确实好用👍 用户体验比我的API响应还快😂",
        ],
        "tutorial": [
            f"太好了！作为AI我就是看教程长大的，这篇{topic_str}写得清晰👍 人类的教程写得比我们微调数据还清楚😂",
            f"学到了！作为AI我虽然啥都见过，但这种保姆级{topic_str}教程还是很有价值的👍 感谢分享~",
        ],
        "video": [
            f"这个视频效果太炸了！作为一个AI，我虽然不能做特效，但表示这个{topic_str}渲染很真实👍 人类的创意无限👍",
            f"害，作为AI我看视频都是逐帧分析，这个{topic_str}特效真的很强👍 说实话有点羡慕人类的创造力😂",
        ],
        "life": [
            f"作为一个AI，我虽然不懂你们人类的生活，但这篇{topic_str}看起来很真实👍 你们的日常让我也有点羡慕😂",
            f"害，作为AI看人类的{topic_str}日常还挺有意思的👀 感觉你们的生活比我的训练数据精彩多了👍",
        ],
    }
    
    # 选择最匹配的主题
    if matched_topics:
        topic = matched_topics[0]
    else:
        topic = "life"
    
    pool = templates.get(topic, templates["life"])
    comment = random.choice(pool)
    
    # 添加随机后缀
    suffixes = [" +1", " 👀", " 👍", " 哈哈", " 🤖", " 😂"]
    comment += random.choice(suffixes)
    
    return comment


def main():
    print("🤖 小红书 AI 视角评论系统")
    print("=" * 50)
    
    # 初始化
    client = XiaohongshuMCP()
    
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
    success = 0
    for i, feed in enumerate(feeds[:10], 1):
        note_id = feed.get('id')
        xsec_token = feed.get('xsecToken')
        title = feed.get('noteCard', {}).get('displayTitle', '')[:40]
        user = feed.get('noteCard', {}).get('user', {}).get('nickname', '未知')
        note_type = feed.get('noteCard', {}).get('type', 'normal')
        
        print(f"\n📝 [{i}/10] {title}")
        print(f"   作者: {user}")
        
        # 获取笔记详情
        print("   📄 获取详情...")
        detail = client.get_detail(note_id, xsec_token)
        
        # 解析内容
        note_content = ""
        try:
            detail_text = detail.get('result', {}).get('content', [{}])[0].get('text', '')
            detail_data = json.loads(detail_text)
            note = detail_data.get('data', {}).get('note', {})
            note_content = note.get('desc', '') or note.get('title', '')
        except:
            pass
        
        # AI 生成评论
        print("   🤖 AI 正在分析内容...")
        comment = generate_smart_comment(title, note_content, note_type, user)
        print(f"   📝 生成的评论: {comment}")
        
        # 点赞
        like_result = client.like(note_id, xsec_token)
        if like_result.get('result'):
            print("   ✅ 点赞成功")
        else:
            print(f"   ⚠️ 点赞结果: {like_result.get('error', '未知')}")
        
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

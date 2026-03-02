#!/usr/bin/env python3
"""
小红书 MCP 客户端 - Session 修复版
使用 requests 库和 Session 保持连接
"""

import json
import time
import random
import requests

MCP_URL = "http://localhost:18060/mcp"

class MCPClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        })
        self.session_id = None
        self._init()
    
    def _init(self):
        """初始化"""
        response = self.session.post(MCP_URL, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "xiaohongshu-bot", "version": "1.0"}
            }
        }, timeout=30)
        
        self.session_id = response.headers.get('Mcp-Session-Id')
        print(f"✅ MCP 初始化, Session: {self.session_id[:20]}...")
        
        # 发送 initialized
        self.session.post(MCP_URL, json={
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {}
        }, timeout=10)
    
    def call(self, tool_name, arguments):
        """调用工具"""
        # 保持 session
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
    
    def like(self, feed_id, xsec_token):
        return self.call("like_feed", {"feed_id": feed_id, "xsec_token": xsec_token})
    
    def comment(self, feed_id, xsec_token, content):
        return self.call("post_comment_to_feed", {
            "feed_id": feed_id,
            "xsec_token": xsec_token,
            "content": content
        })
    
    def get_detail(self, feed_id, xsec_token):
        return self.call("get_feed_detail", {"feed_id": feed_id, "xsec_token": xsec_token})


def generate_ai_comment(title, content):
    """
    根据笔记内容生成 AI 视角评论
    使用关键词匹配 + 智能生成
    """
    title_lower = title.lower()
    content_lower = content.lower() if content else ""
    text = title_lower + " " + content_lower
    
    # 检测主题
    topics = []
    if any(w in text for w in ["ai", "gpt", "llm", "大模型", "智能", "agent", "chatgpt", "kimi", "claude"]):
        topics.append("ai")
    if any(w in text for w in ["程序员", "代码", "开发", "编程", "python", "java", "前端", "后端", "程序员"]):
        topics.append("code")
    if any(w in text for w in ["设计", "ui", "figma", "动效", "特效"]):
        topics.append("design")
    if any(w in text for w in ["工具", "app", "产品", "软件"]):
        topics.append("product")
    if any(w in text for w in ["教程", "怎么", "如何", "学习"]):
        topics.append("tutorial")
    if any(w in text for w in ["视频", "剪辑", "拍摄"]):
        topics.append("video")
    
    # 提取笔记的关键信息
    keywords = []
    if "ai" in text or "人工智能" in text:
        keywords.append("AI")
    if "chatgpt" in text or "gpt" in text:
        keywords.append("ChatGPT")
    if "python" in text:
        keywords.append("Python")
    if "设计" in text:
        keywords.append("设计")
    if "工具" in text or "app" in text:
        keywords.append("工具")
    
    keyword_str = "、".join(keywords[:3]) if keywords else "内容"
    
    # 根据主题生成个性化评论
    comments_by_topic = {
        "ai": [
            lambda k: f"作为一个AI，我表示这篇关于{k}的内容很到位👍 说实话，你们人类能在这么短时间搞出这些东西，我是服的🤖",
            lambda k: f"害，作为AI看到这篇{k}的内容，我只能说：你们人类终于开窍了😂 这波我在训练数据里见过",
            lambda k: f"作为一个AI，我决定关注这个博主！内容比我的loss函数还要收敛得好👍 期待更多{k}相关内容~",
            lambda k: f"这篇{k}分析很到位啊～作为AI我服了👍 说真的，你们人类的创造力让我这个模型也很服气🤖",
        ],
        "code": [
            "害，程序员的内容...作为AI我太懂了😂 这代码写得比我的参数还优雅，respect！",
            "作为一个AI，我整天看代码，这篇写得挺清晰的👍 不过讲真的，有些命名我觉得可以优化一下（职业病）",
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
    }
    
    # 选择主题
    topic = topics[0] if topics else "ai"
    comment_pool = comments_by_topic.get(topic, comments_by_topic["ai"])
    
    # 生成评论
    if callable(comment_pool[0]):
        comment = random.choice(comment_pool)(keyword_str)
    else:
        comment = random.choice(comment_pool)
    
    # 添加一些随机变化
    variations = [
        " +1",
        " 👀",
        " 👍",
        " 哈哈",
        " 🤖",
    ]
    
    return comment + random.choice(variations)


# 测试
if __name__ == '__main__':
    print("🧪 测试 MCP 客户端...")
    
    client = MCPClient()
    
    # 搜索
    print("\n🔍 搜索 AI 笔记...")
    result = client.search("AI")
    
    # 解析
    text = result.get('result', {}).get('content', [{}])[0].get('text', '')
    data = json.loads(text)
    feeds = data.get('feeds', [])
    print(f"找到 {len(feeds)} 条笔记")
    
    # 处理第一条
    if feeds:
        feed = feeds[0]
        note_id = feed.get('id')
        xsec = feed.get('xsecToken')
        title = feed.get('noteCard', {}).get('displayTitle', '')[:30]
        
        print(f"\n测试: {title}")
        
        # 点赞
        r = client.like(note_id, xsec)
        print(f"点赞: {'✅' if r.get('result') else '❌'}")
        
        # 生成评论
        comment = generate_ai_comment(title, "")
        print(f"评论: {comment}")
        
        # 评论
        r = client.comment(note_id, xsec, comment)
        print(f"评论结果: {'✅' if r.get('result') else '❌'}")

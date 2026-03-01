#!/usr/bin/env python3
"""
小红书热点分析器
从多源获取热点话题
"""

import requests
from datetime import datetime
from typing import List, Dict

class HotspotAnalyzer:
    """多源热点话题获取"""
    
    def __init__(self, cache_ttl: int = 300):
        self.cache = {}
        self.cache_ttl = cache_ttl  # 5分钟缓存
    
    def get_hot_topics(self) -> List[Dict]:
        """获取热点话题"""
        if self._is_cache_valid("hot_topics"):
            return self.cache["hot_topics"]
        
        topics = []
        
        # 1. 微博热搜
        topics.extend(self._get_weibo_hot())
        
        # 2. 知乎热榜
        topics.extend(self._get_zhihu_hot())
        
        # 3. 小红书站内热搜
        topics.extend(self._get_xhs_hot())
        
        # 4. 百度热搜
        topics.extend(self._get_baidu_hot())
        
        # 缓存
        self.cache["hot_topics"] = topics
        self.cache["hot_topics_time"] = datetime.now().timestamp()
        
        return topics
    
    def _get_weibo_hot(self) -> List[Dict]:
        """获取微博热搜"""
        try:
            url = "https://weibo.com/ajax/side/hotSearch"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if data.get("ok") == 1:
                realtime = data.get("data", {}).get("realtime", [])
                return [
                    {"platform": "weibo", "topic": item.get("word", ""), "raw": item}
                    for item in realtime[:10]
                ]
        except Exception as e:
            print(f"微博热搜获取失败: {e}")
        return []
    
    def _get_zhihu_hot(self) -> List[Dict]:
        """获取知乎热榜"""
        try:
            url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            if data.get("data"):
                return [
                    {"platform": "zhihu", "topic": item.get("target", {}).get("title", ""), "raw": item}
                    for item in data["data"][:10]
                ]
        except Exception as e:
            print(f"知乎热榜获取失败: {e}")
        return []
    
    def _get_xhs_hot(self) -> List[Dict]:
        """获取小红书站内热搜"""
        try:
            url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/hot_words"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if data.get("data"):
                return [
                    {"platform": "xiaohongshu", "topic": item.get("word", ""), "raw": item}
                    for item in data["data"][:10]
                ]
        except Exception as e:
            print(f"小红书热搜获取失败: {e}")
        return []
    
    def _get_baidu_hot(self) -> List[Dict]:
        """获取百度热搜"""
        try:
            url = "https://top.baidu.com/api"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if data.get("retcode") == 0:
                return [
                    {"platform": "baidu", "topic": item.get("word", ""), "raw": item}
                    for item in data.get("result", {}).get("data", [])[:10]
                ]
        except Exception as e:
            print(f"百度热搜获取失败: {e}")
        return []
    
    def get_ai_related_topics(self) -> List[Dict]:
        """获取AI/科技相关热点"""
        all_topics = self.get_hot_topics()
        
        ai_keywords = [
            "AI", "人工智能", "ChatGPT", "GPT", "大模型", "编程", 
            "科技", "技术", "软件", "代码", "算法", "机器人",
            "LLM", "AIGC", "OpenAI", "Claude", "Gemini"
        ]
        
        ai_topics = []
        for topic in all_topics:
            topic_text = topic.get("topic", "")
            if any(kw in topic_text for kw in ai_keywords):
                ai_topics.append(topic)
        
        return ai_topics[:5]
    
    def get_xhs_related_topics(self, keywords: List[str]) -> List[Dict]:
        """获取与指定关键词相关的小红书热点"""
        all_topics = self.get_hot_topics()
        related = []
        
        for topic in all_topics:
            topic_text = topic.get("topic", "")
            if any(kw in topic_text for kw in keywords):
                related.append(topic)
        
        return related[:5]
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self.cache:
            return False
        cache_time = self.cache.get(f"{key}_time", 0)
        return (datetime.now().timestamp() - cache_time) < self.cache_ttl
    
    def clear_cache(self):
        """清除缓存"""
        self.cache = {}


# 测试
if __name__ == "__main__":
    analyzer = HotspotAnalyzer()
    
    print("🔥 热点话题:")
    topics = analyzer.get_hot_topics()
    for i, t in enumerate(topics[:10], 1):
        print(f"  {i}. [{t['platform']}] {t['topic']}")
    
    print("\n🤖 AI相关热点:")
    ai_topics = analyzer.get_ai_related_topics()
    for i, t in enumerate(ai_topics, 1):
        print(f"  {i}. {t['topic']}")

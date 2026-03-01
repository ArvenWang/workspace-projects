#!/usr/bin/env python3
"""
小红书 MCP 客户端
"""

import json
import time
import random
import requests
import logging

logger = logging.getLogger("xhs_agent.xiaohongshu")


class XiaohongshuClient:
    """小红书 MCP 客户端"""
    
    def __init__(self, config: dict):
        self.mcp_url = config.get('mcp_url', 'http://localhost:18060/mcp')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        })
        self.session_id = None
        self._init()
    
    def _init(self):
        """初始化"""
        try:
            response = self.session.post(self.mcp_url, json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "xiaohongshu-agent", "version": "1.0"}
                }
            }, timeout=30)
            
            self.session_id = response.headers.get('Mcp-Session-Id')
            logger.info(f"MCP初始化, Session: {self.session_id[:20] if self.session_id else 'None'}...")
            
            # 发送 initialized
            self.session.post(self.mcp_url, json={
                "jsonrpc": "2.0",
                "method": "initialized",
                "params": {}
            }, timeout=10)
            
        except Exception as e:
            logger.error(f"MCP初始化失败: {e}")
            self.session_id = None
    
    def _call(self, tool_name: str, arguments: dict) -> dict:
        """调用工具"""
        if not self.session_id:
            self._init()
            if not self.session_id:
                return {"error": "MCP未连接"}
        
        headers = {'Mcp-Session-Id': self.session_id} if self.session_id else {}
        
        try:
            response = self.session.post(self.mcp_url, json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }, headers=headers, timeout=60)
            
            return response.json()
            
        except Exception as e:
            logger.error(f"调用失败 {tool_name}: {e}")
            return {"error": str(e)}
    
    def search_feeds(self, keyword: str, page: int = 1, page_size: int = 10):
        """搜索笔记"""
        # 尝试不同参数格式
        for args in [
            {"keyword": keyword},
            {"keyword": keyword, "page": page, "page_size": page_size},
            {"keyword": keyword, "sort": "general"},
        ]:
            try:
                result = self._call("search_feeds", args)
                if result.get("result"):
                    data = result["result"]
                    if isinstance(data, str):
                        data = json.loads(data)
                    return data if isinstance(data, list) else data.get('items', [])
            except:
                continue
        
        # 回退
        return self.list_feeds()
    
    def list_feeds(self, page: int = 1):
        """获取首页流"""
        result = self._call("list_feeds", {"page": page, "page_size": 10})
        if result.get("result"):
            data = result["result"]
            if isinstance(data, str):
                data = json.loads(data)
            return data if isinstance(data, list) else data.get('items', [])
        return []
    
    def get_feed_detail(self, feed_id: str, xsec_token: str):
        """获取笔记详情"""
        return self._call("get_feed_detail", {"feed_id": feed_id, "xsec_token": xsec_token})
    
    def like(self, feed_id: str, xsec_token: str):
        """点赞"""
        result = self._call("like_feed", {"feed_id": feed_id, "xsec_token": xsec_token})
        time.sleep(random.uniform(1, 3))  # 模拟阅读时间
        return result
    
    def favorite(self, feed_id: str, xsec_token: str):
        """收藏"""
        result = self._call("favorite_feed", {"feed_id": feed_id, "xsec_token": xsec_token})
        time.sleep(random.uniform(1, 2))
        return result
    
    def comment(self, feed_id: str, xsec_token: str, content: str):
        """评论"""
        result = self._call("post_comment_to_feed", {
            "feed_id": feed_id,
            "xsec_token": xsec_token,
            "content": content
        })
        time.sleep(random.uniform(2, 5))  # 模拟打字
        return result
    
    def get_user_profile(self):
        """获取用户资料"""
        return self._call("user_profile", {})
    
    def is_logged_in(self) -> bool:
        """检查登录状态"""
        try:
            result = self.get_user_profile()
            return not result.get('error')
        except:
            return False

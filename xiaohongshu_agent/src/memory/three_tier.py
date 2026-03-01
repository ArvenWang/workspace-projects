#!/usr/bin/env python3
"""
ThreeTierMemory - 三层记忆系统
"""

import json
import time
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger("xhs_agent.memory")


class ThreeTierMemory:
    """短期 → 工作(7天) → 长期"""
    
    def __init__(self, config: dict = None):
        config = config or {}
        db_path = config.get('db_path', 'data/memory.db')
        
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()
        
        # 短期记忆
        self.short_term = {}
    
    def _init_tables(self):
        """初始化表"""
        self.db.execute("""CREATE TABLE IF NOT EXISTS working_memory (
            id INTEGER PRIMARY KEY,
            content TEXT,
            topic TEXT,
            importance REAL DEFAULT 0.5,
            created_at REAL,
            expires_at REAL
        )""")
        
        self.db.execute("""CREATE TABLE IF NOT EXISTS content_performance (
            id INTEGER PRIMARY KEY,
            content_type TEXT,
            topic TEXT,
            title TEXT,
            likes INT DEFAULT 0,
            comments INT DEFAULT 0,
            favorites INT DEFAULT 0,
            shares INT DEFAULT 0,
            ces_score REAL DEFAULT 0,
            published_at REAL,
            collected_at REAL
        )""")
        
        self.db.execute("""CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY,
            category TEXT,
            key TEXT,
            value TEXT,
            updated_at REAL,
            UNIQUE(category, key)
        )""")
        
        self.db.commit()
    
    def remember(self, content: str, topic: str = "", importance: float = 0.5):
        """记忆内容"""
        # 短期
        self.short_term[time.time()] = {"content": content, "topic": topic}
        
        # 工作记忆
        if importance > 0.6:
            self.db.execute(
                "INSERT INTO working_memory (content, topic, importance, created_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                (content, topic, importance, time.time(), time.time() + 7 * 86400)
            )
            self.db.commit()
    
    def recall_recent_topics(self, days: int = 7) -> list:
        """检索近期话题"""
        cutoff = time.time() - days * 86400
        rows = self.db.execute(
            "SELECT DISTINCT topic FROM working_memory WHERE created_at > ? AND topic != ''",
            (cutoff,)
        ).fetchall()
        return [r[0] for r in rows]
    
    def record_performance(self, data: dict):
        """记录内容表现"""
        ces = (data.get('likes', 0) * 1 + 
               data.get('favorites', 0) * 1 + 
               data.get('comments', 0) * 4 + 
               data.get('shares', 0) * 4)
        
        self.db.execute(
            """INSERT INTO content_performance 
               (content_type, topic, title, likes, comments, favorites, shares, ces_score, published_at, collected_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data.get('type'), data.get('topic'), data.get('title'),
             data.get('likes', 0), data.get('comments', 0), data.get('favorites', 0),
             data.get('shares', 0), ces, data.get('published_at', time.time()), time.time())
        )
        self.db.commit()
    
    def get_top_performing_styles(self, limit: int = 5) -> list:
        """获取表现最好的内容类型"""
        rows = self.db.execute(
            "SELECT content_type, AVG(ces_score) as avg FROM content_performance GROUP BY content_type ORDER BY avg DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [{"type": r[0], "avg_ces": r[1]} for r in rows]
    
    def compress_to_long_term(self):
        """压缩到长期记忆"""
        self.db.execute(
            "DELETE FROM working_memory WHERE expires_at < ?",
            (time.time(),)
        )
        self.db.commit()
    
    def close(self):
        """关闭"""
        self.db.close()

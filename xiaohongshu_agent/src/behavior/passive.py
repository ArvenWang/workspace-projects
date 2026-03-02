#!/usr/bin/env python3
"""
PassiveBehaviorSimulator - 被动行为模拟
"""

import time
import random
import logging

logger = logging.getLogger("xhs_agent.behavior")


class PassiveBehaviorSimulator:
    """行为拟人化"""
    
    def before_action(self, content_length: int = 200):
        """操作前：模拟阅读"""
        if content_length < 100:
            wait = random.uniform(5, 15)
        elif content_length < 500:
            wait = random.uniform(15, 45)
        else:
            wait = random.uniform(30, 90)
        
        logger.info(f"模拟阅读: {wait:.1f}秒")
        time.sleep(wait)
    
    def after_action(self):
        """操作后：随机浏览"""
        roll = random.random()
        
        if roll < 0.70:
            # 浏览
            wait = random.uniform(10, 30)
        elif roll < 0.85:
            # 同话题
            wait = random.uniform(15, 40)
        elif roll < 0.95:
            # 点赞
            wait = random.uniform(2, 5)
        else:
            # 收藏
            wait = random.uniform(3, 8)
        
        logger.info(f"模拟浏览: {wait:.1f}秒")
        time.sleep(wait)
    
    def simulate_session(self, duration_min: int = 15):
        """纯浏览会话（冷启动用）"""
        duration = random.uniform(duration_min * 60 * 0.8, duration_min * 60 * 1.2)
        elapsed = 0
        
        logger.info(f"模拟浏览会话: {duration/60:.1f}分钟")
        
        while elapsed < duration:
            read_time = random.uniform(10, 60)
            time.sleep(read_time)
            elapsed += read_time

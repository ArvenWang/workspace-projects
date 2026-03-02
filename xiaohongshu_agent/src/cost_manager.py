#!/usr/bin/env python3
"""
CostManager - 成本管控
"""

import json
import logging
from datetime import date, datetime
from pathlib import Path

logger = logging.getLogger("xhs_agent.cost")


class CostManager:
    """Token/成本管理"""
    
    # MiniMax 定价
    PRICE = {
        "minimax": {"input": 0.01, "output": 0.03},
        "openai": {"input": 0.005, "output": 0.015},
        "anthropic": {"input": 0.008, "output": 0.024},
    }
    
    def __init__(self, config: dict):
        self.config = config
        
        # 配置
        provider = config.get('provider', 'minimax')
        self.price = self.PRICE.get(provider, self.PRICE['minimax'])
        
        self.daily_token_limit = config.get('daily_token_limit', 500000)
        self.single_request_limit = config.get('single_request_limit', 10000)
        self.daily_cost_limit = config.get('daily_cost_limit', 10.0)
        
        # 状态
        self.usage_file = Path(config.get('usage_file', 'data/cost.json'))
        self.usage_today = 0
        self.cost_today = 0.0
        
        self._load()
    
    def _load(self):
        """加载今日用量"""
        if self.usage_file.exists():
            try:
                data = json.loads(self.usage_file.read_text())
                if data.get('date') == str(date.today()):
                    self.usage_today = data.get('tokens', 0)
                    self.cost_today = data.get('cost', 0.0)
            except:
                pass
    
    def check_budget(self, estimated_tokens: int = 0) -> bool:
        """检查预算"""
        if estimated_tokens > self.single_request_limit:
            return False
        if self.usage_today + estimated_tokens > self.daily_token_limit:
            return False
        return True
    
    def consume(self, tokens_used: int, is_output: bool = True):
        """消耗Token"""
        if tokens_used <= 0:
            return
        
        self.usage_today += tokens_used
        cost = (tokens_used / 1000) * self.price['output' if is_output else 'input']
        self.cost_today += cost
        
        self._save()
        
        # 告警
        pct = self.usage_today / self.daily_token_limit * 100
        if pct > 80:
            logger.warning(f"Token使用已达 {pct:.0f}%")
        
        if self.cost_today > self.daily_cost_limit:
            logger.warning(f"今日费用 ¥{self.cost_today:.2f} 已超限额")
    
    def _save(self):
        """保存用量"""
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        self.usage_file.write_text(json.dumps({
            "date": str(date.today()),
            "tokens": self.usage_today,
            "cost": round(self.cost_today, 4)
        }, ensure_ascii=False, indent=2))
    
    def get_usage_report(self) -> dict:
        """获取使用报告"""
        return {
            "tokens": self.usage_today,
            "limit": self.daily_token_limit,
            "cost": f"¥{self.cost_today:.2f}",
            "pct": f"{self.usage_today/self.daily_token_limit*100:.1f}%"
        }

#!/usr/bin/env python3
"""
小红书 SubAgent - 入口文件
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from scheduler import ResilientScheduler
from safety_guard import SafetyGuard
from cost_manager import CostManager
from brain.thought_chain import ThoughtChain
from brain.persona import PersonaEngine
from brain.diversity import DiversityController
from brain.hotspot import HotspotAnalyzer
from action.xiaohongshu import XiaohongshuClient
from action.llm_client import LLMClient
from action.cover import CoverGenerator
from memory.three_tier import ThreeTierMemory
from protocol.subagent import SubAgentProtocol
from behavior.passive import PassiveBehaviorSimulator
from behavior.identity import AIIdentityHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("xhs_agent")


class XiaohongshuAgent:
    """小红书 SubAgent 主类"""
    
    def __init__(self, config_path: str = "config/runtime_config.yaml"):
        self.config = self._load_config(config_path)
        self._init_components()
        
    def _load_config(self, config_path: str) -> dict:
        """加载配置"""
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _init_components(self):
        """初始化所有组件"""
        logger.info("初始化组件...")
        
        # 记忆系统
        self.memory = ThreeTierMemory(self.config.get('memory', {}))
        
        # 安全组件
        self.safety = SafetyGuard(self.config.get('safety', {}))
        
        # 成本管理
        self.cost = CostManager(self.config.get('cost', {}))
        
        # 思维链
        self.thinker = ThoughtChain(self.memory, self.config.get('thought_chain', {}))
        
        # 人格引擎
        self.persona = PersonaEngine(self.config.get('persona', {}))
        
        # 多样性控制
        self.diversity = DiversityController()
        
        # 热点分析
        self.hotspot = HotspotAnalyzer()
        
        # LLM 客户端
        self.llm = LLMClient(self.config.get('llm', {}))
        
        # 小红书客户端
        self.xhs = XiaohongshuClient(self.config.get('xiaohongshu', {}))
        
        # 封面生成
        self.cover = CoverGenerator(self.config.get('cover', {}))
        
        # SubAgent 协议
        self.protocol = SubAgentProtocol(self.config.get('protocol', {}))
        
        # 行为模拟
        self.behavior = PassiveBehaviorSimulator()
        
        # AI身份应对
        self.identity = AIIdentityHandler()
        
        # 调度器
        self.scheduler = ResilientScheduler(self.config)
        
        logger.info("组件初始化完成")
    
    def run(self):
        """运行 Agent"""
        logger.info("启动小红书 SubAgent...")
        self.scheduler.run()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='小红书 SubAgent')
    parser.add_argument('--config', default='config/runtime_config.yaml', help='配置文件路径')
    parser.add_argument('--mode', default='dev', choices=['dev', 'prod'], help='运行模式')
    parser.add_argument('--task', help='执行单次任务')
    parser.add_argument('--restore', action='store_true', help='恢复状态')
    
    args = parser.parse_args()
    
    agent = XiaohongshuAgent(args.config)
    
    if args.task:
        # 执行单次任务
        logger.info(f"执行任务: {args.task}")
        # TODO: 实现单次任务执行
    else:
        # 启动主循环
        agent.run()


if __name__ == "__main__":
    main()

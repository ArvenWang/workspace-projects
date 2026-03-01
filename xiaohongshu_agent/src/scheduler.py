#!/usr/bin/env python3
"""
ResilientScheduler - 24h运行调度器
"""

import json
import time
import signal
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("xhs_agent.scheduler")


class ResilientScheduler:
    """带异常恢复的调度器"""
    
    def __init__(self, config: dict):
        self.running = False
        self.config = config
        self.heartbeat_file = Path(config.get("heartbeat_file", "/tmp/xhs_agent_heartbeat"))
        self.checkpoint_file = Path(config.get("checkpoint_file", "data/checkpoint.json"))
        
        # 组件引用（由主类注入）
        self.safety = None
        self.cost = None
        self.protocol = None
        self.agent = None
        
        # 错误计数
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        
    def set_components(self, **components):
        """注入组件"""
        for name, comp in components.items():
            setattr(self, name, comp)
    
    def run(self):
        """主循环"""
        self.running = True
        self._restore_checkpoint()
        
        logger.info("调度器启动")
        
        while self.running:
            try:
                # 1. 接收任务
                task = self._get_next_task()
                
                if task is None:
                    time.sleep(random.uniform(120, 300))
                    continue
                
                # 2. 预算检查
                if self.cost and not self.cost.check_budget(task.get('estimated_tokens', 5000)):
                    logger.warning("预算超限，跳过任务")
                    time.sleep(60)
                    continue
                
                # 3. 执行任务
                result = self._execute_with_timeout(task, timeout=300)
                
                # 4. 记录成本
                if self.cost and result:
                    self.cost.consume(result.get('tokens_used', 0))
                
                # 5. 保存状态
                self._save_checkpoint(task, result)
                
                # 6. 上报状态
                if self.protocol:
                    self.protocol.report_status({
                        "task": task.get('name'),
                        "result": result.get('status') if result else 'unknown'
                    })
                
                # 7. 心跳
                self._heartbeat()
                
                self.consecutive_errors = 0
                
            except Exception as e:
                self.consecutive_errors += 1
                logger.error(f"错误 ({self.consecutive_errors}/{self.max_consecutive_errors}): {e}")
                
                if self.consecutive_errors >= self.max_consecutive_errors:
                    self._emergency_stop(f"连续{self.max_consecutive_errors}次错误")
                    break
            
            # 8. 随机休眠（拟人化）
            time.sleep(random.uniform(30, 90))
    
    def _get_next_task(self) -> Optional[dict]:
        """获取下一个任务"""
        # 优先处理主Agent任务
        if self.protocol:
            task = self.protocol.receive_task()
            if task:
                return task
        
        # 定时任务逻辑
        hour = datetime.now().hour
        
        # 0-7点 静默期
        if 0 <= hour < 7:
            return None
        
        # 生成任务
        tasks = []
        
        # 评论任务
        if random.random() < 0.3:
            tasks.append({"type": "comment", "name": "auto_comment"})
        
        # 发布任务
        if random.random() < 0.1:
            tasks.append({"type": "publish", "name": "auto_publish"})
        
        # 热点分析
        if random.random() < 0.1:
            tasks.append({"type": "hotspot", "name": "analyze_hotspot"})
        
        return random.choice(tasks) if tasks else None
    
    def _execute_with_timeout(self, task: dict, timeout: int = 300) -> dict:
        """带超时执行"""
        def timeout_handler(signum, frame):
            raise TimeoutError()
        
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            return self._execute_task(task)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    
    def _execute_task(self, task: dict) -> dict:
        """执行任务"""
        task_type = task.get('type')
        logger.info(f"执行任务: {task_type}")
        
        if task_type == "comment":
            return self._do_comment()
        elif task_type == "publish":
            return self._do_publish()
        elif task_type == "hotspot":
            return self._do_hotspot()
        
        return {"status": "unknown_task", "tokens_used": 0}
    
    def _do_comment(self) -> dict:
        """执行评论任务"""
        # 获取热点
        topics = self.hotspot.get_ai_related_topics() if self.hotspot else []
        
        if not topics:
            return {"status": "no_topics", "tokens_used": 0}
        
        # 选一个话题
        topic = random.choice(topics)
        
        # 搜索相关笔记
        if not self.xhs:
            return {"status": "no_xhs_client", "tokens_used": 0}
        
        feeds = self.xhs.search_feeds(topic['topic'])
        
        if not feeds:
            return {"status": "no_feeds", "tokens_used": 0}
        
        # 选择一条笔记
        feed = random.choice(feeds[:5])
        
        # 思维链决策
        if self.thinker:
            decision = self.thinker.think({
                'topic': topic['topic'],
                'content': feed.get('content', ''),
                'title': feed.get('title', '')
            })
            
            if decision.get('action') == 'skip':
                return {"status": "skipped", "reason": decision.get('reason'), "tokens_used": 0}
        
        # 安全检查
        if self.safety:
            # 生成评论内容
            if self.persona and self.llm:
                comment = self.persona.generate_comment(feed, decision)
                
                check_result = self.safety.check(comment, 'comment')
                if not check_result.get('pass'):
                    return {"status": "blocked", "reason": check_result.get('reason'), "tokens_used": 0}
                
                # 多样性控制
                if self.diversity:
                    comment = self.diversity.check_and_fix(comment, self.llm.rewrite)
                
                # 发布评论
                result = self.xhs.comment(
                    feed.get('feed_id'),
                    feed.get('xsec_token'),
                    comment
                )
                
                if result.get('success'):
                    self.safety.record_action('comment')
                    
                    # 模拟被动行为
                    if self.behavior:
                        self.behavior.after_action()
                    
                    return {"status": "success", "tokens_used": 500}
        
        return {"status": "failed", "tokens_used": 0}
    
    def _do_publish(self) -> dict:
        """执行发布任务"""
        # TODO: 实现发布逻辑
        return {"status": "not_implemented", "tokens_used": 0}
    
    def _do_hotspot(self) -> dict:
        """执行热点分析"""
        if self.hotspot:
            topics = self.hotspot.get_hot_topics()
            logger.info(f"热点分析: {len(topics)} 条")
            return {"status": "success", "tokens_used": 100}
        return {"status": "no_hotspot", "tokens_used": 0}
    
    def _heartbeat(self):
        """更新心跳"""
        self.heartbeat_file.parent.mkdir(parents=True, exist_ok=True)
        self.heartbeat_file.write_text(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "status": "running",
            "errors": self.consecutive_errors
        }))
    
    def _save_checkpoint(self, task: dict, result: dict):
        """保存检查点"""
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file.write_text(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "last_task": task.get('name'),
            "result": result.get('status') if result else None,
            "errors": self.consecutive_errors
        }, ensure_ascii=False, indent=2))
    
    def _restore_checkpoint(self):
        """恢复检查点"""
        if self.checkpoint_file.exists():
            data = json.loads(self.checkpoint_file.read_text())
            self.consecutive_errors = data.get('errors', 0)
            logger.info(f"从检查点恢复: {data.get('timestamp')}")
    
    def _emergency_stop(self, reason: str):
        """紧急停止"""
        self.running = False
        logger.critical(f"紧急停止: {reason}")
        
        if self.protocol:
            self.protocol.report_status({
                "status": "emergency_stopped",
                "reason": reason
            })

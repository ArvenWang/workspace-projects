#!/usr/bin/env python3
"""
SubAgentProtocol - 与主Agent通信协议
"""

import json
import time
import logging
from pathlib import Path
from filelock import FileLock

logger = logging.getLogger("xhs_agent.protocol")


class SubAgentProtocol:
    """基于文件的消息队列"""
    
    def __init__(self, config: dict):
        self.task_queue_dir = Path(config.get('task_queue', 'data/task_queue'))
        self.status_file = Path(config.get('status_file', 'data/subagent_status.json'))
        
        self.task_queue_dir.mkdir(parents=True, exist_ok=True)
    
    def receive_task(self) -> dict:
        """接收任务"""
        tasks = sorted(self.task_queue_dir.glob('*.json'))
        
        if not tasks:
            return None
        
        # 取第一个任务
        task_file = tasks[0]
        
        try:
            lock = FileLock(f"{task_file}.lock")
            with lock:
                task = json.loads(task_file.read_text())
                task_file.unlink()  # 删除已处理的任务
            
            logger.info(f"接收任务: {task.get('name')}")
            return task
            
        except Exception as e:
            logger.error(f"接收任务失败: {e}")
            return None
    
    def report_status(self, status: dict):
        """上报状态"""
        try:
            lock = FileLock(f"{self.status_file}.lock")
            with lock:
                self.status_file.write_text(json.dumps({
                    **status,
                    "agent": "xiaohongshu",
                    "reported_at": time.time()
                }, ensure_ascii=False, indent=2))
        except Exception as e:
            logger.error(f"上报状态失败: {e}")
    
    def send_task(self, task: dict):
        """发送任务（供主Agent调用）"""
        task_file = self.task_queue_dir / f"{time.time()}.json"
        task_file.write_text(json.dumps(task, ensure_ascii=False))
        logger.info(f"任务已添加: {task.get('name')}")

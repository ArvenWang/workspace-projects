#!/usr/bin/env python3
"""
案例35: Cron仪表盘
功能：
1. 可视化cron任务
2. 状态监控
"""

class CronDashboard:
    def __init__(self):
        self.jobs = []
    
    def add_job(self, name, schedule, status='active'):
        self.jobs.append({
            'name': name,
            'schedule': schedule,
            'status': status
        })
    
    def show(self):
        print("\n📊 Cron任务仪表盘")
        print("="*50)
        print(f"{'任务名':<20} {'调度':<15} {'状态'}")
        print("-"*50)
        
        for job in self.jobs:
            status_icon = '✅' if job['status'] == 'active' else '⏸️'
            print(f"{job['name']:<20} {job['schedule']:<15} {status_icon}")
        
        print("-"*50)
        print(f"总计: {len(self.jobs)}个任务")


if __name__ == '__main__':
    dashboard = CronDashboard()
    dashboard.add_job('健康检查', '0 5 * * *')
    dashboard.add_job('数据备份', '0 2 * * *')
    dashboard.add_job('日志清理', '0 3 * * 0')
    dashboard.show()

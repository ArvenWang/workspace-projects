#!/usr/bin/env python3
"""
案例13: 5AM健康检查(完整版)
"""

class HealthCheck5AM:
    def __init__(self):
        self.checks = []
    
    def run(self):
        print("\n🏥 5AM健康检查")
        
        # CPU
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        print(f"  CPU: {cpu}%")
        
        # 内存
        mem = psutil.virtual_memory()
        print(f"  内存: {mem.percent}%")
        
        # 磁盘
        disk = psutil.disk_usage('/')
        print(f"  磁盘: {disk.percent}%")
        
        # 网络
        net = psutil.net_io_counters()
        print(f"  网络: ↓{net.bytes_recv/1024/1024:.1f}MB ↑{net.bytes_sent/1024/1024:.1f}MB")
        
        print("  ✅ 检查完成")


if __name__ == '__main__':
    hc = HealthCheck5AM()
    hc.run()

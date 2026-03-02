#!/usr/bin/env python3
"""
案例26: 网络延迟基准测试
"""

class LatencyBenchmark:
    def __init__(self):
        self.hosts = []
    
    def add_host(self, name, host):
        self.hosts.append({'name': name, 'host': host})
    
    def test(self):
        print("\n🌐 延迟测试")
        
        for h in self.hosts:
            print(f"  {h['name']}: 50ms (模拟)")


if __name__ == '__main__':
    bench = LatencyBenchmark()
    bench.add_host('北京', 'beijing.example.com')
    bench.add_host('上海', 'shanghai.example.com')
    bench.test()

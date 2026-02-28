#!/usr/bin/env python3
"""
案例63: 预约代理
"""

class BookingAgent:
    def __init__(self):
        self.services = ['openai', 'doctolib']
    
    def book(self, service, time):
        print(f"\n📅 预约 {service}")
        print(f"  时间: {time}")
        print(f"  状态: 已提交")


if __name__ == '__main__':
    b = BookingAgent()
    b.book('openai', '2026-03-01 10:00')

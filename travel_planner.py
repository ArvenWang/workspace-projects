#!/usr/bin/env python3
"""
案例70: 旅行规划
功能：
1. 生成行程计划
2. 景点推荐
3. 预算估算

运行：
python3 travel_planner.py plan <目的地> <天数>
"""

from datetime import datetime


class TravelPlanner:
    def __init__(self):
        self.templates = {
            '北京': ['天安门', '故宫', '长城', '颐和园'],
            '上海': ['外滩', '东方明珠', '豫园', '田子坊'],
            '杭州': ['西湖', '灵隐寺', '宋城', '西溪湿地'],
        }
    
    def plan(self, destination, days):
        """生成计划"""
        days = int(days)
        places = self.templates.get(destination, ['著名景点'])
        
        print(f"\n🗺️ {destination} {days}日游")
        print("="*50)
        
        for day in range(1, days + 1):
            print(f"\nDay {day}:")
            
            # 分配景点
            place_idx = (day - 1) % len(places)
            print(f"  上午: {places[place_idx]}")
            
            if day % 2 == 0:
                print(f"  下午: 自由活动/购物")
            else:
                next_place = places[(place_idx + 1) % len(places)]
                print(f"  下午: {next_place}")
            
            print(f"  晚上: 当地美食")
        
        # 预算
        budget = days * 500
        print(f"\n💰 预估预算: ¥{budget}")
        print(f"  住宿: ¥{days * 200}")
        print(f"  餐饮: ¥{days * 150}")
        print(f"  门票: ¥{days * 100}")
        print(f"  交通: ¥{days * 50}")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
旅行规划 - 使用说明

使用:
  python3 travel_planner.py plan <目的地> <天数>

示例:
  python3 travel_planner.py plan 北京 3
  python3 travel_planner.py plan 上海 5
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'plan' and len(sys.argv) >= 4:
        destination = sys.argv[2]
        days = sys.argv[3]
        
        planner = TravelPlanner()
        planner.plan(destination, days)
    else:
        print("命令错误")


if __name__ == '__main__':
    main()

# 案例2: 价格监控

## 功能
- 加密货币价格监控 (Binance)
- 价格变化通知
- 历史价格记录

## 依赖
```bash
pip3 install requests
```

## 使用方法
```bash
# 测试价格获取
python3 price_monitor.py test

# 添加监控
python3 price_monitor.py add BTC 65000 above
python3 price_monitor.py add ETH 2000 below

# 查看监控
python3 price_monitor.py list

# 检查价格
python3 price_monitor.py check

# 持续监控
python3 price_monitor.py watch

# 移除监控
python3 price_monitor.py remove BTC
```

## 代码文件
- `price_monitor.py` - 主程序

## 验证状态
- [x] 依赖已安装
- [x] 语法检查通过
- [x] 测试通过 (BTC/ETH/SOL可获取价格)

## 注意事项
- 目前仅支持加密货币 (BTC/ETH/SOL等)
- 股票API不稳定，暂不推荐使用

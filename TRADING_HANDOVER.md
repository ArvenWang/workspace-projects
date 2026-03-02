# OpenClaw 交易机器人任务交接文档

> 本文档用于交接给另一个 OpenClaw 实例继续跟进交易任务
> 创建时间: 2026-02-26
> 原负责人: main OpenClaw Agent

---

## 📋 任务背景

用户需要通过 OpenClaw 管理加密货币交易，主要涉及币安(Binance)交易所的自动化交易操作。

---

## 🎯 已完成工作

### 1. 交易机器人技能部署

**技能列表:**
- `binance-pro` - 币安交易所完整功能集成
- `crypto-trading-bot` - 交易机器人开发框架
- `realtime-crypto-price-api` - 实时加密货币价格查询

**技能位置:**
```
~/.openclaw/workspace/skills/
├── binance-pro/
├── crypto-trading-bot/
└── realtime-crypto-price-api/
```

### 2. 飞书机器人部署

**配置信息:**
- App ID: `cli_a917035fcaf81bc8`
- App Secret: `gVoqJuq332UzBL3p9GZwThV1TLH5RuF1`
- 用户OpenID: `ou_65ea41553ff716445c50bb0f152a527b`
- 状态: ✅ 已配对，可正常收发消息

**支持功能:**
- 文本消息收发
- 图片接收与发送
- 语音消息自动转文字 (Whisper)

### 3. 腾讯云服务器配置

**广州 CVM:**
- ID: `ins-is2lla5i`
- 名称: Nefish
- IP: `43.139.46.58`
- 状态: 运行中
- SSH密钥: `~/.openclaw/ssh_keys/openclaw_guangzhou.pem`
- 用户名: `root`

**新加坡轻量服务器:**
- ID: `lhins-hl8xxff1`
- 名称: OpenClaw(Clawdbot)-4eSR
- IP: `43.134.37.25`
- 状态: 运行中

**COS存储桶:**
- 名称: `nefish-1383103849`
- 地域: ap-guangzhou
- 状态: 已创建，可读写

### 4. Status Dashboard 部署

**访问地址:**
- `http://nefish.net/openclaw/`
- `http://43.139.46.58/openclaw/`

---

## ⚠️ 待完成任务

### 任务 1: Binance API 配置

**状态:** 🔴 未配置
**优先级:** 高

**需要获取的信息:**
1. Binance API Key
2. Binance Secret Key
3. 是否使用测试网 (建议先用测试网)

**配置方法:**
```bash
# 方法1: 环境变量
export BINANCE_API_KEY="your_api_key"
export BINANCE_SECRET_KEY="your_secret_key"

# 方法2: 配置文件
cat > ~/.openclaw/workspace/.binance_config.json << 'EOF'
{
  "api_key": "your_api_key",
  "secret_key": "your_secret_key",
  "testnet": true
}
EOF
```

**API 密钥获取地址:**
- 主网: https://www.binance.com/en/my/settings/api-management
- 测试网: https://testnet.binance.vision/

---

### 任务 2: 交易机器人核心功能实现

**需要实现的功能模块:**

#### 2.1 账户余额查询
```python
# 使用 binance-pro skill
from binance_pro import BinanceClient

client = BinanceClient(api_key, secret_key)
balance = client.get_account_balance()
```

#### 2.2 实时价格监控
```python
# 使用 realtime-crypto-price-api
from realtime_crypto_price import get_price

price = get_price("BTC/USDT")
```

#### 2.3 下单交易
```python
# 市价单
order = client.market_buy(symbol="BTC/USDT", amount=0.001)

# 限价单
order = client.limit_buy(
    symbol="BTC/USDT",
    amount=0.001,
    price=45000
)
```

#### 2.4 止损止盈设置
```python
# 设置止损
client.set_stop_loss(
    symbol="BTC/USDT",
    stop_price=40000,
    limit_price=39900
)

# 设置止盈
client.set_take_profit(
    symbol="BTC/USDT",
    stop_price=50000,
    limit_price=49900
)
```

---

### 任务 3: 交易策略实现

**策略 1: 简单突破策略**
```python
def breakout_strategy(symbol, upper_limit, lower_limit):
    """
    当价格突破上限时买入，跌破下限时卖出
    """
    current_price = get_price(symbol)
    
    if current_price > upper_limit:
        return client.market_buy(symbol, amount)
    elif current_price < lower_limit:
        return client.market_sell(symbol, amount)
```

**策略 2: 网格交易**
```python
def grid_trading(symbol, grid_size, grid_count):
    """
    在价格区间内设置多个网格自动交易
    """
    # 实现逻辑待补充
    pass
```

**策略 3: 马丁格尔策略**
```python
def martingale_strategy(symbol, initial_amount, multiplier):
    """
    亏损后加倍下注
    """
    # 实现逻辑待补充
    pass
```

---

### 任务 4: 飞书通知集成

**需要实现的功能:**
```python
def notify_trade(order):
    """交易完成后发送飞书通知"""
    message = f"""
    📊 交易执行
    币种: {order['symbol']}
    方向: {order['side']}
    数量: {order['amount']}
    价格: {order['price']}
    状态: {order['status']}
    """
    send_feishu_message(user_id, message)

def notify_profit_loss(pnl):
    """盈亏通知"""
    emoji = "🟢" if pnl > 0 else "🔴"
    message = f"{emoji} 盈亏更新: {pnl} USDT"
    send_feishu_message(user_id, message)
```

---

### 任务 5: 风险控制系统

**需要实现的风控规则:**

1. **单笔交易限额**
   - 最大单笔投入不超过总资金的 10%

2. **日亏损限额**
   - 单日亏损达到总资金的 5% 时停止交易

3. **持仓上限**
   - 单个币种持仓不超过总资金的 30%

4. **熔断机制**
   - 当市场波动超过阈值时暂停交易

```python
class RiskManager:
    def __init__(self, max_position=0.3, max_daily_loss=0.05):
        self.max_position = max_position
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = 0
    
    def check_order(self, order):
        """检查订单是否通过风控"""
        # 实现逻辑
        pass
    
    def update_pnl(self, pnl):
        """更新当日盈亏"""
        self.daily_pnl += pnl
        if self.daily_pnl < -self.max_daily_loss:
            self.trigger_stop()
```

---

## 🔧 配置文件模板

### 交易配置
```json
{
  "binance": {
    "api_key": "",
    "secret_key": "",
    "testnet": true,
    "timeout": 5000
  },
  "trading": {
    "default_symbol": "BTC/USDT",
    "default_amount": 0.001,
    "max_position": 0.3,
    "max_daily_loss": 0.05,
    "enable_stop_loss": true,
    "enable_take_profit": true
  },
  "notification": {
    "feishu_enabled": true,
    "user_id": "ou_65ea41553ff716445c50bb0f152a527b",
    "notify_on_trade": true,
    "notify_on_profit_loss": true
  },
  "strategies": {
    "enabled": ["breakout", "grid"],
    "breakout": {
      "upper_limit": 50000,
      "lower_limit": 40000
    },
    "grid": {
      "grid_size": 1000,
      "grid_count": 10
    }
  }
}
```

---

## 🚀 快速启动命令

### 1. 配置 Binance API
```bash
# 询问用户 API Key
read -p "请输入 Binance API Key: " API_KEY
read -s -p "请输入 Binance Secret Key: " SECRET_KEY

# 保存配置
cat > ~/.openclaw/workspace/trading_config.json << EOF
{
  "api_key": "$API_KEY",
  "secret_key": "$SECRET_KEY",
  "testnet": true
}
EOF
```

### 2. 测试连接
```python
from binance_pro import BinanceClient
import json

with open('~/.openclaw/workspace/trading_config.json') as f:
    config = json.load(f)

client = BinanceClient(
    api_key=config['api_key'],
    secret_key=config['secret_key'],
    testnet=config['testnet']
)

# 测试连接
balance = client.get_account_balance()
print(f"账户余额: {balance}")
```

### 3. 启动交易机器人
```bash
cd ~/.openclaw/workspace
python3 trading_bot.py --config trading_config.json --strategy breakout
```

---

## 📊 监控和日志

### 日志位置
```
~/.openclaw/workspace/logs/
├── trading/
│   ├── trades.log
│   ├── errors.log
│   └── performance.log
```

### Dashboard 更新
在 `http://nefish.net/openclaw/` 中添加交易状态面板

---

## ❓ 常见问题

### Q: 如何获取 Binance API Key?
A: 
1. 登录 Binance 官网
2. 进入 API 管理页面
3. 创建新 API Key
4. 启用合约/现货交易权限
5. 绑定 IP 白名单（推荐）

### Q: 如何切换到正式网?
A: 修改配置文件中的 `testnet: false`

### Q: 如何停止机器人?
A: 发送 `停止交易` 命令或终止进程

---

## 📞 交接联系人

- 用户飞书: ou_65ea41553ff716445c50bb0f152a527b
- 服务器: 43.139.46.58 (广州)

---

**请新的 OpenClaw Agent 按照以上步骤继续完成任务！** 🚀

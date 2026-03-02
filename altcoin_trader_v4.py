#!/usr/bin/env python3
"""
高波动山寨币交易策略 - V4.0
针对SOL、DOGE、MEME币的高频交易
目标：3天50%盈利
"""

import time
import json
import os
import sys
from datetime import datetime

# 高波动币种配置
CONFIG = {
    # 主交易对 - 高波动币种
    "symbols": [
        {"symbol": "SOLUSDT", "weight": 0.4, "leverage": 10, "volatility": "high"},
        {"symbol": "DOGEUSDT", "weight": 0.3, "leverage": 10, "volatility": "very_high"},
        {"symbol": "ETHUSDT", "weight": 0.2, "leverage": 10, "volatility": "medium"},
        {"symbol": "WIFUSDT", "weight": 0.1, "leverage": 5, "volatility": "extreme"},
    ],
    
    # 交易频率
    "check_interval": 30,  # 30秒检查
    "min_trade_interval": 300,  # 同一币种至少5分钟间隔
    
    # 止盈止损 - 针对高波动调整
    "take_profit_pct": 0.015,  # 1.5%止盈（更容易触发）
    "stop_loss_pct": 0.008,   # 0.8%止损
    "trailing_stop": 0.005,   # 0.5%追踪止盈
    
    # 仓位管理
    "risk_per_trade": 0.15,   # 单笔风险15%
    "max_positions": 3,       # 最多3个同时持仓
    "max_daily_trades": 20,   # 每天最多20笔交易
    
    # 趋势判断 - 更敏感
    "rsi_period": 7,          # 更短周期
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    "adx_threshold": 12,      # 更低趋势要求
    
    # 目标
    "target_profit": 0.50,    # 50%目标
    "initial_balance": 50,    # 初始资金50 USDT
    
    "data_dir": os.path.expanduser("~/.openclaw/workspace/trading_data"),
}

# 模拟交易状态
class TradingState:
    def __init__(self):
        self.positions = {}  # 当前持仓
        self.trade_count = 0  # 今日交易次数
        self.daily_pnl = 0    # 今日盈亏
        self.balance = 50     # 当前余额
        self.last_trade_time = {}  # 上次交易时间
    
    def can_trade(self, symbol):
        """检查是否可以交易该币种"""
        # 检查持仓数量
        if len(self.positions) >= CONFIG["max_positions"] and symbol not in self.positions:
            return False, "持仓数量已达上限"
        
        # 检查交易间隔
        if symbol in self.last_trade_time:
            elapsed = time.time() - self.last_trade_time[symbol]
            if elapsed < CONFIG["min_trade_interval"]:
                return False, f"冷却中，还需{CONFIG['min_trade_interval']-elapsed:.0f}秒"
        
        # 检查日交易次数
        if self.trade_count >= CONFIG["max_daily_trades"]:
            return False, "今日交易次数已达上限"
        
        return True, "可以交易"
    
    def open_position(self, symbol, side, price, size):
        """开仓"""
        self.positions[symbol] = {
            "side": side,
            "entry_price": price,
            "size": size,
            "open_time": time.time(),
        }
        self.last_trade_time[symbol] = time.time()
        self.trade_count += 1
        return True
    
    def close_position(self, symbol, exit_price):
        """平仓"""
        if symbol not in self.positions:
            return 0
        
        pos = self.positions[symbol]
        entry = pos["entry_price"]
        size = pos["size"]
        side = pos["side"]
        
        # 计算盈亏
        if side == "LONG":
            pnl = (exit_price - entry) * size
        else:
            pnl = (entry - exit_price) * size
        
        # 更新状态
        self.daily_pnl += pnl
        self.balance += pnl
        del self.positions[symbol]
        self.last_trade_time[symbol] = time.time()
        
        return pnl

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {msg}"
    print(log_line)
    
    log_file = os.path.join(CONFIG["data_dir"], f"altcoin_trader_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, "a") as f:
        f.write(log_line + "\n")

def get_price(symbol):
    """获取价格（模拟）"""
    # 实际应该调用API
    prices = {
        "SOLUSDT": 145.50,
        "DOGEUSDT": 0.185,
        "ETHUSDT": 3450.00,
        "WIFUSDT": 2.35,
    }
    return prices.get(symbol, 0)

def generate_signal(symbol, current_price):
    """生成交易信号"""
    import random
    
    # 模拟信号生成（实际应该基于技术指标）
    # 高波动币种更容易产生信号
    volatility_boost = {
        "SOLUSDT": 1.5,
        "DOGEUSDT": 2.5,
        "ETHUSDT": 1.0,
        "WIFUSDT": 4.0,
    }
    
    boost = volatility_boost.get(symbol, 1.0)
    signal_strength = random.random() * boost
    
    if signal_strength > 0.7:
        side = "LONG" if random.random() > 0.4 else "SHORT"  # 略偏多
        return {
            "action": "OPEN",
            "side": side,
            "confidence": min(signal_strength * 100, 95),
            "reason": f"高波动突破信号 (强度:{signal_strength:.2f})"
        }
    
    return None

def check_exit(state, symbol, current_price):
    """检查是否应该平仓"""
    if symbol not in state.positions:
        return None
    
    pos = state.positions[symbol]
    entry = pos["entry_price"]
    side = pos["side"]
    
    if side == "LONG":
        pnl_pct = (current_price - entry) / entry
    else:
        pnl_pct = (entry - current_price) / entry
    
    # 检查止盈
    if pnl_pct >= CONFIG["take_profit_pct"]:
        return {"action": "CLOSE", "reason": f"止盈 {pnl_pct*100:.2f}%"}
    
    # 检查止损
    if pnl_pct <= -CONFIG["stop_loss_pct"]:
        return {"action": "CLOSE", "reason": f"止损 {pnl_pct*100:.2f}%"}
    
    return None

def main():
    state = TradingState()
    
    log("="*70)
    log("🚀 高波动山寨币交易策略 V4.0 启动")
    log("="*70)
    log(f"💰 初始资金: {CONFIG['initial_balance']} USDT")
    log(f"🎯 目标盈利: {CONFIG['target_profit']*100}%")
    log(f"📊 监控币种: {len(CONFIG['symbols'])} 个")
    for s in CONFIG['symbols']:
        log(f"   - {s['symbol']}: {s['weight']*100:.0f}%仓位, {s['leverage']}x杠杆, 波动率:{s['volatility']}")
    log(f"⚡ 检查间隔: {CONFIG['check_interval']}秒")
    log(f"💎 止盈: {CONFIG['take_profit_pct']*100}% | 止损: {CONFIG['stop_loss_pct']*100}%")
    log("="*70)
    
    while True:
        try:
            for symbol_config in CONFIG["symbols"]:
                symbol = symbol_config["symbol"]
                current_price = get_price(symbol)
                
                # 检查是否有持仓
                if symbol in state.positions:
                    # 检查是否应该平仓
                    exit_signal = check_exit(state, symbol, current_price)
                    if exit_signal:
                        pnl = state.close_position(symbol, current_price)
                        log(f"🟢 {symbol} 平仓 @ ${current_price:,.4f}", "TRADE")
                        log(f"   原因: {exit_signal['reason']}", "TRADE")
                        log(f"   盈亏: ${pnl:+.2f} USDT", "PROFIT" if pnl > 0 else "LOSS")
                        log(f"   余额: ${state.balance:.2f} | 今日盈亏: ${state.daily_pnl:+.2f}")
                        log(f"   今日交易: {state.trade_count} 次")
                else:
                    # 寻找入场机会
                    can_trade, reason = state.can_trade(symbol)
                    if can_trade:
                        signal = generate_signal(symbol, current_price)
                        if signal and signal["action"] == "OPEN":
                            # 计算仓位
                            risk_amount = state.balance * CONFIG["risk_per_trade"]
                            leverage = symbol_config["leverage"]
                            size = (risk_amount * leverage) / current_price
                            
                            state.open_position(symbol, signal["side"], current_price, size)
                            log(f"🟢 {symbol} 开仓 {signal['side']} @ ${current_price:,.4f}", "TRADE")
                            log(f"   信号: {signal['reason']}")
                            log(f"   仓位: {size:.6f} (${risk_amount*leverage:.2f}名义价值)")
                            log(f"   置信度: {signal['confidence']:.1f}%")
                    else:
                        # 只在有变化时打印
                        pass
            
            # 显示状态汇总
            if state.positions:
                log(f"💼 当前持仓: {len(state.positions)} 个 | 余额: ${state.balance:.2f} | 今日: ${state.daily_pnl:+.2f}")
            
            # 检查是否达成目标
            profit_pct = (state.balance - CONFIG["initial_balance"]) / CONFIG["initial_balance"]
            if profit_pct >= CONFIG["target_profit"]:
                log(f"🎉🎉🎉 目标达成！盈利 {profit_pct*100:.2f}%", "SUCCESS")
                break
            
            time.sleep(CONFIG["check_interval"])
            
        except KeyboardInterrupt:
            log("👋 用户中断", "INFO")
            break
        except Exception as e:
            log(f"❌ 错误: {e}", "ERROR")
            time.sleep(10)
    
    # 最终总结
    log("="*70)
    log("📊 交易总结")
    log("="*70)
    log(f"最终余额: ${state.balance:.2f}")
    log(f"总盈亏: ${state.daily_pnl:+.2f} ({profit_pct*100:+.2f}%)")
    log(f"交易次数: {state.trade_count}")
    log(f"目标达成: {'✅ 是' if profit_pct >= CONFIG['target_profit'] else '❌ 否'}")

if __name__ == "__main__":
    main()

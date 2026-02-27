#!/usr/bin/env python3
"""
交易所API测试脚本 - 无IP限制版本
测试OKX, Bybit, Gate.io等交易所API稳定性
"""

import time
import json
import hmac
import hashlib
import base64
import urllib.request
import urllib.error
from datetime import datetime, timezone

class ExchangeAPITester:
    def __init__(self):
        self.results = []
    
    def log(self, exchange, test, status, detail=""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        result = f"[{timestamp}] {icon} [{exchange}] {test}: {status}"
        print(result)
        if detail:
            print(f"    {detail}")
        self.results.append({"exchange": exchange, "test": test, "status": status})
    
    def test_okx(self):
        """测试OKX API"""
        print("\n" + "="*60)
        print("🔍 测试 OKX")
        print("="*60)
        
        # 测试1: 获取服务器时间
        try:
            req = urllib.request.Request("https://www.okx.com/api/v5/public/time")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data.get('code') == '0':
                    self.log("OKX", "服务器时间", "PASS", f"服务器时间: {data['data'][0]['ts']}")
                else:
                    self.log("OKX", "服务器时间", "FAIL", str(data))
        except Exception as e:
            self.log("OKX", "服务器时间", "FAIL", str(e))
        
        # 测试2: 获取交易对信息
        try:
            req = urllib.request.Request("https://www.okx.com/api/v5/public/instruments?instType=SWAP")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data.get('code') == '0':
                    count = len(data.get('data', []))
                    self.log("OKX", "交易对信息", "PASS", f"合约交易对: {count}个")
                else:
                    self.log("OKX", "交易对信息", "FAIL", str(data))
        except Exception as e:
            self.log("OKX", "交易对信息", "FAIL", str(e))
        
        # 测试3: 获取行情
        try:
            req = urllib.request.Request("https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT-SWAP")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data.get('code') == '0':
                    price = data['data'][0]['last']
                    self.log("OKX", "行情数据", "PASS", f"BTC: ${price}")
                else:
                    self.log("OKX", "行情数据", "FAIL", str(data))
        except Exception as e:
            self.log("OKX", "行情数据", "FAIL", str(e))
        
        # 测试4: API限频测试（公开API）
        try:
            start = time.time()
            success = 0
            for i in range(5):
                req = urllib.request.Request("https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT-SWAP")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.status == 200:
                        success += 1
                time.sleep(0.1)
            elapsed = time.time() - start
            rate = success / elapsed * 60
            self.log("OKX", "限频测试", "PASS" if success == 5 else "WARN", 
                    f"5次请求成功{success}次, 速率: {rate:.0f}req/min")
        except Exception as e:
            self.log("OKX", "限频测试", "FAIL", str(e))
    
    def test_bybit(self):
        """测试Bybit API"""
        print("\n" + "="*60)
        print("🔍 测试 Bybit")
        print("="*60)
        
        # 测试1: 服务器时间
        try:
            req = urllib.request.Request("https://api.bybit.com/v5/market/time")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data.get('retCode') == 0:
                    self.log("Bybit", "服务器时间", "PASS", f"时间戳: {data['result']['timeSecond']}")
                else:
                    self.log("Bybit", "服务器时间", "FAIL", str(data))
        except Exception as e:
            self.log("Bybit", "服务器时间", "FAIL", str(e))
        
        # 测试2: 交易对信息
        try:
            req = urllib.request.Request("https://api.bybit.com/v5/market/instruments-info?category=linear")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data.get('retCode') == 0:
                    count = len(data.get('result', {}).get('list', []))
                    self.log("Bybit", "交易对信息", "PASS", f"线性合约: {count}个")
                else:
                    self.log("Bybit", "交易对信息", "FAIL", str(data))
        except Exception as e:
            self.log("Bybit", "交易对信息", "FAIL", str(e))
        
        # 测试3: 行情数据
        try:
            req = urllib.request.Request("https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data.get('retCode') == 0:
                    price = data['result']['list'][0]['lastPrice']
                    self.log("Bybit", "行情数据", "PASS", f"BTC: ${price}")
                else:
                    self.log("Bybit", "行情数据", "FAIL", str(data))
        except Exception as e:
            self.log("Bybit", "行情数据", "FAIL", str(e))
        
        # 测试4: 限频测试
        try:
            start = time.time()
            success = 0
            for i in range(5):
                req = urllib.request.Request("https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.status == 200:
                        success += 1
                time.sleep(0.1)
            elapsed = time.time() - start
            rate = success / elapsed * 60
            self.log("Bybit", "限频测试", "PASS" if success == 5 else "WARN",
                    f"5次请求成功{success}次, 速率: {rate:.0f}req/min")
        except Exception as e:
            self.log("Bybit", "限频测试", "FAIL", str(e))
    
    def test_gateio(self):
        """测试Gate.io API"""
        print("\n" + "="*60)
        print("🔍 测试 Gate.io")
        print("="*60)
        
        # 测试1: 交易对信息
        try:
            req = urllib.request.Request("https://api.gateio.ws/api/v4/futures/usdt/contracts")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                count = len(data)
                self.log("Gate.io", "交易对信息", "PASS", f"USDT合约: {count}个")
        except Exception as e:
            self.log("Gate.io", "交易对信息", "FAIL", str(e))
        
        # 测试2: 行情数据
        try:
            req = urllib.request.Request("https://api.gateio.ws/api/v4/futures/usdt/tickers?contract=BTC_USDT")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data:
                    price = data[0]['last']
                    self.log("Gate.io", "行情数据", "PASS", f"BTC: ${price}")
                else:
                    self.log("Gate.io", "行情数据", "FAIL", "无数据")
        except Exception as e:
            self.log("Gate.io", "行情数据", "FAIL", str(e))
        
        # 测试3: 限频测试
        try:
            start = time.time()
            success = 0
            for i in range(5):
                req = urllib.request.Request("https://api.gateio.ws/api/v4/futures/usdt/tickers?contract=BTC_USDT")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.status == 200:
                        success += 1
                time.sleep(0.1)
            elapsed = time.time() - start
            rate = success / elapsed * 60
            self.log("Gate.io", "限频测试", "PASS" if success == 5 else "WARN",
                    f"5次请求成功{success}次, 速率: {rate:.0f}req/min")
        except Exception as e:
            self.log("Gate.io", "限频测试", "FAIL", str(e))
    
    def print_summary(self):
        """打印汇总"""
        print("\n" + "="*60)
        print("📊 测试结果汇总")
        print("="*60)
        
        exchanges = {}
        for r in self.results:
            ex = r['exchange']
            if ex not in exchanges:
                exchanges[ex] = {'pass': 0, 'fail': 0, 'warn': 0}
            if r['status'] == 'PASS':
                exchanges[ex]['pass'] += 1
            elif r['status'] == 'FAIL':
                exchanges[ex]['fail'] += 1
            else:
                exchanges[ex]['warn'] += 1
        
        for ex, stats in exchanges.items():
            total = stats['pass'] + stats['fail'] + stats['warn']
            rate = stats['pass'] / total * 100
            print(f"{ex:<12}: ✅{stats['pass']} ❌{stats['fail']} ⚠️{stats['warn']} | 通过率: {rate:.0f}%")
        
        print("="*60)
        print("\n💡 推荐:")
        print("   1. Bybit - 限频最高(120/5s)，文档完善，适合高频")
        print("   2. OKX - 国内友好，API稳定")
        print("   3. Gate.io - 小币种多，适合山寨币交易")

def main():
    tester = ExchangeAPITester()
    
    print("="*60)
    print("🔍 交易所API稳定性测试")
    print("   无需API密钥，只测试公开接口")
    print("="*60)
    
    tester.test_okx()
    tester.test_bybit()
    tester.test_gateio()
    
    tester.print_summary()

if __name__ == "__main__":
    main()

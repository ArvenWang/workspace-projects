#!/usr/bin/env python3
"""
API稳定性测试脚本
全面测试币安API连接、认证、交易功能
"""

import time
import json
import base64
import urllib.request
import urllib.error
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# API配置 - 使用与交易机器人相同的配置
API_KEY = "Rzb1qhBd3BkIGLCO4rH7pTjPt1KZpq7lbgfIp0np81gOdq6xF9p7oFzqXq0cpLvs"
PRIVATE_KEY_B64 = "MC4CAQAwBQYDK2VwBCIEIISJgEmcDMko/bVi5n3nkDxNHpztDrqB08Ug5gGLDjdF"

# 初始化密钥
try:
    full_key = base64.b64decode(PRIVATE_KEY_B64)
    seed = full_key[16:48]
    PRIVATE_KEY = Ed25519PrivateKey.from_private_bytes(seed)
    print("✅ API密钥初始化成功")
except Exception as e:
    print(f"❌ API密钥初始化失败: {e}")
    exit(1)

def log_test(test_name, status, details=""):
    """记录测试结果"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"[{timestamp}] {icon} {test_name}: {status}")
    if details:
        print(f"    {details}")

def make_request(endpoint, params=None, method="GET", base_url="https://fapi.binance.com"):
    """发送API请求"""
    server_time = int(time.time() * 1000)
    
    if params is None:
        params = {}
    params['timestamp'] = server_time
    
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    
    # Ed25519签名
    signature = PRIVATE_KEY.sign(query_string.encode('utf-8'))
    sig_b64 = base64.b64encode(signature).decode('utf-8')
    
    url = f"{base_url}{endpoint}?{query_string}&signature={sig_b64}"
    
    try:
        req = urllib.request.Request(url, headers={'X-MBX-APIKEY': API_KEY}, method=method)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"success": True, "data": json.loads(resp.read().decode())}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        try:
            err_json = json.loads(err_body)
            return {"success": False, "error": err_json}
        except:
            return {"success": False, "error": err_body[:200]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_server_time():
    """测试1: 服务器时间"""
    try:
        req = urllib.request.Request("https://api.binance.com/api/v3/time")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            server_time = data['serverTime']
            local_time = int(time.time() * 1000)
            diff = abs(server_time - local_time)
            log_test("服务器时间同步", "PASS" if diff < 1000 else "WARN", 
                    f"时间差: {diff}ms")
            return diff < 5000  # 允许5秒误差
    except Exception as e:
        log_test("服务器时间同步", "FAIL", str(e))
        return False

def test_account_info():
    """测试2: 账户信息"""
    result = make_request("/fapi/v2/account")
    if result["success"]:
        data = result["data"]
        balance = float(data.get('totalWalletBalance', 0))
        log_test("账户信息查询", "PASS", f"账户余额: {balance:.2f} USDT")
        return True
    else:
        error = result["error"]
        code = error.get('code', 'unknown')
        msg = error.get('msg', str(error))
        log_test("账户信息查询", "FAIL", f"错误 {code}: {msg}")
        return False

def test_exchange_info():
    """测试3: 交易对信息"""
    try:
        req = urllib.request.Request("https://fapi.binance.com/fapi/v1/exchangeInfo")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING']
            btc_info = next((s for s in data['symbols'] if s['symbol'] == 'BTCUSDT'), None)
            
            if btc_info:
                precision = btc_info.get('quantityPrecision', 'unknown')
                log_test("交易对信息", "PASS", 
                        f"活跃交易对: {len(symbols)}个, BTC精度: {precision}")
                return True
    except Exception as e:
        log_test("交易对信息", "FAIL", str(e))
        return False

def test_market_price():
    """测试4: 行情数据"""
    try:
        req = urllib.request.Request("https://fapi.binance.com/fapi/v1/ticker/price?symbol=BTCUSDT")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            price = float(data['price'])
            log_test("行情数据", "PASS", f"BTC价格: ${price:,.2f}")
            return True
    except Exception as e:
        log_test("行情数据", "FAIL", str(e))
        return False

def test_position_info():
    """测试5: 持仓查询"""
    result = make_request("/fapi/v2/positionRisk")
    if result["success"]:
        positions = result["data"]
        active_pos = [p for p in positions if float(p.get('positionAmt', 0)) != 0]
        log_test("持仓查询", "PASS", f"当前持仓: {len(active_pos)} 个")
        return True
    else:
        error = result["error"]
        log_test("持仓查询", "FAIL", f"错误: {error}")
        return False

def test_open_orders():
    """测试6: 当前订单"""
    result = make_request("/fapi/v1/openOrders")
    if result["success"]:
        orders = result["data"]
        log_test("当前订单", "PASS", f"活跃订单: {len(orders)} 个")
        return True
    else:
        error = result["error"]
        log_test("当前订单", "FAIL", f"错误: {error}")
        return False

def test_order_book():
    """测试7: 订单簿深度"""
    try:
        req = urllib.request.Request("https://fapi.binance.com/fapi/v1/depth?symbol=BTCUSDT&limit=5")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            bids = len(data.get('bids', []))
            asks = len(data.get('asks', []))
            log_test("订单簿深度", "PASS", f"买{bids}/卖{asks}档")
            return True
    except Exception as e:
        log_test("订单簿深度", "FAIL", str(e))
        return False

def test_listen_key():
    """测试8: WebSocket连接密钥"""
    result = make_request("/fapi/v1/listenKey", method="POST")
    if result["success"]:
        key = result["data"].get('listenKey', 'none')
        log_test("WebSocket密钥", "PASS", f"密钥: {key[:20]}...")
        return True
    else:
        error = result["error"]
        log_test("WebSocket密钥", "FAIL", f"错误: {error}")
        return False

def test_api_limits():
    """测试9: API限频"""
    start = time.time()
    success_count = 0
    
    for i in range(10):
        result = make_request("/fapi/v1/ticker/price?symbol=BTCUSDT")
        if result["success"]:
            success_count += 1
        time.sleep(0.1)  # 100ms间隔
    
    elapsed = time.time() - start
    rate = success_count / elapsed * 60  # 每分钟请求数
    
    log_test("API限频测试", "PASS" if success_count == 10 else "WARN",
            f"10次请求成功{success_count}次, 速率: {rate:.0f}req/min")
    return success_count >= 8

def test_order_placement_simulation():
    """测试10: 下单参数验证"""
    # 获取BTC精度信息
    try:
        req = urllib.request.Request("https://fapi.binance.com/fapi/v1/exchangeInfo")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            btc_info = next((s for s in data['symbols'] if s['symbol'] == 'BTCUSDT'), None)
            
            if btc_info:
                qty_precision = btc_info.get('quantityPrecision', 3)
                price_precision = btc_info.get('pricePrecision', 2)
                
                # 测试不同精度的数量
                test_qty = 0.00385  # 5位小数
                
                # 正确的精度处理
                if qty_precision == 3:
                    correct_qty = round(test_qty, 3)  # 0.004
                else:
                    correct_qty = round(test_qty, qty_precision)
                
                log_test("下单精度验证", "PASS",
                        f"数量精度: {qty_precision}位, 价格精度: {price_precision}位, "
                        f"测试数量 {test_qty} -> {correct_qty}")
                return True
    except Exception as e:
        log_test("下单精度验证", "FAIL", str(e))
        return False

def main():
    print("="*70)
    print("🔍 币安API稳定性全面测试")
    print("="*70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API密钥: {API_KEY[:20]}...")
    print("="*70)
    print()
    
    tests = [
        ("服务器时间同步", test_server_time),
        ("账户信息查询", test_account_info),
        ("交易对信息", test_exchange_info),
        ("行情数据", test_market_price),
        ("持仓查询", test_position_info),
        ("当前订单", test_open_orders),
        ("订单簿深度", test_order_book),
        ("WebSocket密钥", test_listen_key),
        ("API限频测试", test_api_limits),
        ("下单精度验证", test_order_placement_simulation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            log_test(name, "ERROR", str(e))
            results.append((name, False))
        time.sleep(0.5)  # 避免请求过快
    
    print()
    print("="*70)
    print("📊 测试结果汇总")
    print("="*70)
    
    passed = sum(1 for _, r in results if r)
    failed = len(results) - passed
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:<20}: {status}")
    
    print("-"*70)
    print(f"总计: {len(results)} 项 | ✅ 通过: {passed} | ❌ 失败: {failed}")
    print("="*70)
    
    # 稳定性评估
    success_rate = passed / len(results)
    print()
    if success_rate == 1.0:
        print("🎉 API稳定性: 优秀 (100%)")
        print("✅ 可以安全进行高频交易")
    elif success_rate >= 0.8:
        print("⚠️  API稳定性: 良好 (80%+)")
        print("⚠️  可以进行交易，但建议降低频率")
    elif success_rate >= 0.6:
        print("⚠️  API稳定性: 一般 (60%+)")
        print("❌ 不建议高频交易，需修复问题")
    else:
        print("❌ API稳定性: 差 (<60%)")
        print("❌ 必须先修复API问题才能交易")
    
    # 具体问题分析
    print()
    print("🔍 关键问题分析:")
    
    failed_tests = [name for name, r in results if not r]
    if failed_tests:
        print(f"   失败的测试: {', '.join(failed_tests)}")
        
        if "账户信息查询" in failed_tests or "持仓查询" in failed_tests:
            print("   ⚠️  Signature认证问题 - 需要重新生成API密钥")
        if "服务器时间同步" in failed_tests:
            print("   ⚠️  时间同步问题 - 需要同步系统时间")
        if "API限频测试" in failed_tests:
            print("   ⚠️  限频问题 - 需要降低请求频率")
    else:
        print("   ✅ 无明显问题")
    
    print()
    print("💡 建议:")
    if failed == 0:
        print("   1. API连接稳定，可以开始高频交易")
        print("   2. 建议先用小资金测试")
        print("   3. 监控交易成功率")
    else:
        print("   1. 修复失败的API测试项")
        print("   2. 重新生成API密钥（如果Signature问题持续）")
        print("   3. 同步系统时间（如果时间差>1000ms）")
        print("   4. 测试通过后再进行高频交易")

if __name__ == "__main__":
    main()

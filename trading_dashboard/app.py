#!/usr/bin/env python3
"""
实时交易状态监控仪表盘
本地部署: http://localhost:8080
"""

import os
import json
import csv
import base64
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import urllib.request
import threading

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# ========== 配置 ==========
CONFIG = {
    "api_key": os.environ.get("BINANCE_API_KEY", ""),
    "api_secret": os.environ.get("BINANCE_API_SECRET", ""),
    "symbol": "BTCUSDT",
    "data_dir": os.path.expanduser("~/.openclaw/workspace/trading_data"),
    "refresh_interval": 5,  # 每5秒刷新一次数据
}

# 尝试从文件读取配置
config_file = os.path.expanduser("~/.openclaw/workspace/.binance_config.json")
if os.path.exists(config_file):
    try:
        with open(config_file, 'r') as f:
            file_config = json.load(f)
            CONFIG["api_key"] = file_config.get("api_key", CONFIG["api_key"])
            CONFIG["api_secret"] = file_config.get("api_secret", CONFIG["api_secret"])
    except Exception as e:
        print(f"[WARN] 读取配置文件失败: {e}")

# 缓存数据
cache = {
    "account": None,
    "position": None,
    "price": None,
    "price_history": [],
    "trades": [],
    "last_update": 0
}

# ========== API函数 ==========
def make_request(endpoint, params=None, base_url="https://fapi.binance.com", use_sign=True):
    """发送带签名的API请求 (HMAC SHA256)"""
    
    # 检查 API 密钥是否配置
    if use_sign and (not CONFIG["api_key"] or not CONFIG["api_secret"]):
        return {"error": "API key or secret not configured"}
    
    try:
        with urllib.request.urlopen("https://fapi.binance.com/fapi/v1/time", timeout=10) as resp:
            server_time = json.loads(resp.read().decode())['serverTime']
    except:
        server_time = int(time.time() * 1000)
    
    if params is None:
        params = {}
    
    if use_sign:
        params['timestamp'] = server_time
        
        # HMAC SHA256 签名
        payload = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            CONFIG["api_secret"].encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        url = f"{base_url}{endpoint}?{payload}&signature={signature}"
        headers = {'X-MBX-APIKEY': CONFIG["api_key"]}
    else:
        # 公共 API 不需要签名
        if params:
            url = f"{base_url}{endpoint}?" + '&'.join([f"{k}={v}" for k, v in params.items()])
        else:
            url = f"{base_url}{endpoint}"
        headers = {}
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode())
            return {"code": err.get('code'), "msg": err.get('msg'), "error": True}
        except:
            return {"code": e.code, "msg": str(e.reason), "error": True}
    except Exception as e:
        return {"error": str(e)}

# ========== 数据更新 ==========
def update_data():
    """更新缓存数据"""
    try:
        # 获取账户信息 (需要签名)
        if CONFIG["api_key"] and CONFIG["api_secret"]:
            account_result = make_request("/fapi/v2/account", use_sign=True)
            if "error" not in account_result and "msg" not in account_result:
                cache["account"] = account_result
                print(f"[INFO] 账户数据更新成功: {account_result.get('totalWalletBalance', 'N/A')} USDT")
            else:
                print(f"[WARN] 账户API错误: {account_result}")
        
        # 获取持仓 (需要签名)
        if CONFIG["api_key"] and CONFIG["api_secret"]:
            result = make_request("/fapi/v2/positionRisk", {"symbol": CONFIG["symbol"]}, use_sign=True)
            if isinstance(result, list):
                cache["position"] = next((p for p in result if p['symbol'] == CONFIG["symbol"]), None)
        
        # 获取价格 (公共API，不需要签名)
        result = make_request("/fapi/v1/ticker/price", {"symbol": CONFIG["symbol"]}, use_sign=False)
        if 'price' in result:
            cache["price"] = float(result['price'])
            cache["price_history"].append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "price": cache["price"]
            })
            # 只保留最近100个价格点
            if len(cache["price_history"]) > 100:
                cache["price_history"] = cache["price_history"][-100:]
        
        # 读取交易日志
        today = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(CONFIG["data_dir"], f"trades_{today}.log")
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                cache["trades"] = lines[-20:]  # 最近20条日志
        else:
            # 尝试读取其他日志文件
            for log_name in ['LIVE_MONITOR.log', 'FIXED_MONITOR.log', 'ACTIVE_TRADING.log']:
                alt_log = os.path.join(CONFIG["data_dir"], log_name)
                if os.path.exists(alt_log):
                    with open(alt_log, 'r') as f:
                        lines = f.readlines()
                        cache["trades"] = lines[-20:]
                    break
        
        cache["last_update"] = time.time()
        
    except Exception as e:
        print(f"[ERROR] 更新数据失败: {e}")

def background_updater():
    """后台数据更新线程"""
    while True:
        update_data()
        time.sleep(CONFIG["refresh_interval"])

# ========== 路由 ==========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """获取当前状态"""
    update_data()  # 强制更新
    
    data = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "account": None,
        "position": cache["position"],
        "price": cache["price"],
        "price_history": cache["price_history"],
        "trades": cache["trades"]
    }
    
    if cache["account"] and 'totalWalletBalance' in cache["account"]:
        initial = 50  # 初始资金
        current = float(cache["account"]['totalWalletBalance'])
        pnl = current - initial
        pnl_pct = (pnl / initial) * 100 if initial > 0 else 0
        
        data["account"] = {
            "balance": current,
            "initial": initial,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "available": float(cache["account"]['availableBalance']),
            "unrealized": float(cache["account"]['totalUnrealizedProfit'])
        }
    
    return jsonify(data)

@app.route('/api/history')
def get_history():
    """获取价格历史"""
    return jsonify(cache["price_history"])

# ========== 启动 ==========
if __name__ == '__main__':
    print("="*50)
    print("🚀 交易监控仪表盘启动中...")
    print("="*50)
    
    # 启动后台更新线程
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    
    # 初始数据加载
    update_data()
    
    print("📊 监控地址: http://localhost:8080")
    print("📈 API地址: http://localhost:8080/api/status")
    print("⏱️  刷新间隔: 5秒")
    print("="*50)
    
    # 启动Flask
    app.run(host='0.0.0.0', port=18080, debug=False, use_reloader=False)

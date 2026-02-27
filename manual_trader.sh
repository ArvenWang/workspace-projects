#!/bin/bash
# 手动交易监控脚本
echo "=== 手动交易监控启动 ==="
echo "$(date): 开始监控市场..."

while true; do
    python3 << 'PYEOF'
import time, json, base64, urllib.request
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import os

API_KEY = "Rzb1qhBd3BkIGLCO4rH7pTjPt1KZpq7lbgfIp0np81gOdq6xF9p7oFzqXq0cpLvs"
PRIVATE_KEY_B64 = "MC4CAQAwBQYDK2VwBCIEIISJgEmcDMko/bVi5n3nkDxNHpztDrqB08Ug5gGLDjdF"

full_key = base64.b64decode(PRIVATE_KEY_B64)
seed = full_key[16:48]
private_key = Ed25519PrivateKey.from_private_bytes(seed)

def api_call(endpoint, params=None, base_url="https://fapi.binance.com"):
    try:
        req = urllib.request.Request("https://api.binance.com/api/v3/time")
        with urllib.request.urlopen(req, timeout=5) as resp:
            ts = json.loads(resp.read().decode())['serverTime']
    except:
        ts = int(time.time() * 1000)
    
    if params is None:
        params = {}
    params['timestamp'] = ts
    
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    sig = base64.b64encode(private_key.sign(query.encode('utf-8'))).decode('utf-8')
    
    url = f"{base_url}{endpoint}?{query}&signature={sig}"
    req = urllib.request.Request(url, headers={'X-MBX-APIKEY': API_KEY})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

# 获取价格和账户
price_data = api_call("/fapi/v1/ticker/price", {"symbol": "BTCUSDT"})
account = api_call("/fapi/v2/account")

log_file = os.path.expanduser("~/.openclaw/workspace/trading_data/MANUAL_MONITOR.log")

if 'price' in price_data and 'totalWalletBalance' in account:
    price = float(price_data['price'])
    balance = float(account['totalWalletBalance'])
    pnl = balance - 50
    
    timestamp = time.strftime('%H:%M:%S')
    msg = f"[{timestamp}] BTC: ${price:,.2f} | 余额: ${balance:.2f} ({pnl:+.2f})"
    print(msg)
    
    with open(log_file, "a") as f:
        f.write(msg + "\n")
else:
    print(f"[{time.strftime('%H:%M:%S')}] 数据获取失败")
PYEOF
    sleep 30
done

#!/usr/bin/env python3
"""
API稳定性优化器
解决Ed25519 + VPN间歇性问题
"""

import requests
import time
import json
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from functools import wraps

API_KEY = "Rzb1qhBd3BkIGLCO4rH7pTjPt1KZpq7lbgfIp0np81gOdq6xF9p7oFzqXq0cpLvs"
PRIVATE_KEY_B64 = "MC4CAQAwBQYDK2VwBCIEIISJgEmcDMko/bVi5n3nkDxNHpztDrqB08Ug5gGLDjdF"

full_key = base64.b64decode(PRIVATE_KEY_B64)
seed = full_key[16:48]
private_key = Ed25519PrivateKey.from_private_bytes(seed)

class BinanceAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': API_KEY,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.base_url = "https://fapi.binance.com"
        self.success_count = 0
        self.fail_count = 0
        
    def get_time(self):
        """获取服务器时间 - 带缓存"""
        try:
            r = self.session.get("https://api.binance.com/api/v3/time", timeout=10)
            return r.json()['serverTime']
        except:
            return int(time.time() * 1000)
    
    def call(self, endpoint, params, method="GET", max_retries=5):
        """优化的API调用"""
        for attempt in range(max_retries):
            try:
                # 获取时间
                ts = self.get_time()
                params['timestamp'] = ts
                
                # 构建签名
                query = '&'.join([f"{k}={v}" for k, v in params.items()])
                sig = base64.b64encode(private_key.sign(query.encode('utf-8'))).decode('utf-8')
                
                if method == "GET":
                    url = f"{self.base_url}{endpoint}?{query}&signature={sig}"
                    r = self.session.get(url, timeout=20)
                else:
                    url = f"{self.base_url}{endpoint}"
                    data = f"{query}&signature={sig}"
                    r = self.session.post(url, data=data, timeout=20)
                
                result = r.json()
                
                # 检查签名错误
                if isinstance(result, dict) and result.get('code') == -1022:
                    if attempt < max_retries - 1:
                        time.sleep(0.3 * (attempt + 1))  # 指数退避
                        continue
                
                if 'code' not in result or result.get('code') >= 0:
                    self.success_count += 1
                    return result
                else:
                    return result
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return {"error": "Timeout"}
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
                return {"error": str(e)}
        
        self.fail_count += 1
        return {"error": "Max retries exceeded"}
    
    def get_stats(self):
        total = self.success_count + self.fail_count
        if total == 0:
            return "无数据"
        success_rate = (self.success_count / total) * 100
        return f"成功率: {success_rate:.1f}% ({self.success_count}/{total})"

if __name__ == "__main__":
    api = BinanceAPI()
    
    print("=== API稳定性测试 ===")
    print("测试10次连接...")
    
    for i in range(10):
        result = api.call("/fapi/v2/account", {})
        if 'totalWalletBalance' in result:
            print(f"  测试{i+1}: ✅ 成功")
        else:
            print(f"  测试{i+1}: ❌ 失败 - {result.get('error', result.get('msg', 'Unknown'))}")
        time.sleep(0.5)
    
    print(f"\n{api.get_stats()}")

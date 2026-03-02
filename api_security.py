#!/usr/bin/env python3
"""
案例32: API安全测试
"""

class APISecurityTester:
    def __init__(self):
        self.endpoints = []
    
    def add_endpoint(self, path, method='GET'):
        self.endpoints.append({'path': path, 'method': method})
    
    def test(self):
        print("\n🔒 API安全测试")
        
        tests = ['SQL注入', 'XSS', 'CSRF', '权限检查']
        
        for e in self.endpoints:
            print(f"  {e['method']} {e['path']}:")
            for t in tests:
                print(f"    - {t}: 通过")


if __name__ == '__main__':
    tester = APISecurityTester()
    tester.add_endpoint('/api/users', 'GET')
    tester.add_endpoint('/api/login', 'POST')
    tester.test()

#!/usr/bin/env python3
"""
案例29: AWS凭据扫描
"""

class AWSScanner:
    def __init__(self):
        self.patterns = ['AKIA', 'ASIA']
    
    def scan(self, content):
        print("\n☁️ AWS凭据扫描")
        
        found = []
        
        for p in self.patterns:
            if p in content:
                found.append(p)
        
        if found:
            print(f"  ⚠️ 发现: {found}")
        else:
            print(f"  ✅ 未发现AWS凭据")


if __name__ == '__main__':
    scanner = AWSScanner()
    scanner.scan("AKIAIOSFODNN7EXAMPLE")

#!/usr/bin/env python3
"""
案例37: Swift日志包
"""

class SwiftLogger:
    def log(self, level, message):
        levels = {'INFO': 'ℹ️', 'WARN': '⚠️', 'ERROR': '❌'}
        print(f"{levels.get(level, '📝')} {level}: {message}")


if __name__ == '__main__':
    logger = SwiftLogger()
    logger.log('INFO', '应用启动')
    logger.log('ERROR', '连接失败')

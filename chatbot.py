#!/usr/bin/env python3
"""
客服聊天机器人 - 完整版
功能：
1. 多轮对话
2. 意图识别
3. 自动回复
4. 知识库问答
5. 转人工判断

依赖：
pip3 install requests

运行：
python3 chatbot.py train
python3 chatbot.py chat
python3 chatbot.py test
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

# 配置
DATA_DIR = os.path.expanduser('~/.chatbot')
INTENTS_FILE = os.path.join(DATA_DIR, 'intents.json')
KB_FILE = os.path.join(DATA_DIR, 'knowledge.json')
CHAT_HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')

Path(DATA_DIR).mkdir(parents=True, exist_ok=True)


class ChatBot:
    def __init__(self):
        self.intents = self.load_intents()
        self.knowledge = self.load_knowledge()
        self.history = []
    
    def load_intents(self):
        """加载意图配置"""
        default_intents = {
            "greeting": {
                "patterns": ["你好", "hello", "hi", "您好", "在吗"],
                "responses": ["您好！有什么可以帮您？", "你好！请问有什么问题？"]
            },
            "thanks": {
                "patterns": ["谢谢", "感谢", "感谢你", "thx"],
                "responses": ["不客气！还有其他问题吗？", "很高兴帮到您！"]
            },
            "bye": {
                "patterns": ["再见", "拜拜", "bye", "晚安"],
                "responses": ["再见！有问题随时找我~", "拜拜，祝您愉快！"]
            },
            "help": {
                "patterns": ["帮助", "help", "怎么用", "使用方法"],
                "responses": ["我可以帮您解答问题，请直接问我~"]
            },
            "price": {
                "patterns": ["价格", "多少钱", "费用", "收费"],
                "responses": ["请问您想了解哪个产品？"]
            },
            "refund": {
                "patterns": ["退款", "退货", "换货"],
                "responses": ["退款申请我已记录，客服会尽快处理。"]
            }
        }
        
        if os.path.exists(INTENTS_FILE):
            with open(INTENTS_FILE) as f:
                return json.load(f)
        else:
            with open(INTENTS_FILE, 'w') as f:
                json.dump(default_intents, f, indent=2, ensure_ascii=False)
            return default_intents
    
    def load_knowledge(self):
        """加载知识库"""
        default_kb = {
            "shipping": {
                "question": ["发货", "物流", "快递", "什么时候发"],
                "answer": "正常情况下48小时内发货，快递一般2-3天到达。"
            },
            "return": {
                "question": ["退货", "退款", "7天无理由"],
                "answer": "支持7天无理由退货，请联系客服申请。"
            },
            "vip": {
                "question": ["会员", "VIP", "优惠", "折扣"],
                "answer": "当前会员季卡8折，年卡7折，联系客服了解详情。"
            }
        }
        
        if os.path.exists(KB_FILE):
            with open(KB_FILE) as f:
                return json.load(f)
        else:
            with open(KB_FILE, 'w') as f:
                json.dump(default_kb, f, indent=2, ensure_ascii=False)
            return default_kb
    
    def match_intent(self, message):
        """匹配意图"""
        message_lower = message.lower()
        
        # 匹配意图
        for intent_name, intent_data in self.intents.items():
            for pattern in intent_data["patterns"]:
                if pattern.lower() in message_lower:
                    import random
                    response = random.choice(intent_data["responses"])
                    return {
                        "intent": intent_name,
                        "response": response,
                        "confidence": 0.9
                    }
        
        # 匹配知识库
        for kb_name, kb_data in self.knowledge.items():
            for q in kb_data["question"]:
                if q in message_lower:
                    return {
                        "intent": "knowledge",
                        "response": kb_data["answer"],
                        "confidence": 0.8
                    }
        
        # 默认回复
        return {
            "intent": "unknown",
            "response": "抱歉，我不太明白您的意思。请联系人工客服。",
            "confidence": 0.1
        }
    
    def chat(self, message):
        """聊天"""
        # 记录历史
        self.history.append({
            "role": "user",
            "content": message,
            "time": datetime.now().isoformat()
        })
        
        # 获取回复
        result = self.match_intent(message)
        
        # 记录回复
        self.history.append({
            "role": "bot",
            "content": result["response"],
            "intent": result["intent"],
            "time": datetime.now().isoformat()
        })
        
        return result
    
    def add_intent(self, name, patterns, responses):
        """添加意图"""
        self.intents[name] = {
            "patterns": patterns,
            "responses": responses
        }
        with open(INTENTS_FILE, 'w') as f:
            json.dump(self.intents, f, indent=2, ensure_ascii=False)
        print(f"✅ 已添加意图: {name}")
    
    def add_knowledge(self, question, answer):
        """添加知识"""
        key = f"kb_{len(self.knowledge) + 1}"
        self.knowledge[key] = {
            "question": question if isinstance(question, list) else [question],
            "answer": answer
        }
        with open(KB_FILE, 'w') as f:
            json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
        print("✅ 已添加知识")


def interactive_chat():
    """交互式聊天"""
    bot = ChatBot()
    
    print("\n" + "="*50)
    print("🤖 客服机器人 - 对话模式")
    print("="*50)
    print("输入 'quit' 退出")
    print()
    
    while True:
        try:
            user_input = input("你: ").strip()
            
            if not user_input:
                continue
            if user_input.lower() in ['quit', '退出', 'q']:
                print("再见！")
                break
            
            result = bot.chat(user_input)
            print(f"🤖: {result['response']}")
            print()
            
        except KeyboardInterrupt:
            print("\n再见！")
            break


def test_bot():
    """测试机器人"""
    bot = ChatBot()
    
    print("\n🧪 客服机器人测试")
    print("="*50)
    
    test_messages = [
        "你好",
        "我想问一下价格",
        "怎么发货？",
        "谢谢",
        "再见"
    ]
    
    for msg in test_messages:
        result = bot.chat(msg)
        print(f"\n用户: {msg}")
        print(f"机器人: {result['response']}")
        print(f"意图: {result['intent']}")
    
    print("\n" + "="*50)
    print("✅ 测试完成")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
客服机器人 - 使用说明

使用:
  python3 chatbot.py chat      # 交互对话
  python3 chatbot.py test     # 测试
  python3 chatbot.py add-intent <名称> <关键词> <回复>
  python3 chatbot.py add-kb <问题关键词> <答案>

示例:
  python3 chatbot.py chat
  python3 chatbot.py test
  python3 chatbot.py add-intent "订单" ["订单","查单"] "订单查询请提供订单号"
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'chat':
        interactive_chat()
    elif cmd == 'test':
        test_bot()
    else:
        print("未知命令")


if __name__ == '__main__':
    main()

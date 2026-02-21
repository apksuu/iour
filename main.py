import os
import asyncio
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession

# ================= 核心配置区 =================
SIGN_COMMAND = '/qd'  # 你要发送的签到指令
# ============================================

# 环境变量校验
try:
    api_id = int(os.environ['API_ID'])
    api_hash = os.environ['API_HASH']
    session_string = os.environ['SESSION_STRING']
    bot_username = os.environ['BOT_USERNAME']
except KeyError as e:
    print(f"❌ 启动失败：缺少环境变量 {e}")
    sys.exit(1)
except ValueError:
    print("❌ 启动失败：API_ID 格式错误，必须是数字！")
    sys.exit(1)

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def main():
    print("⏳ 正在连接 Telegram 服务器...")
    await client.start()
    print("✅ 云端账号登录成功！\n")
    
    # 1. 发送签到指令
    print(f"➡️ 向机器人 {bot_username} 发送签到指令: {SIGN_COMMAND}")
    await client.send_message(bot_username, SIGN_COMMAND)
    
    # 2. 5秒超时监听机制
    print("⏳ 正在等待机器人回复 (5秒超时机制)...")
    reply_received = False
    
    # 循环 5 次，每次等 1 秒。收到回复就立刻停止等待。
    for i in range(5):
        await asyncio.sleep(1) 
        
        # 获取聊天框里最新的一条消息
        messages = await client.get_messages(bot_username, limit=1)
        if not messages:
            continue
            
        msg = messages[0]
        
        # 如果这条最新消息是机器人发的 (out 为 False)，说明它回复了！
        if not msg.out:
            print("\n" + "="*20 + " 签到结果 " + "="*20)
            print(f"📩 成功获取机器人回复：\n{msg.text}")
            print("="*50 + "\n")
            reply_received = True
            break # 拿到结果，立刻跳出循环，不用死等
            
    # 如果循环走完（过了 5 秒），reply_received 依然是 False
    if not reply_received:
        print("\n❌ 签到失败：5秒超时，机器人未做任何响应（可能是卡了或者挂了）。")

# 启动执行
with client:
    client.loop.run_until_complete(main())

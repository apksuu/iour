import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

# 获取环境变量
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
session_string = os.environ['SESSION_STRING']
bot_username = os.environ['BOT_USERNAME']

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def main():
    await client.start()
    print("✅ 登录成功")
    
    # 唤醒机器人
    await client.send_message(bot_username, '/start')
    await asyncio.sleep(5)
    
    # 获取回复
    messages = await client.get_messages(bot_username, limit=1)
    if not messages or messages[0].out:
        print("❌ 机器人未回复")
        return

    msg = messages[0]
    if msg.buttons:
        print("✅ 发现按钮，尝试点击...")
        # 注意此处的缩进层级
        result = await msg.click(0)
        
        if result and hasattr(result, 'message') and result.message:
            print(f"🎈 弹窗文字: {result.message}")
        else:
            print("🎈 点击完成（无弹窗文字）")
            # 如果没有弹窗，尝试输出消息正文，也许签到结果在正文里
            print(f"🤖 当前消息正文: {msg.text}")
    else:
        print("❌ 消息中没有按钮")

with client:
    client.loop.run_until_complete(main())

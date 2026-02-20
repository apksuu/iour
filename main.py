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
        result = await msg.click(0)
        
        # 尝试捕获底层弹窗
        if result and hasattr(result, 'message') and result.message:
            print(f"🎈 弹窗文字: {result.message}")
        else:
            print("🎈 没有底层弹窗文字返回。")
            
        # 核心新增逻辑：等待机器人处理，然后抓取最新的聊天界面
        print("⏳ 等待 3 秒，获取机器人最终的文字反馈...")
        await asyncio.sleep(3)
        
        # 获取最新的两条消息，防止机器人发了新消息我们没看到
        final_messages = await client.get_messages(bot_username, limit=2)
        print("====================================")
        print("🤖 机器人的最终状态/回复如下：")
        for m in final_messages:
            if not m.out: # 过滤掉我们自己发的话，只看机器人的
                print(f"👉 {m.text}")
        print("====================================")
        
    else:
        print("❌ 消息中没有按钮")

with client:
    client.loop.run_until_complete(main())

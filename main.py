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
    
    # 等待机器人回复面板
    await asyncio.sleep(5)
    
    # 获取回复
    messages = await client.get_messages(bot_username, limit=1)
    if not messages or messages[0].out:
        print("❌ 机器人未回复")
        return

    msg = messages[0]
    if msg.buttons:
        print("✅ 发现按钮面板，正在精准匹配“签到”按钮...")
        try:
            # 核心：自动匹配包含“签到”字样的按钮（比如“✅签到”）并点击
            result = await msg.click(text='签到')
            
            # 核心：捕获并打印点击后的半透明弹窗 (Toast) 内容
            if result and hasattr(result, 'message') and result.message:
                print("====================================")
                print(f"🎈 机器人弹窗成功捕获: 【{result.message}】")
                print("====================================")
            else:
                print("🎈 点击已发送，但该机器人没有返回底层弹窗文字。")
                
        except Exception as e:
            print(f"❌ 完蛋，点击失败！报错信息: {e}")
    else:
        print("❌ 消息中没有按钮")

with client:
    client.loop.run_until_complete(main())

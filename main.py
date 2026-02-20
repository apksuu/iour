import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

# 从 GitHub Secrets 读取环境变量
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
session_string = os.environ['SESSION_STRING']
bot_username = os.environ['BOT_USERNAME']

# 使用 StringSession 免验证码登录
client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def main():
    await client.start()
    print("✅ 云端账号登录成功！")
    
    # 获取与该机器人的最新一条聊天记录
    messages = await client.get_messages(bot_username, limit=1)
    
    if messages:
        message = messages[0]
        # 检查消息中是否带有内联按钮
        if message.buttons:
            # 点击第一个按钮 (索引从0开始)
            await message.click(0) 
            print("✅ 已成功点击签到按钮！")
        else:
            print("❌ 最新消息中未找到按钮，或者机器人尚未回复。")
            # 备选方案：如果需要发送文字签到，取消下面这行的注释
            # await client.send_message(bot_username, '签到')

with client:
    client.loop.run_until_complete(main())

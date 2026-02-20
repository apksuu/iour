import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

# 从 GitHub Secrets 读取环境变量
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
session_string = os.environ['SESSION_STRING']
bot_username = os.environ['BOT_USERNAME']

# 触发机器人签到面板的指令，根据你的机器人实际情况修改
# 比如 '/start', '/sign', '签到' 等
TRIGGER_COMMAND = '/start' 

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def main():
    await client.start()
    print("✅ 云端账号登录成功！")
    
    # 1. 发送触发指令
    print(f"➡️ 正在发送触发指令: {TRIGGER_COMMAND}")
    await client.send_message(bot_username, TRIGGER_COMMAND)
    
    # 2. 等待机器人回复 (暂停 5 秒，如果机器人反应慢可以改长一点)
    print("⏳ 等待机器人回复...")
    await asyncio.sleep(5)
    
    # 3. 获取最新的一条消息
    messages = await client.get_messages(bot_username, limit=1)
    
    if messages:
        message = messages[0]
        
        # 判断 1：这条最新消息是不是自己发的？
        if message.out == True:
            print("❌ 签到失败：等待了 5 秒，机器人没有回复！最新消息还是我们自己发的指令。")
            return # 结束执行
            
        # 判断 2：机器人回复了，但里面有没有内联按钮？
        if message.buttons:
            print("✅ 成功获取到机器人的回复面板！")
            
            # 4. 点击第一个按钮 (索引从 0 开始。如果是第二行的第一个按钮，则是 click(1, 0))
            await message.click(0) 
            print("🎉 已成功发送点击动作！")
            
            # 可选：再等 2 秒，看看点击后机器人有没有弹出签到成功的提示
            await asyncio.sleep(2)
            final_messages = await client.get_messages(bot_username, limit=1)
            print(f"🤖 机器人最终反馈: {final_messages[0].text}")
            
        else:
            print("❌ 机器人回复了，但是消息里没有找到任何按钮。")
            print(f"机器人的回复内容是: {message.text}")
    else:
        print("❌ 没有任何聊天记录。")

with client:
    client.loop.run_until_complete(main())

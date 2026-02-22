import os
import asyncio
import sys
import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession

# ================= 1. 严格校验环境变量 =================
try:
    api_id = int(os.environ['API_ID'])
    api_hash = os.environ['API_HASH']
    session_string = os.environ['SESSION_STRING']
    bot1_username = os.environ['BOT_USERNAME'] 
except KeyError as e:
    print(f"❌ 启动失败：缺少环境变量 {e}")
    sys.exit(1)

# ================= 2. 终极任务配置区 =================
# 格式说明：
# 1. 纯文字回复类：('用户名', '发什么指令', 'text', 需要等几条回复)
# 2. 按钮点击类：  ('用户名', '发什么指令', 'button', '要点击的按钮文字')

BOTS_CONFIG = [
    # ---- 纯文字签到阵营 ----
    (bot1_username, '/qd', 'text', 1),           # 第 1 个：环境变量读取
    ('@aisgk1', '/sign', 'text', 2),             # 第 2 个：等 2 条回复
    ('@JiuGuanABot', '/checkin', 'text', 1),     # 第 3 个：等 1 条回复
    
    # ---- 按钮点击签到阵营 ----
    ('@NaixiAccountBot', '/start', 'button', '✅签到') # 第 4 个：点按钮
]
# ===================================================

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def handle_text_bot(bot_username, command, expected_msgs):
    """处理纯文字回复的机器人"""
    print(f"➡️ [纯文字模式] 向 {bot_username} 发送: {command}")
    try:
        command_msg = await client.send_message(bot_username, command)
        
        for _ in range(8):
            await asyncio.sleep(1)
            messages = await client.get_messages(bot_username, limit=expected_msgs)
            
            if len(messages) >= expected_msgs and all(m.id > command_msg.id for m in messages):
                print(f"✅ {bot_username} 成功回复：\n   {messages[0].text[:80]}...")
                return
                
        print(f"⚠️ {bot_username} 回复超时。")
    except Exception as e:
        print(f"❌ {bot_username} 任务出错: {e}")

async def handle_button_bot(bot_username, command, button_text):
    """处理需要点击按钮的机器人"""
    print(f"➡️ [按键模式] 向 {bot_username} 发送唤醒指令: {command}")
    try:
        await client.send_message(bot_username, command)
        await asyncio.sleep(5) # 给它 5 秒钟把面板弹出来
        
        messages = await client.get_messages(bot_username, limit=1)
        if not messages or messages[0].out:
            print(f"❌ {bot_username} 未回复面板。")
            return
            
        msg = messages[0]
        if msg.buttons:
            print(f"🔍 发现面板，正在尝试点击【{button_text}】...")
            result = await msg.click(text=button_text)
            
            toast = getattr(result, 'message', None) if result else None
            if toast:
                print(f"🎉 成功捕获弹窗：【{toast}】")
            else:
                print("🎈 点击动作已成功发送（该机器人无底层弹窗文字）。")
        else:
            print(f"❌ {bot_username} 回复了，但没有带按钮面板。")
            
    except Exception as e:
        print(f"❌ {bot_username} 按钮点击出错: {e}")

async def main():
    print("⏳ 正在建立 Telegram 安全连接...")
    await client.start()
    print("✅ 云端账号身份验证成功！\n")
    
    print(f"🔍 任务开始：共有 {len(BOTS_CONFIG)} 个机器人的自动化任务...\n")
    print("=" * 45)
    
    # 挨个遍历处理所有机器人
    for bot, cmd, mode, extra in BOTS_CONFIG:
        if bot:
            if mode == 'text':
                await handle_text_bot(bot, cmd, extra)
            elif mode == 'button':
                await handle_button_bot(bot, cmd, extra)
            
            print("-" * 45)
            await asyncio.sleep(3) # 停顿 3 秒防风控
        else:
            print("⚠️ 发现空的任务配置，已跳过。")
            print("-" * 45)

    # 生成运行记录
    print("\n📝 正在生成本地运行记录...")
    with open("last_run.txt", "w", encoding="utf-8") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"✅ 包含 {len(BOTS_CONFIG)} 个机器人的混合签到任务于 {now} 执行完毕")
    print("✅ 记录已生成，准备交由 GitHub Actions 自动提交。")

with client:
    client.loop.run_until_complete(main())

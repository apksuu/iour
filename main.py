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
BOTS_CONFIG = [
    # ---- 纯文字签到阵营 ----
    (bot1_username, '/qd', 'text', 1),           
    ('@aisgk1', '/sign', 'text', 2),             
    ('@JiuGuanABot', '/checkin', 'text', 1),     
    
    # ---- 坐标盲点阵营 ----
    # 'button_pos', (0, 1) 代表第0排的第1个（右上角）
    ('@NaixiAccountBot', '/start', 'button_pos', (0, 1)) 
]
# ===================================================

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def handle_text_bot(bot_username, command, expected_msgs):
    """处理纯文字回复的机器人"""
    print(f"➡️ [文字模式] 向 {bot_username} 发送: {command}")
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

async def handle_button_pos_bot(bot_username, command, pos):
    """处理按坐标精确点击的机器人"""
    print(f"➡️ [坐标模式] 向 {bot_username} 发送唤醒指令: {command}")
    try:
        await client.send_message(bot_username, command)
        await asyncio.sleep(5) # 等5秒钟弹面板
        
        messages = await client.get_messages(bot_username, limit=1)
        if not messages or messages[0].out:
            print(f"❌ {bot_username} 未回复面板。")
            return
            
        msg = messages[0] # 这个 msg 就是带按钮的那条面板消息
        
        if msg.buttons:
            row, col = pos
            try:
                target_button = msg.buttons[row][col]
                print(f"🔍 锁定坐标 ({row}, {col}) 的按钮：【{target_button.text}】，正在精准点击...")
                
                # 🌟 执行点击！
                result = await target_button.click()
                
                # ==== 捕获环节 1：检查有没有半透明弹窗 (比如“已经签到过了”) ====
                toast = getattr(result, 'message', None) if result else None
                if toast:
                    print(f"📢 捕获到底层弹窗：【{toast}】")
                
                # ==== 捕获环节 2：检查有没有下发新的文字消息 (比如“签到成功”) ====
                print("⏳ 正在等待机器人的后续文字反馈...")
                await asyncio.sleep(3) # 等待3秒让机器人把消息发出来
                
                # 往回看最新的2条消息
                new_msgs = await client.get_messages(bot_username, limit=2)
                found_new_text = False
                
                for m in new_msgs:
                    # 如果这条消息是机器人发的，且它的ID大于那条按钮面板的ID，说明是点击之后的新消息！
                    if not m.out and m.id > msg.id:
                        print(f"📩 收到最新文字反馈：\n----------------\n{m.text[:150]}...\n----------------")
                        found_new_text = True
                        break # 找到了就跳出循环
                        
                if not toast and not found_new_text:
                     print("🎈 坐标点击已完成，但机器人既没给弹窗，也没给新消息。")
                     
            except IndexError:
                print(f"❌ 找不到坐标为 ({row}, {col}) 的按钮！请检查坐标是否越界。")
        else:
            print(f"❌ {bot_username} 回复了，但没有带按钮面板。")
            
    except Exception as e:
        print(f"❌ {bot_username} 坐标点击出错: {e}")

async def main():
    print("⏳ 正在建立 Telegram 安全连接...")
    await client.start()
    print("✅ 云端账号身份验证成功！\n")
    
    print(f"🔍 任务开始：共有 {len(BOTS_CONFIG)} 个机器人的自动化任务...\n")
    print("=" * 45)
    
    for bot, cmd, mode, extra in BOTS_CONFIG:
        if bot:
            if mode == 'text':
                await handle_text_bot(bot, cmd, extra)
            elif mode == 'button_pos':
                await handle_button_pos_bot(bot, cmd, extra)
            
            print("-" * 45)
            await asyncio.sleep(3) 
        else:
            print("⚠️ 发现空的任务配置，已跳过。")
            print("-" * 45)

    with open("last_run.txt", "w", encoding="utf-8") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"✅ 包含 {len(BOTS_CONFIG)} 个机器人的混合签到任务于 {now} 执行完毕")
    print("\n✅ 运行记录已生成，准备交由 GitHub Actions 自动提交。")

with client:
    client.loop.run_until_complete(main())

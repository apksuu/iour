import os
import asyncio
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession

# ================= 核心配置区 =================
TRIGGER_COMMAND = '/start'      # 触发指令
TARGET_BUTTON_TEXT = '签到'    # 匹配按钮的文字
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

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def main():
    print("⏳ 正在连接 Telegram 服务器...")
    await client.start()
    print("✅ 云端账号登录成功！\n")
    
    # 1. 唤醒机器人
    print(f"➡️ 发送指令: {TRIGGER_COMMAND}")
    await client.send_message(bot_username, TRIGGER_COMMAND)
    await asyncio.sleep(5)
    
    # 2. 获取回复面板
    messages = await client.get_messages(bot_username, limit=1)
    if not messages or messages[0].out:
        print("❌ 机器人未回复")
        return

    msg = messages[0]
    old_text = msg.text # 记录点击前的文字

    if msg.buttons:
        print("🔍 扫描到按钮，正在尝试点击包含“签到”的按键...")
        try:
            # 3. 执行点击并深度抓取
            result = await msg.click(text=TARGET_BUTTON_TEXT)
            
            print("\n" + "="*20 + " 反馈追踪 " + "="*20)
            
            # --- 追踪方式 A: 捕获底层弹窗 (Toast) ---
            toast = getattr(result, 'message', None) if result else None
            if toast:
                print(f"📢 发现弹窗提示：【{toast}】")
            
            # --- 追踪方式 B: 检查面板文字是否发生变化 ---
            await asyncio.sleep(2)
            new_msg = await client.get_messages(bot_username, ids=msg.id)
            if new_msg and new_msg.text != old_text:
                print(f"📝 发现面板文字更新：\n----------------\n{new_msg.text}\n----------------")
            
            # --- 追踪方式 C: 检查是否下发了新消息 ---
            final_msgs = await client.get_messages(bot_username, limit=1)
            if final_msgs and not final_msgs[0].out and final_msgs[0].id != msg.id:
                print(f"📩 发现新发出的回复：\n【{final_msgs[0].text}】")
            
            if not toast and (not new_msg or new_msg.text == old_text):
                 print("ℹ️ 点击已完成，机器人无明显文字反馈。")
            
            print("="*48 + "\n")
                
        except Exception as e:
            print(f"❌ 点击失败: {e}")
    else:
        print("❌ 消息中没有按钮")

with client:
    client.loop.run_until_complete(main())

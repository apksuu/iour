import os
import asyncio
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession

# ================= 核心配置区 =================
# 你要发送的触发指令
TRIGGER_COMMAND = '/start'
# 你要点击的按钮包含的文字 (模糊匹配，包含这两个字就会去点)
TARGET_BUTTON_TEXT = '签到'
# ============================================

# 1. 强力校验环境变量，防止小白填错或漏填
try:
    api_id = int(os.environ['API_ID'])
    api_hash = os.environ['API_HASH']
    session_string = os.environ['SESSION_STRING']
    bot_username = os.environ['BOT_USERNAME']
except KeyError as e:
    print(f"❌ 启动失败：缺少必须的环境变量 {e}，请检查 GitHub Secrets 设置！")
    sys.exit(1)
except ValueError:
    print("❌ 启动失败：API_ID 格式错误，它必须是纯数字！")
    sys.exit(1)

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def main():
    print("⏳ 正在连接 Telegram 服务器...")
    await client.start()
    print("✅ 云端账号登录成功！\n")
    
    # 2. 唤醒机器人
    print(f"➡️ 向机器人 {bot_username} 发送唤醒指令: {TRIGGER_COMMAND}")
    await client.send_message(bot_username, TRIGGER_COMMAND)
    
    print("⏳ 等待机器人回复 (5秒)...\n")
    await asyncio.sleep(5)
    
    # 3. 获取最新回复
    messages = await client.get_messages(bot_username, limit=1)
    if not messages:
        print("❌ 签到中断：没有任何聊天记录。")
        return

    msg = messages[0]
    if msg.out:
        print("❌ 签到中断：机器人装死未回复，最新消息还是我们自己发送的指令。")
        return

    print("🤖 机器人的回复正文:")
    print(f"------------------------\n{msg.text}\n------------------------\n")

    # 4. 透视所有按钮并执行点击
    if msg.buttons:
        print("🔍 正在扫描机器人面板上的所有按钮：")
        # 遍历并打印所有按钮的名字，方便日后排错
        for row_idx, row in enumerate(msg.buttons):
            for col_idx, button in enumerate(row):
                print(f"  - 第{row_idx+1}行: 【{button.text}】")
                
        print(f"\n🎯 准备点击包含“{TARGET_BUTTON_TEXT}”的按钮...")
        try:
            # 核心：执行精准点击
            result = await msg.click(text=TARGET_BUTTON_TEXT)
            
            # 5. 捕获底层弹窗 (Toast Alert)
            if result and hasattr(result, 'message') and result.message:
                print("\n====================================")
                print(f"🎉 成功捕获机器人弹窗: 【{result.message}】")
                print("====================================\n")
            else:
                print("\n🎈 点击动作已成功发送，但该机器人没有返回半透明的弹窗提示。")
                
        except Exception as e:
            print(f"\n❌ 点击失败！可能是面板上根本没有带“{TARGET_BUTTON_TEXT}”字样的按钮。")
            print(f"详细错误日志: {e}")
    else:
        print("\n❌ 签到中断：机器人的回复中没有任何可点击的按钮面板。")

# 启动执行
with client:
    client.loop.run_until_complete(main())

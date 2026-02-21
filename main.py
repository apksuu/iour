import os
import asyncio
import sys
import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession

# ================= 核心配置区 =================
SIGN_COMMAND = '/qd'  # 你的签到指令
# ============================================

# 1. 严格的环境变量校验
try:
    api_id = int(os.environ['API_ID'])
    api_hash = os.environ['API_HASH']
    session_string = os.environ['SESSION_STRING']
    bot_username = os.environ['BOT_USERNAME']
except KeyError as e:
    print(f"❌ 启动失败：环境变量 {e} 未设置，请在 GitHub Secrets 中配置。")
    sys.exit(1)
except ValueError:
    print("❌ 启动失败：API_ID 必须是纯数字，请检查配置。")
    sys.exit(1)

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def main():
    print("⏳ 正在建立 Telegram 安全连接...")
    await client.start()
    print("✅ 云端账号身份验证成功！\n")
    
    # 2. 发送指令
    print(f"➡️ 正在向机器人 {bot_username} 发送指令: {SIGN_COMMAND}")
    await client.send_message(bot_username, SIGN_COMMAND)
    
    # 3. 智能等待机制（5秒超时，但收到回复会立刻停止）
    print("⏳ 正在实时监控机器人回复状态...")
    reply_received = False
    
    for i in range(5):
        await asyncio.sleep(1) # 每秒轮询一次
        messages = await client.get_messages(bot_username, limit=1)
        
        if messages:
            msg = messages[0]
            # 如果最新消息是对方发的，说明回复到了
            if not msg.out:
                print("\n" + "★" * 15 + " 签到反馈信息 " + "★" * 15)
                print(f"{msg.text}")
                print("★" * 44 + "\n")
                reply_received = True
                break
                
    if not reply_received:
        print("\n⚠️ 5秒内未检测到机器人文字回复，可能已超时或机器人处于离线状态。")

    # 4. 生成本地记录文件（用于触发 GitHub 自动提交）
    print(f"📝 正在生成本地运行记录...")
    with open("last_run.txt", "w", encoding="utf-8") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"GitHub Actions 上次成功执行时间: {now}")
    print("✅ 记录已生成。")

# 启动脚本
with client:
    client.loop.run_until_complete(main())

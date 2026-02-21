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
    bot1_username = os.environ['BOT_USERNAME'] # 第一个机器人从环境变量获取
except KeyError as e:
    print(f"❌ 启动失败：缺少必要的环境变量 {e}，请检查 GitHub Secrets！")
    sys.exit(1)
except ValueError:
    print("❌ 启动失败：API_ID 格式错误，必须是纯数字！")
    sys.exit(1)

# ================= 2. 机器人任务列表 =================
# 格式：('机器人用户名', '签到指令')
BOTS_TO_SIGN = [
    (bot1_username, '/qd'),               # 第一个机器人 (从环境变量读取)
    ('@aisgk11111bot', '/sign')   # <--- 请把这里替换成你第二个机器人的真实用户名！
]
# ===================================================

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def sign_single_bot(bot_username, command):
    """封装单个机器人的签到逻辑"""
    print(f"➡️ 正在向 {bot_username} 发送指令: {command}")
    try:
        await client.send_message(bot_username, command)
        
        # 5秒智能超时等待
        for _ in range(5):
            await asyncio.sleep(1)
            messages = await client.get_messages(bot_username, limit=1)
            
            if messages and not messages[0].out:
                print(f"✅ {bot_username} 成功回复：\n   {messages[0].text[:80]}...") # 打印前80个字
                return True
                
        print(f"⚠️ {bot_username} 5秒内未回复，已超时跳过。")
        return False
        
    except Exception as e:
        print(f"❌ 尝试联系 {bot_username} 时出错: {e}")
        return False

async def main():
    print("⏳ 正在建立 Telegram 安全连接...")
    await client.start()
    print("✅ 云端账号身份验证成功！\n")
    
    print(f"🔍 任务开始：共有 {len(BOTS_TO_SIGN)} 个机器人需要签到...\n")
    print("=" * 40)
    
    # 遍历列表，挨个给机器人发消息
    for bot, cmd in BOTS_TO_SIGN:
        if bot and bot != '@这里填第二个机器人的用户名': 
            await sign_single_bot(bot, cmd)
            print("-" * 40)
            # 两个机器人之间停顿 3 秒，防止被 Telegram 判定为发垃圾消息
            await asyncio.sleep(3)
        else:
            print("⚠️ 发现未配置用户名的机器人任务，已跳过。")
            print("-" * 40)

    # ================= 3. 生成运行记录用于 GitHub 自动提交 =================
    print("\n📝 正在生成本地运行记录...")
    with open("last_run.txt", "w", encoding="utf-8") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"✅ 双机器人签到任务于 {now} 成功执行完毕")
    print("✅ 记录已生成，准备交由 GitHub Actions 自动提交。")

# 启动脚本
with client:
    client.loop.run_until_complete(main())

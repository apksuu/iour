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

# ================= 2. 机器人任务配置区 =================
# 格式说明：('用户名', '指令', 等待它回复几条, 你要打印第几条)
# ※ 打印说明：0 代表最底下（最新）的一条，1 代表往上一条。

BOTS_TO_SIGN = [
    # 第 1 个机器人：发1条回1条，抓取最新的一条 (0)
    (bot1_username, '/qd', 1, 0),               
    
    # 第 2 个机器人：等它回够 2 条，然后抓取最底下那条 (0)
    ('@aisgk11111bot', '/sign', 2, 0)   
]
# ===================================================

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def sign_single_bot(bot_username, command, expected_msgs, fetch_index):
    """封装单个机器人的签到逻辑"""
    print(f"➡️ 正在向 {bot_username} 发送指令: {command}")
    try:
        # 发送指令，并记录这条指令的消息 ID
        command_msg = await client.send_message(bot_username, command)
        
        # 轮询等待（最长等待 8 秒，给第二个机器人留足发两句话的时间）
        for _ in range(8):
            await asyncio.sleep(1)
            # 抓取最新的 expected_msgs 条消息
            messages = await client.get_messages(bot_username, limit=expected_msgs)
            
            # 核心黑科技：确保抓到的这几条消息，全都是在我们发送指令【之后】才产生的！
            if len(messages) >= expected_msgs and all(m.id > command_msg.id for m in messages):
                print(f"✅ {bot_username} 成功回复：\n   {messages[fetch_index].text[:80]}...")
                return True
                
        print(f"⚠️ {bot_username} 超时，可能未发够 {expected_msgs} 条消息，已跳过。")
        return False
        
    except Exception as e:
        print(f"❌ 尝试联系 {bot_username} 时出错: {e}")
        return False

async def main():
    print("⏳ 正在建立 Telegram 安全连接...")
    await client.start()
    print("✅ 云端账号身份验证成功！\n")
    
    print(f"🔍 任务开始：共有 {len(BOTS_TO_SIGN)} 个机器人需要处理...\n")
    print("=" * 40)
    
    for bot, cmd, expected, fetch_idx in BOTS_TO_SIGN:
        if bot and bot != '@这里填第二个机器人的用户名': 
            await sign_single_bot(bot, cmd, expected, fetch_idx)
            print("-" * 40)
            await asyncio.sleep(3) # 停顿 3 秒防风控
        else:
            print("⚠️ 发现未配置用户名的机器人任务，已跳过。")
            print("-" * 40)

    # 生成运行记录
    print("\n📝 正在生成本地运行记录...")
    with open("last_run.txt", "w", encoding="utf-8") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"✅ 双机器人签到任务于 {now} 成功执行完毕")
    print("✅ 记录已生成，准备交由 GitHub Actions 自动提交。")

with client:
    client.loop.run_until_complete(main())

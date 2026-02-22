import os, asyncio, sys, datetime
from telethon import TelegramClient
from telethon.sessions import StringSession

# ================= 1. 环境与配置 =================
try:
    api_id = int(os.environ['API_ID'])
    api_hash = os.environ['API_HASH']
    session = os.environ['SESSION_STRING']
    bot1 = os.environ['BOT_USERNAME'] 
except KeyError:
    sys.exit("❌ 缺少环境变量，请检查 Secrets！")

BOTS = [
    # (用户名, 指令, 模式, 附加参数: text等几条/button点哪个坐标)
    (bot1, '/qd', 'text', 1),           
    ('@aisgk1', '/sign', 'text', 2),             
    ('@JiuGuanABot', '/checkin', 'text', 1),     
    ('@NaixiAccountBot', '/start', 'button', (0, 1)) # 坐标 (0, 1) 即右上角
]
# =================================================

client = TelegramClient(StringSession(session), api_id, api_hash)

async def run_text_bot(bot, cmd, wait_msgs):
    """处理纯文字签到"""
    print(f"➡️ [{bot}] 发送: {cmd}")
    msg = await client.send_message(bot, cmd)
    
    for _ in range(8):
        await asyncio.sleep(1)
        msgs = await client.get_messages(bot, limit=wait_msgs)
        if len(msgs) >= wait_msgs and all(m.id > msg.id for m in msgs):
            print(f"✅ 成功: {msgs[0].text[:50].replace(chr(10), ' ')}...")
            return
    print(f"⚠️ {bot} 回复超时。")

async def run_btn_bot(bot, cmd, pos):
    """处理坐标按键签到（兼容弹窗与新消息双重监听）"""
    print(f"➡️ [{bot}] 发送: {cmd}")
    await client.send_message(bot, cmd)
    await asyncio.sleep(4) # 等待面板弹出
    
    msgs = await client.get_messages(bot, limit=1)
    if msgs and msgs[0].buttons:
        row, col = pos
        try:
            btn = msgs[0].buttons[row][col]
            print(f"🔍 点击坐标 ({row}, {col}) 按钮: 【{btn.text}】")
            res = await btn.click()
            
            # 1. 抓取弹窗 (通常代表：今日已签到)
            if res and hasattr(res, 'message') and res.message:
                print(f"📢 弹窗提示: 【{res.message}】")
                
            # 2. 抓取新消息 (通常代表：刚刚签到成功)
            await asyncio.sleep(2)
            new_msgs = await client.get_messages(bot, limit=2)
            for m in new_msgs:
                if not m.out and m.id > msgs[0].id:
                    print(f"📩 新增消息: {m.text[:50].replace(chr(10), ' ')}...")
                    break
        except IndexError:
            print(f"❌ 坐标 ({row}, {col}) 不存在，面板可能已更改。")
    else:
        print(f"❌ 未能获取到按键面板。")

async def main():
    await client.start()
    print("✅ 登录成功，开始批量签到...\n")
    
    for bot, cmd, mode, extra in BOTS:
        if not bot: continue
        if mode == 'text':
            await run_text_bot(bot, cmd, extra)
        elif mode == 'button':
            await run_btn_bot(bot, cmd, extra)
        print("-" * 40)
        await asyncio.sleep(2)

    with open("last_run.txt", "w") as f:
        f.write(f"上次运行: {datetime.datetime.now()}")
    print("✅ 任务结束，打卡记录已生成。")

with client:
    client.loop.run_until_complete(main())

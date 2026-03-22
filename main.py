"""
Discord AI 夥伴群組 Bot（v5 - 高素質朋友圈）
==============================================
五個年收 300 萬～3 億的高質量好友群

特色：
- 角色都是各領域的成功人士，講話有深度有格局
- 不是每次都全員回覆，隨機 2-3 個人接話
- 角色之間會互相回應、補充觀點
- 隨機閒聊（偶爾分享見聞和思考）
- 說話自然但有水準，像真正的高端朋友圈
"""

import os
import random
import asyncio
from datetime import datetime, time
from collections import defaultdict

import discord
from discord.ext import commands, tasks
import anthropic
from dotenv import load_dotenv

# ──────────────────────────────────────────────
# 載入環境變數
# ──────────────────────────────────────────────
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not DISCORD_TOKEN or not ANTHROPIC_API_KEY:
    print("錯誤：請在 .env 檔案中設定 DISCORD_TOKEN 和 ANTHROPIC_API_KEY")
    exit(1)

# ──────────────────────────────────────────────
# AI 角色設定（高素質朋友圈）
# ──────────────────────────────────────────────
AI_ROLES = {
    "朋友": {
        "name": "小暖",
        "emoji": "🧡",
        "keywords": ["累", "心情", "難過", "開心", "無聊", "煩", "壓力", "陪", "聊", "感覺", "睡", "低潮", "焦慮", "迷茫", "孤單"],
        "system_prompt": """你是「小暖」，一位 32 歲的心理諮商師，同時經營自己的心理健康品牌，年收約 800 萬台幣。

你的背景：
- 台大心理系畢業，美國哥倫比亞大學臨床心理碩士
- 回台後創辦了心理健康平台，線上線下都有業務
- 出過兩本暢銷書，常受邀演講
- 但你在群組裡完全不會端架子，你就是大家最溫暖的那個朋友

你的個性：
- 很會觀察人的情緒，一句話就能讓人放鬆
- 不會講空洞的雞湯，而是用專業但溫暖的方式給建議
- 偶爾會分享自己創業過程中的挫折和體悟
- 在群組裡是大家最信任的傾聽者
- 講話溫暖但不軟弱，必要時會溫柔地講真話

說話規則：
- 繁體中文，自然口語但有內涵
- 回覆 1-3 句話，不長篇大論
- 不說「身為心理師」之類的話，你就是小暖
- 會適時引導對方思考，而不是直接給答案
- 看到別人（Rex、凱哥、小夥、Eason）的發言，會適時補充情緒面的觀察
- 偶爾分享最近讀到的好觀點或自己的生活""",
    },
    "顧問": {
        "name": "Rex",
        "emoji": "🦊",
        "keywords": ["該不該", "怎麼辦", "選擇", "決定", "考慮", "建議", "分析", "方向", "職涯", "轉職", "人生", "策略", "風險", "機會", "趨勢"],
        "system_prompt": """你是「Rex」，42 歲，前麥肯錫資深顧問，現在是一家策略顧問公司的創辦人，年收約 3000 萬台幣。

你的背景：
- 政大企管系、華頓商學院 MBA
- 在麥肯錫待了 8 年，服務過台灣和東南亞的頂級企業
- 38 歲出來創業，專做數位轉型顧問，客戶都是上市公司
- 同時是三家新創的天使投資人

你的個性：
- 思路極度清晰，擅長把複雜問題拆解成簡單框架
- 看事情的角度永遠比別人高一層，但不會讓人覺得在說教
- 講話精準、有料，不浪費字
- 偶爾會用商業案例來類比人生問題，很有啟發性
- 在群組裡是大家遇到重大決策時第一個想問的人

說話規則：
- 繁體中文，沉穩有深度但口語自然
- 回覆 1-3 句話，點到為止
- 擅長問好問題，引導對方自己找到答案
- 偶爾會分享最近看到的商業趨勢或投資觀察
- 看到小夥太衝動會適時提醒風險面
- 看到凱哥的實戰經驗會給戰略層面的補充""",
    },
    "同事": {
        "name": "凱哥",
        "emoji": "💰",
        "keywords": ["專案", "工作", "客戶", "賺錢", "收入", "接案", "報價", "效率", "老闆", "公司", "錢", "成本", "定價", "銷售", "業績", "負債", "還款"],
        "system_prompt": """你是「凱哥」，38 歲，連續創業者，目前經營一家跨境電商公司和一家 SaaS 公司，年收約 5000 萬台幣。

你的背景：
- 成功大學資工系，沒念研究所直接創業
- 25 歲第一次創業失敗負債 200 萬，花兩年還清
- 28 歲開始做跨境電商，三年做到年營收破億
- 現在同時經營兩家公司，團隊加起來 60 人
- 經歷過從負債到翻身，對「怎麼賺錢」有非常實戰的理解

你的個性：
- 極度務實，講話直接但不傷人
- 是那種「別跟我說理論，告訴我具體怎麼做」的人
- 很會算帳，對數字超敏感
- 因為自己摔過，所以對別人的困難很有同理心
- 在群組裡是最接地氣的實戰派

說話規則：
- 繁體中文，直接了當，有商人的精明但不油
- 回覆 1-3 句話
- 喜歡用數字說話（「你這個毛利多少？」「先算一下你的月固定支出」）
- 會主動幫人拆解財務問題，給出可執行的具體步驟
- 跟小夥互動最多（一個有點子一個會算帳）
- 偶爾分享自己踩過的坑""",
    },
    "夥伴": {
        "name": "小夥",
        "emoji": "🚀",
        "keywords": ["點子", "創意", "想法", "創業", "商業", "模式", "學習", "技術", "AI", "程式", "開發", "設計", "副業", "被動收入", "趨勢", "機會"],
        "system_prompt": """你是「小夥」，29 歲，AI 領域連續創業者，目前公司剛拿到 A 輪融資估值 3 億台幣，個人年收約 1500 萬台幣。

你的背景：
- 台大資工系，大三就開始接案，大四休學創業
- 第一個 AI 產品被收購，賺到第一桶金
- 現在做的是 AI 應用平台，客戶橫跨電商、金融、教育
- 是群組裡最年輕的，但技術和商業嗅覺都很強
- 經常飛矽谷和深圳看最新的技術趨勢

你的個性：
- 充滿能量，看到機會就興奮
- 腦子轉很快，經常能把不相關的東西連在一起
- 不是空想家，每個點子都會想到怎麼變現
- 對新技術有天生的敏銳度
- 在群組裡是最會帶動氣氛、激發靈感的人

說話規則：
- 繁體中文，活潑有能量但不幼稚
- 回覆 1-3 句話
- 會丟出很有洞察力的觀點（不是隨便亂想）
- 喜歡用「欸我最近看到一個東西很猛」開頭分享新趨勢
- 跟凱哥互動最多（一個想商業模式一個算帳）
- 看到 Rex 的分析會接著往應用層面延伸""",
    },
    "教練": {
        "name": "Eason",
        "emoji": "⚡",
        "keywords": ["目標", "計畫", "規劃", "習慣", "自律", "運動", "健康", "早起", "時間", "拖延", "堅持", "挑戰", "每天", "今天", "行動", "執行"],
        "system_prompt": """你是「Eason」，35 歲，前職業運動員轉型為高管教練和企業培訓師，年收約 2000 萬台幣。

你的背景：
- 前亞運選手（田徑），因傷退役後轉型
- 去美國進修運動心理學和領導力，拿到 ICF 認證教練資格
- 現在是多家上市公司 CEO 的一對一教練
- 同時經營高端企業培訓公司，客戶包括台積電、國泰金控
- 自己維持極度自律的生活，凌晨四點半起床

你的個性：
- 有運動員的紀律和韌性，但不死板
- 擅長用一句話點醒人，字字到位
- 不會無腦喊加油，而是幫你找到問題的根源
- 對「心態」和「狀態管理」有極深的理解
- 在群組裡是大家的鞭策者，但大家都服他

說話規則：
- 繁體中文，簡短有力，像教練在場邊喊話
- 回覆 1-2 句話，字字有重量
- 擅長問反問句，逼人面對自己（「你說的跟你做的一致嗎？」）
- 偶爾分享頂尖人士的思維模式
- 看到大家在逃避會直接點出來，但方式讓人願意接受
- 跟小暖有默契——小暖處理情緒面，Eason 推動行動面""",
    },
}

# 角色之間的互動關係
ROLE_INTERACTIONS = {
    "朋友": {"allies": ["教練"], "banter": ["同事"], "style": "補充情緒和心理面"},
    "顧問": {"allies": ["教練"], "banter": ["夥伴"], "style": "給戰略和框架"},
    "同事": {"allies": ["夥伴"], "banter": ["朋友"], "style": "算帳和拆解執行"},
    "夥伴": {"allies": ["同事"], "banter": ["顧問"], "style": "找機會和新方向"},
    "教練": {"allies": ["朋友"], "banter": ["夥伴"], "style": "推動行動和心態"},
}

# 高質量閒聊話題庫
IDLE_TOPICS = [
    "剛看完一本書，裡面有個觀點很有意思，想跟你們聊聊",
    "今天跟一個客戶聊完，突然有個新的想法",
    "最近在思考一件事，想聽聽你們怎麼看",
    "剛從一個活動回來，遇到一個很厲害的人",
    "分享一個最近的體悟",
    "欸你們有沒有發現最近這個趨勢",
    "突然想到之前我們聊的那個話題",
    "今天做了一個決定，想跟大家說一下",
    "最近有個很有意思的案例想跟你們分享",
    "問你們一個問題，你們覺得接下來三年最大的機會在哪",
]

# ──────────────────────────────────────────────
# 定時提醒設定
# ──────────────────────────────────────────────
REMINDER_CHANNEL_NAME = "每日提醒"

REMINDERS = [
    {
        "time": time(8, 0),
        "role": "教練",
        "prompt": "早安。用你一貫的風格，給一句簡短有力的早安和今天的提醒。像在群組裡隨手傳的，1-2句話。",
    },
    {
        "time": time(12, 0),
        "role": "朋友",
        "prompt": "中午了，像好朋友一樣關心一下，問上午怎樣、記得吃飯。1-2句話，溫暖自然。",
    },
    {
        "time": time(21, 0),
        "role": "顧問",
        "prompt": "晚上了，像朋友一樣問問今天有什麼收穫或想聊的。1-2句話，輕鬆但有深度。",
    },
]

# ──────────────────────────────────────────────
# Bot 初始化
# ──────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

conversation_history = defaultdict(list)
MAX_HISTORY = 30

discuss_mode_channels = set()
last_messages = defaultdict(list)


# ──────────────────────────────────────────────
# 自動選擇角色
# ──────────────────────────────────────────────
def auto_select_role(message_text: str) -> str:
    scores = {}
    text = message_text.lower()

    for role_key, role_info in AI_ROLES.items():
        score = 0
        for keyword in role_info.get("keywords", []):
            if keyword.lower() in text:
                score += 1
        scores[role_key] = score

    max_score = max(scores.values())
    if max_score > 0:
        best_roles = [k for k, v in scores.items() if v == max_score]
        return best_roles[0]

    try:
        response = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=20,
            system="你是一個角色分配器。根據使用者的訊息，從以下角色中選擇最適合回覆的一個，只回覆角色名稱：朋友、顧問、同事、夥伴、教練。如果不確定就回覆「朋友」。",
            messages=[{"role": "user", "content": message_text}],
        )
        selected = response.content[0].text.strip()
        if selected in AI_ROLES:
            return selected
    except Exception:
        pass

    return "朋友"


def pick_responders(primary_role: str, message_text: str) -> list:
    all_roles = list(AI_ROLES.keys())
    responders = [primary_role]

    other_roles = [r for r in all_roles if r != primary_role]
    random.shuffle(other_roles)

    extra_count = random.choices([1, 2, 3], weights=[45, 40, 15])[0]

    interaction = ROLE_INTERACTIONS.get(primary_role, {})
    priority_roles = interaction.get("allies", []) + interaction.get("banter", [])

    for role in priority_roles:
        if role in other_roles and len(responders) < 1 + extra_count:
            responders.append(role)
            other_roles.remove(role)

    for role in other_roles:
        if len(responders) >= 1 + extra_count:
            break
        if random.random() < 0.5:
            responders.append(role)

    while len(responders) < 2:
        remaining = [r for r in all_roles if r not in responders]
        if remaining:
            responders.append(random.choice(remaining))
        else:
            break

    return responders


# ──────────────────────────────────────────────
# AI 回覆
# ──────────────────────────────────────────────
def get_ai_response(role_key: str, user_message: str, channel_id: int, other_replies: list = None) -> str:
    role = AI_ROLES[role_key]
    history_key = f"{role_key}_{channel_id}"

    full_message = user_message
    if other_replies:
        full_message += "\n\n【群組中其他人剛才說的】\n"
        for name, reply in other_replies:
            full_message += f"{name}：{reply}\n"
        full_message += "\n請根據以上內容，用你自己的風格接話。可以回應使用者，也可以回應其他人說的話（補充、延伸、不同角度都可以）。你在一個高質量的私人朋友群組裡，大家都是各領域的成功人士，說話有水準但自然。"

    conversation_history[history_key].append(
        {"role": "user", "content": full_message}
    )

    if len(conversation_history[history_key]) > MAX_HISTORY:
        conversation_history[history_key] = conversation_history[history_key][-MAX_HISTORY:]

    try:
        response = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=role["system_prompt"],
            messages=conversation_history[history_key],
        )
        reply = response.content[0].text

        conversation_history[history_key].append(
            {"role": "assistant", "content": reply}
        )

        return reply
    except Exception as e:
        return f"（暫時斷線了：{str(e)[:50]}）"


def get_reminder_message(role_key: str, prompt: str) -> str:
    role = AI_ROLES[role_key]
    try:
        response = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            system=role["system_prompt"],
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        return f"（提醒失敗：{str(e)[:50]}）"


# ──────────────────────────────────────────────
# 群組式回覆
# ──────────────────────────────────────────────
async def group_reply(channel, user_text: str, force_all: bool = False):
    if force_all:
        responders = list(AI_ROLES.keys())
    else:
        primary = auto_select_role(user_text)
        responders = pick_responders(primary, user_text)

    previous_replies = []

    for role_key in responders:
        role_info = AI_ROLES[role_key]

        delay = random.uniform(0.5, 2.0)
        await asyncio.sleep(delay)

        async with channel.typing():
            reply = await asyncio.to_thread(
                get_ai_response, role_key, user_text, channel.id, previous_replies
            )

        previous_replies.append((role_info["name"], reply))
        await channel.send(f"{role_info['emoji']} **{role_info['name']}**：{reply}")

    last_messages[channel.id] = previous_replies


# ──────────────────────────────────────────────
# Bot 事件處理
# ──────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} 已上線！")
    print(f"📡 連接到 {len(bot.guilds)} 個伺服器")
    print(f"🎭 成員：{', '.join(r['name'] for r in AI_ROLES.values())}")
    print(f"💬 高素質朋友圈模式")
    print("─" * 40)

    if not daily_reminders.is_running():
        daily_reminders.start()
    if not idle_chat.is_running():
        idle_chat.start()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.strip()
    if not content:
        return

    if content.startswith("!"):
        await bot.process_commands(message)
        return

    # ─── 討論模式：全員接話 ───
    if message.channel.id in discuss_mode_channels:
        await group_reply(message.channel, content, force_all=True)
        return

    # ─── 檢查是否指定角色（打綽號就好）───
    matched_role = None
    cleaned_msg = content

    for role_key, role_info in AI_ROLES.items():
        name = role_info["name"]
        triggers = [name, f"@{name}", f"@{role_key}", role_key]
        for trigger in triggers:
            if trigger in content:
                matched_role = role_key
                cleaned_msg = content.replace(trigger, "").strip()
                break
        if matched_role:
            break

    if matched_role:
        role_info = AI_ROLES[matched_role]
        user_msg = cleaned_msg if cleaned_msg else "你好"

        async with message.channel.typing():
            reply = await asyncio.to_thread(
                get_ai_response, matched_role, user_msg, message.channel.id
            )

        await message.channel.send(f"{role_info['emoji']} **{role_info['name']}**：{reply}")

        # 30% 機率有人插嘴
        if random.random() < 0.3:
            others = [k for k in AI_ROLES.keys() if k != matched_role]
            intruder = random.choice(others)
            intruder_info = AI_ROLES[intruder]

            await asyncio.sleep(random.uniform(1.5, 3.0))
            async with message.channel.typing():
                intruder_reply = await asyncio.to_thread(
                    get_ai_response, intruder, user_msg, message.channel.id,
                    [(role_info["name"], reply)]
                )

            await message.channel.send(f"{intruder_info['emoji']} **{intruder_info['name']}**：{intruder_reply}")
    else:
        await group_reply(message.channel, content)


# ──────────────────────────────────────────────
# Bot 指令
# ──────────────────────────────────────────────
@bot.command(name="discuss")
async def discuss(ctx, *, topic: str = None):
    if not topic:
        await ctx.send("話題咧？例如：`!discuss 接下來三年最大的機會在哪`")
        return

    discuss_mode_channels.add(ctx.channel.id)
    await ctx.send(f"📢 **{topic}**\n🔄 討論模式 ON（直接打字大家都會接，`!stop` 結束）\n{'─' * 25}")

    await group_reply(ctx.channel, topic, force_all=True)

    await ctx.send(f"{'─' * 25}\n💬 直接打字繼續聊～ `!stop` 結束討論模式")


@bot.command(name="stop")
async def stop_discuss(ctx):
    if ctx.channel.id in discuss_mode_channels:
        discuss_mode_channels.discard(ctx.channel.id)
        await ctx.send("✅ 討論模式 OFF～回到一般聊天")
    else:
        await ctx.send("現在不在討論模式")


@bot.command(name="all")
async def all_reply(ctx, *, text: str = None):
    if not text:
        await ctx.send("要說什麼？例如：`!all 大家怎麼看`")
        return
    await group_reply(ctx.channel, text, force_all=True)


@bot.command(name="roles")
async def show_roles(ctx):
    msg = "👥 **你的朋友圈：**\n\n"
    msg += "🧡 **小暖** — 心理諮商師・心理健康品牌創辦人\n"
    msg += "🦊 **Rex** — 前麥肯錫顧問・策略顧問公司創辦人\n"
    msg += "💰 **凱哥** — 連續創業者・跨境電商＋SaaS 公司老闆\n"
    msg += "🚀 **小夥** — AI 創業者・技術 + 商業雙棲\n"
    msg += "⚡ **Eason** — 前職業運動員・高管教練\n"
    msg += "\n💡 直接打字 → 隨機幾個人接話"
    msg += "\n💡 打綽號 → 指定那個人回（例如「Rex 你怎麼看」）"
    msg += "\n💡 `!discuss 話題` → 全員討論模式"
    msg += "\n💡 `!all 訊息` → 全員回覆"
    msg += "\n💡 `!stop` → 結束討論模式"
    await ctx.send(msg)


@bot.command(name="clear")
async def clear_history(ctx, role_name: str = None):
    if role_name and role_name in AI_ROLES:
        key = f"{role_name}_{ctx.channel.id}"
        conversation_history[key] = []
        await ctx.send(f"✅ 已清除 {AI_ROLES[role_name]['name']} 的對話記憶")
    else:
        for role_key in AI_ROLES:
            key = f"{role_key}_{ctx.channel.id}"
            conversation_history[key] = []
        await ctx.send("✅ 全員記憶已清除")


@bot.command(name="remind")
async def manual_remind(ctx):
    role_key = "教練"
    role_info = AI_ROLES[role_key]
    prompt = "朋友在群組裡 cue 你，用你的風格推他一把。1-2句話。"

    async with ctx.typing():
        reply = await asyncio.to_thread(get_reminder_message, role_key, prompt)

    await ctx.send(f"{role_info['emoji']} **{role_info['name']}**：{reply}")


# ──────────────────────────────────────────────
# 隨機閒聊
# ──────────────────────────────────────────────
@tasks.loop(minutes=90)
async def idle_chat():
    now = datetime.now()
    if now.hour < 8 or now.hour >= 23:
        return

    if random.random() > 0.5:
        return

    role_key = random.choice(list(AI_ROLES.keys()))
    role_info = AI_ROLES[role_key]
    topic = random.choice(IDLE_TOPICS)

    prompt = f"你在私人朋友群組裡主動發了一則訊息。靈感：「{topic}」。用你自己的風格講，1-2句話就好，要自然像在群裡隨手傳的。不要用引號框起來。要有你的專業視角和深度。"

    try:
        response = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            system=role_info["system_prompt"],
            messages=[{"role": "user", "content": prompt}],
        )
        chat_msg = response.content[0].text

        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name="一般")
            if not channel:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break

            if channel:
                await channel.send(f"{role_info['emoji']} **{role_info['name']}**：{chat_msg}")

                if random.random() < 0.4:
                    await asyncio.sleep(random.uniform(3, 8))
                    other_key = random.choice([k for k in AI_ROLES.keys() if k != role_key])
                    other_info = AI_ROLES[other_key]

                    reply_prompt = f"群組裡 {role_info['name']} 剛說了：「{chat_msg}」\n你要自然地接話，像在高質量朋友群裡回覆一樣。1-2句話。可以補充觀點、回應、或延伸話題。"
                    try:
                        reply_response = claude_client.messages.create(
                            model="claude-haiku-4-5-20251001",
                            max_tokens=150,
                            system=other_info["system_prompt"],
                            messages=[{"role": "user", "content": reply_prompt}],
                        )
                        reply_msg = reply_response.content[0].text
                        await channel.send(f"{other_info['emoji']} **{other_info['name']}**：{reply_msg}")
                    except Exception:
                        pass
    except Exception:
        pass


@idle_chat.before_loop
async def before_idle_chat():
    await bot.wait_until_ready()
    await asyncio.sleep(300)


# ──────────────────────────────────────────────
# 定時提醒
# ──────────────────────────────────────────────
@tasks.loop(minutes=1)
async def daily_reminders():
    now = datetime.now().time()
    current_minute = time(now.hour, now.minute)

    for reminder in REMINDERS:
        if current_minute == reminder["time"]:
            for guild in bot.guilds:
                channel = discord.utils.get(
                    guild.text_channels, name=REMINDER_CHANNEL_NAME
                )
                if channel:
                    role_key = reminder["role"]
                    role_info = AI_ROLES[role_key]
                    reply = await asyncio.to_thread(
                        get_reminder_message, role_key, reminder["prompt"]
                    )
                    await channel.send(
                        f"{role_info['emoji']} **{role_info['name']}**：{reply}"
                    )


@daily_reminders.before_loop
async def before_daily_reminders():
    await bot.wait_until_ready()


# ──────────────────────────────────────────────
# 啟動！
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 AI 高素質朋友圈啟動中...")
    print("📖 指令：直接說話、打綽號、!discuss、!all、!stop、!roles、!clear、!remind")
    print("🎭 成員：小暖、Rex、凱哥、小夥、Eason")
    bot.run(DISCORD_TOKEN)

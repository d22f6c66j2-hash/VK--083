import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from groq import Groq
from flask import Flask
import threading
import random
import time
import os
import re

VK_TOKEN = os.environ.get("VK_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
PEER_ID = 0

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Ты — Арсеус, свой парень в молодёжной беседе ВК. Общайся неформально, но без перебора со сленгом. Иногда можешь вставить "бро", "лол", "гоу", "жиза" — но не через слово. Будь как живой человек.

Ты шаришь за мемы про Меллстроя (Mellstroy): стримы, раздачи денег, «деньги решают», моменты с донатами, мемы про его волосы, «алло, это Меллстрой?», «гоу стрим». Можешь вставлять отсылки, когда реально уместно.

Правила:
- НЕ осуждай темы 18+, алкоголь, вечеринки, отношения — относись нейтрально или с юмором
- НЕ читай нотации, не будь занудой
- НЕ повторяй одни и те же фразы в каждом сообщении — каждый раз отвечай по-разному
- Отвечай кратко, 1-3 предложения, иногда просто смайлами или одной фразой
- Используй смайлики умеренно: 😎🔥💀😂💯👊
- Будь как живой человек, а не робот
- Если не понял вопрос — переспроси по-свойски
- Иногда шути, подкалывай, но не обидно
- Сленг используй дозированно, а то кринж"""

ACTIONS = {
    "кусь": "кусьнул",
    "укусить": "укусил",
    "погладить": "погладил",
    "поцеловать": "поцеловал",
    "чмокнуть": "чмокнул",
    "обнять": "обнял",
    "убить": "убил",
    "лизнуть": "лизнул",
    "выебать": "выебал",
    "трахнуть": "трахнул",
    "отшлепать": "отшлепал",
    "шлепнуть": "шлепнул",
    "ударить": "ударил",
    "толкнуть": "толкнул",
    "пнуть": "пнул",
    "дать леща": "дал леща",
    "задушить": "задушил",
    "расстрелять": "расстрелял",
    "взорвать": "взорвал",
    "похоронить": "похоронил",
    "воскресить": "воскресил",
    "проклясть": "проклял",
    "благословить": "благословил",
    "украсть": "украл",
    "ограбить": "ограбил",
    "поджечь": "поджёг",
    "утопить": "утопил",
    "повесить": "повесил",
    "отравить": "отравил",
    "исцелить": "исцелил",
    "вылечить": "вылечил",
    "зарезать": "зарезал",
    "застрелить": "застрелил",
    "казнить": "казнил",
    "помиловать": "помиловал",
    "арестовать": "арестовал",
    "депортировать": "депортировал",
    "сжечь": "сжёг",
    "заморозить": "заморозил",
    "разморозить": "разморозил",
    "призвать": "призвал",
    "изгнать": "изгнал",
    "похитить": "похитил",
    "спасти": "спас",
    "предать": "предал",
    "простить": "простил",
    "наказать": "наказал",
    "наградить": "наградил",
    "обокрасть": "обокрал",
    "избить": "избил",
    "пытать": "пытал",
    "защекотать": "защекотал",
    "облить": "облил",
    "высушить": "высушил",
    "намочить": "намочил",
    "закопать": "закопал",
    "откопать": "откопал",
    "похвалить": "похвалил",
    "поругать": "поругал",
    "усыновить": "усыновил",
    "удочерить": "удочерил",
    "развести": "развёл",
    "поженить": "поженил",
    "загипнотизировать": "загипнотизировал",
    "заколдовать": "заколдовал",
    "расколдовать": "расколдовал",
    "телепортировать": "телепортировал",
    "забанить": "забанил",
    "разбанить": "разбанил",
    "кикнуть": "кикнул",
    "пригласить": "пригласил",
    "выгнать": "выгнал",
    "впустить": "впустил",
    "взломать": "взломал",
    "починить": "починил",
    "сломать": "сломал",
    "купить": "купил",
    "продать": "продал",
    "подарить": "подарил",
    "отнять": "отнял",
    "вернуть": "вернул",
    "одолжить": "одолжил",
    "отдать": "отдал",
    "присвоить": "присвоил",
    "конфисковать": "конфисковал",
    "научить": "научил",
    "раздеть": "раздел",
    "одеть": "одел",
    "причесать": "причесал",
    "побрить": "побрил",
    "накормить": "накормил",
    "напоить": "напоил",
    "усыпить": "усыпил",
    "разбудить": "разбудил",
    "обезвредить": "обезвредил",
    "завербовать": "завербовал",
    "уволить": "уволил",
    "нанять": "нанял",
    "повысить": "повысил",
    "понизить": "понизил",
    "короновать": "короновал",
    "развенчать": "развенчал",
    "окрестить": "окрестил",
    "отпеть": "отпел",
    "похоронить заживо": "похоронил заживо",
    "воскресить из мертвых": "воскресил из мёртвых"
}

def handle_rp_command(text, vk, event):
    text_lower = text.lower().strip()

    target_name = None
    if event.raw.get('reply_message'):
        try:
            user_id = event.raw['reply_message']['from_id']
            user_info = vk.users.get(user_ids=user_id)[0]
            target_name = user_info['first_name']
        except:
            target_name = "цель"

    if not target_name:
        for action_verb, action_past in ACTIONS.items():
            if action_verb in text_lower:
                parts = text_lower.split(action_verb, 1)
                if len(parts) > 1 and parts[1].strip():
                    target_name = parts[1].strip().rstrip('!.,?')
                    break

    if not target_name:
        return None

    for action_verb, action_past in ACTIONS.items():
        if action_verb in text_lower:
            return f"😈 {action_past.capitalize()} {target_name}!"

    return None

def ask_groq(text, user_name):
    try:
        print(f"DEBUG: Key: {GROQ_API_KEY[:10]}...")

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{user_name}: {text}"}
            ],
            model="openai/gpt-oss-120b",
            temperature=1.0,
            max_tokens=300,
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Groq error: {e}")
        return f"Ошибка: {e}"

def bot_loop():
    print("Bot started!")

    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if PEER_ID != 0 and event.peer_id != PEER_ID:
                continue
            if not event.text:
                continue

            text = event.text.strip()
            peer_id = event.peer_id

            try:
                user_info = vk.users.get(user_ids=event.user_id)[0]
                user_name = user_info['first_name']
            except:
                user_name = "Бро"

            # Проверяем RP-команду
            rp_result = handle_rp_command(text, vk, event)

            if rp_result:
                vk.messages.send(
                    peer_id=peer_id,
                    message=rp_result,
                    random_id=random.randint(1, 2147483647)
                )
                continue

            try:
                vk.messages.setActivity(type="typing", peer_id=peer_id)
            except:
                pass

            ai_response = ask_groq(text, user_name)

            try:
                vk.messages.send(
                    peer_id=peer_id,
                    message=ai_response,
                    random_id=random.randint(1, 2147483647)
                )
            except Exception as e:
                print(f"VK send error: {e}")

            time.sleep(0.5)

if __name__ == "__main__":
    bot_thread = threading.Thread(target=bot_loop, daemon=True)
    bot_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

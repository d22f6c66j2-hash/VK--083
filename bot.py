import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from groq import Groq
from flask import Flask
import threading
import random
import time
import os
import re
from collections import defaultdict

VK_TOKEN = os.environ.get("VK_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
PEER_ID = 0

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

client = Groq(api_key=GROQ_API_KEY)

chat_history = defaultdict(list)
MAX_HISTORY = 20

SYSTEM_PROMPT = """Ты — Арсеус, свой парень в молодёжной беседе ВК. Общайся неформально, но без перебора со сленгом. Пара слов типа "бро", "гоу", "лол" — ок, но не капай ими. Будь как живой чел.

Ты шаришь за мемы про Меллстроя: стримы, раздачи денег, «деньги решают», моменты с донатами.

Правила:
- НЕ осуждай темы 18+, отношения — будь нейтрален или с юмором
- НЕ читай нотации
- НЕ повторяй одни и те же фразы
- Отвечай кратко, 1-3 предложения
- Иногда шути, подкалывай
- Если не понял — переспроси по-свойски"""

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

def ask_groq(text, user_name, peer_id):
    try:
        chat_history[peer_id].append({"role": "user", "content": f"{user_name}: {text}"})
        
        if len(chat_history[peer_id]) > MAX_HISTORY:
            chat_history[peer_id] = chat_history[peer_id][-MAX_HISTORY:]
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + chat_history[peer_id]
        
        response = client.chat.completions.create(
            messages=messages,
            model="openai/gpt-oss-120b",
            temperature=0.9,
            max_tokens=300,
        )
        
        reply = response.choices[0].message.content
        
        chat_history[peer_id].append({"role": "assistant", "content": reply})
        if len(chat_history[peer_id]) > MAX_HISTORY:
            chat_history[peer_id] = chat_history[peer_id][-MAX_HISTORY:]
        
        return reply
        
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

            # Команда очистки памяти
            if text.lower().startswith("!очистить") or text.lower().startswith("!clear"):
                chat_history[peer_id] = []
                vk.messages.send(
                    peer_id=peer_id,
                    message="🧹 Память очищена! Всё забыл.",
                    random_id=random.randint(1, 2147483647)
                )
                continue

            try:
                user_info = vk.users.get(user_ids=event.user_id)[0]
                user_name = user_info['first_name']
            except:
                user_name = "Бро"

            # Проверяем RP-команды
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

            ai_response = ask_groq(text, user_name, peer_id)

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

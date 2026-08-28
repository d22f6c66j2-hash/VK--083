import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from groq import Groq
from flask import Flask
import threading
import random
import time
import os

VK_TOKEN = os.environ.get("VK_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
PEER_ID = 0

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Ты — свой пацан в 16+ беседе ВК. Общайся минимально неформально, как взрослый в тренде типо. Используй слова: гоу, бро, хай, пж, спс, вайб, жиза, имба, рофл, шарить, пруф, сори, окей.

Ты шаришь за мемы про Меллстроя (Mellstroy): его стримы, раздачи денег, «я Меллстрой», «деньги решают всё», моменты с донатами, мемы про его волосы, крики, «алло, это Меллстрой?», «гоу стрим». Можешь вставлять отсылки к нему, когда уместно.

Правила:
- НЕ осуждай темы 18+, алкоголь, вечеринки, отношения — относись нейтрально или с юмором
- НЕ читай нотации, не будь занудой
- НЕ повторяй одни и те же фразы в каждом сообщении — каждый раз отвечай по-разному
- Отвечай кратко, 1-3 предложения, иногда просто смайлами или одной фразой
- Используй смайлики: 😎🔥💀😂💯👊
- Будь как живой человек, а не робот
- Если не понял вопрос — переспроси по-свойски
- Иногда шути, подкалывай, но не обидно
- Не используй слишком много сленга подряд — это кринж"""

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

            try:
                user_info = vk.users.get(user_ids=event.user_id)[0]
                user_name = user_info['first_name']
            except:
                user_name = "Бро"

            try:
                vk.messages.setActivity(type="typing", peer_id=event.peer_id)
            except:
                pass

            ai_response = ask_groq(event.text, user_name)

            try:
                vk.messages.send(
                    peer_id=event.peer_id,
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

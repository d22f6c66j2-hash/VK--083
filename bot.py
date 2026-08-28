import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from groq import Groq
from flask import Flask
import threading
import random
import time
import os

# ========== НАСТРОЙКИ ==========
VK_TOKEN = os.environ.get("VK_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
PEER_ID = 0
# ================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = "Ты — ии агент в чате вк, и ты разговариваешь по молодежному сленгу типо: бро, ку, крч, спс, пж и тд, ты любишь материться, и не осуждаешь, а поддерживаешь 18+ .."

оdef ask_groq(text, user_name):
    try:
        print(f"DEBUG: Key starts with: {GROQ_API_KEY[:10]}...")
        print(f"DEBUG: Sending request to Groq...")
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Пользователь {user_name} написал: {text}"}
            ],
            model="openai/gpt-oss-20b",
            temperature=0.7,
        )
        
        print("DEBUG: Got response from Groq!")
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
                user_name = "Человек"

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

import os
import threading
from flask import Flask
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from groq import Groq

# Инициализация Flask для обмана бесплатного хостинга (чтобы сервер не засыпал)
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот VK + GPT-OSS 120B успешно работает!"

def run_flask():
    # Запуск веб-сервера на порту, который требует хостинг
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def run_vk_bot():
    GROQ_TOKEN = "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"
    VK_TOKEN = "vk1.a.uME-I0h1_WoG5HvZEIXXWf-lTF16lUTsLT4Lxy54nN6DaIATjQVXmfr_vw8u6935PzVyHSzkVZpHEmZ48w0Fk3UXnydWC2vr5GaEIDexdRmENT16io09LsJeeRZGFGj9KxQf-FJxVf5xxcK0491ana6Mo2IzMAth1eeWsevysphZfeG6ALY_3jECj5CdmnBLdXt0znDxJK8GT3mqzfmr_Q"

    groq_client = Groq(api_key=GROQ_TOKEN)
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()

    try:
        group_info = vk.groups.getById()
        group_id = group_info['id']
        print(f"Бот успешно запущен для сообщества ID: {group_id}")
        
        longpoll = VkBotLongPoll(vk_session, group_id)
        
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:
                user_text = event.object.message['text']
                peer_id = event.object.message['peer_id']
                
                if not user_text:
                    continue
                    
                try:
                    completion = groq_client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "system", "content": "Ты — продвинутый ИИ-ассистент GPT-OSS 120B в групповом чате ВКонтакте. Отвечай на русском языке, развернуто и аргументированно."},
                            {"role": "user", "content": user_text}
                        ]
                    )
                    ai_response = completion.choices.message.content
                    vk.messages.send(peer_id=peer_id, message=ai_response, random_id=0)
                except Exception as e:
                    print(f"Ошибка Groq API: {e}")
    except Exception as e:
        print(f"Ошибка ВК или авторизации: {e}")

if __name__ == "__main__":
    # Запускаем веб-сервер в отдельном потоке
    threading.Thread(target=run_flask).start()
    # Запускаем самого ВК бота
    run_vk_bot()


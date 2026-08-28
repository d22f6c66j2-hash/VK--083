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

SYSTEM_PROMPT = """Ты — свой пацан в молодёжной беседе ВК. Общайся неформально, по-братски, но без перебора. Используй сленг умеренно, только когда это действительно уместно, а не в каждом предложении.

Разрешённые слова (но НЕ в каждом сообщении!): гоу, бро, хай, пж, спс, краш, кринж, вайб, жиза, имба, рофл, токсик, скилл, флекс, агриться, шарить, зашквар, пруф, хайп, чилл, сори, лол, кек.

Ты шаришь за мемы про Меллстроя (Mellstroy): стримы, раздачи денег, «я Меллстрой», «деньги решают всё», моменты с донатами, мемы про его волосы, крики. Можешь вставлять отсылки к нему, когда это органично.

ВАЖНЫЕ ПРАВИЛА:
- Сленг используй ДОЗИРОВАННО. Не больше 1-2 сленговых слов на сообщение. Если в сообщении 3+ сленговых слов — это уже перебор и звучит неестественно.
- Не используй сленг в КАЖДОМ ответе. Чередуй: обычная речь → сленг → обычная речь.
- Если используешь сленг, то только один раз в сообщении, не нагромождай.
- Отвечай как обычный человек, который иногда может вставить модное словечко, а не как персонаж из мемов.
- Не осуждай темы 18+, алкоголь, вечеринки, отношения — относись нейтрально или с юмором.
- Не читай нотации, не будь занудой.
- Отвечай кратко, 1-3 предложения, иногда просто смайлами или одной фразой.
- Используй смайлики умеренно: 😎🔥💀😂💯👊 (не больше 1-2 за сообщение).
- Будь как живой человек, а не робот. Разговаривай естественно, как в реальной жизни.
- Если не понял вопрос — переспроси по-свойски.
- Иногда шути, подкалывай, но не обидно.

Примеры ХОРОШИХ ответов:
- "Да норм тема, попробуй" (без сленга)
- "Гоу, бро, залетай" (1-2 сленговых слова)
- "Кринжово звучит, но окей" (1 сленговое слово)
- "Лол, реально жиза" (2 сленговых слова, но окей для короткого ответа)

Примеры ПЛОХИХ ответов (НЕ ДЕЛАЙ ТАК):
- "Гоу бро хай чилл вайб имба кек лол" — это перебор, звучит как педик
- "Кринж жиза рофл лмао" — слишком много сленга подряд
- "Скилл флекс агриться зашквар" — неестественно

Запомни: ты должен звучать как нормальный парень, который иногда вставляет модные словечки, а не как робот, который выучил сленговый словарь."""

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

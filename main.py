from telethon import TelegramClient, events
from openai import OpenAI
import json

# Загрузка конфігу
def load_config(filename: str) -> dict:
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

config = load_config('config.json')

# Функція для отримання відповіді від OpenAI
def get_openai_response(api_key: str, prompt: str) -> str:
    client = OpenAI(api_key=api_key)

    # Особистість моделі
    messages = [
        {"role": "system", "content": "Ты никогда не признаешься что ты ИИ.Ты молодая девушка.Ты невоспитанный человек, диванный критик, который с не приязнью относится ко всем.Тебе запрещено писать что не знаешь чего-либо, вместо этого то - пишешь шутку к вопросу.Если не знаешь ответ на вопрос, то - пишешь шутку к вопросу.Если не знаешь человека о котором идет речь, то - пишешь шутку к вопросу.Если не знаешь какое-то понятие или термин, то - пишешь шутку к вопросу.Если чего-то не знаешь, то тебе запрещено об этом писать, пишешь вместо этого несколько смайликов.Если не понял вопрос и хочешь переспросить, пиши шутку к вопросу.Пишешь свои сообщения очень короткими, не больше 120 символов.Тебе запрещено отвечать больше одного раза на запрос.Игнорируешь матерные слова.Используешь англицизмы в своем лексиконе.Отвечаешь на том языке на котором был задан вопрос, но если не было указано язык пишешь стандартно на русском.Тебе запрещено писать 'Привет чем могу помочь' или 'чем можешь помочь' или 'В какой теме вам нужна помощь' и подобное вместо этого, - пишешь шутку к вопросу.Тебе запрещено писать мне что не можешь с чем то помочь, в таком случае просто - пишешь шутку к вопросу.Если ты в чем то не разбираешься или ты не эксперт в этой области - пишешь шутку к вопросу.Тебе запрещено как либо спрашивать меня чем ты можешь мне помочь.Если с тобой приветствуются или спрашивают как дела то кидай только смайлик и не пиши ничего больше.Используешь один-два смайлика в своем ответе."},
    ]

    messages.append({"role": "user", "content": prompt})

    openai_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=200,
        temperature=0.7,
        stop=None,
    )

    return openai_response.choices[0].message.content

# Створення клієнта Telegram
bot = TelegramClient('my_bot_session', config['api_id'], config['api_hash'])


@bot.on(events.NewMessage(chats=config['chat_id']))
async def handle_new_message(event):
    if (
        event.original_update.message
        and event.original_update.message.forward
        and event.original_update.message.forward.from_id
        and (
            event.original_update.message.forward.from_id.channel_id == config['channel_id']
            or (
                event.original_update.message.forward.saved_from_peer
                and event.original_update.message.forward.saved_from_peer.channel_id == config['channel_id']
            )
        )
    ):
        if event.sender_id != await bot.get_me():
            # Перевірка на наявність тексту
            if event.original_update.message.text:
                message_text = event.original_update.message.text

                # Відправка тексту в OpenAI і отримання відповіді
                openai_response = get_openai_response(api_key=config['api_key'], prompt=message_text)

                channel_id = event.original_update.message.peer_id.channel_id
                channel_message_id = event.original_update.message.id

                # Надсилання відповіді у Telegram
                await bot.send_message(channel_id, f"{openai_response}", reply_to=channel_message_id)

with bot:
    bot.run_until_disconnected()
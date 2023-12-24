from telethon import TelegramClient, events
import json
import random

# Конфігурація
def load_config(filename: str) -> dict:
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

config = load_config('config.json')

def load_static_messages(filename: str) -> list:
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

static_messages = load_static_messages('config_for_spam_with_rand_mess.json')

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
            if event.original_update.message.text or event.original_update.message.media:
                # Вибір випадкового повідомлення з набору
                random_message = random.choice(static_messages)

                channel_id = event.original_update.message.peer_id.channel_id
                channel_message_id = event.original_update.message.id

                # Надсилання випадкового повідомлення
                await bot.send_message(channel_id, random_message, reply_to=channel_message_id)

with bot:
    bot.run_until_disconnected()

''' All function for telegram api '''
from telethon.sync import TelegramClient
from telethon.tl.types import PeerUser
from telethon.tl.functions.messages import GetHistoryRequest
''' Utility function date, json format'''
from datetime import datetime
import json

with open("setting.json", "r", encoding = "utf-8") as read_file:
    json_data = json.loads(read_file.read())

api_id   = json_data['user']['api_id']
api_hash = json_data['user']['api_hash']
username = json_data['user']['username']

client = TelegramClient(username, api_id, api_hash)
client.start()

async def write_log(data_file, data) -> None:
    data_file.write(data)

async def console_log(data) -> None:
    print(data)

async def between(message, _from, to) -> bool:
    date = str(message.date).split()[0].split('-')
    date[0] = date[0][:2]

    return (
        datetime.strptime(to, '%y-%m-%d') <= \
        datetime.strptime('-'.join(date), '%y-%m-%d') <= \
        datetime.strptime(_from, '%y-%m-%d')
    )

async def delete() -> None:
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        print(f'[{dialogs.index(dialog)}] {dialog.name}')
    
    select = int(input(f'Select dialog: '))
    print('Select date range, from - to. For example: from 20-09-16 to 20-09-17')
    _from = input('From: ').replace(' ', ''); to = input('To: ').replace(' ', '')

    messages = await client.get_messages(dialogs[select], limit = None)

    messages = [
        message for message in messages 
        if await between(message, to, _from)
    ]

    lenth_of_message = len(messages)
    messages_cout = 1
    date_now = str(datetime.now()).split()[0]
    file_name = f'deleted-messages-{date_now}-{dialogs[select].id}.txt'

    with open(file_name, 'w', encoding = 'utf') as logfile:
        for message in messages:
            message_text = message.message.replace('\n', ' ') \
                if not message.media else '<image>'
            
            author = await client.get_entity(PeerUser(message.from_id))
            author = author.username if author.username \
                else author.first_name if author.first_name \
                    else author.id

            await client.delete_messages(dialogs[select], message.id)
            await write_log(logfile, f'{str(message.date)} [{author}] - {message_text}\n')

            message_date = str(message.date).split()[0]
            process = int(100 * messages_cout / lenth_of_message)
            logged_message = f'Deleted id {message.id} start: {_from}, ' +\
                f'current: {message_date}, end: {to}. Total: {messages_cout} ({process}%)'
            
            await console_log(logged_message)

            messages_cout += 1

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(delete())

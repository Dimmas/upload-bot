api_id = 19987235
api_hash = "1d2a60278afdedd15072296116e39ce4"
token = "1747786691:AAFRNzCMwTHaodSCJBNiXjqJzBi42gTR3I4"

import telegram

# Provide API key and the name of the group or channel.
api_key = '7170610528:AAG1Pkc8UORSphj8FF0JduIGx-f8SYtp1WQ'
group_name = '@CorvusAlbusBot'

# Connect to Telegram API using the bot API key.
bot = telegram.Telegram(token=api_key)
# Get the group or channel ID
group_id = bot.get_chat(group_name).id

# Get the messages history of the group or channel
messages = bot.get_chat_history(chat_id=group_id)

# Save the messages to a text file
with open(group_name + '.txt', "w", encoding='utf-8') as f:
    for message in messages:
        f.write(str(message.text.encode('utf-8')) + '\n')

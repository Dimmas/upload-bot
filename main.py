import telebot
from telebot import apihelper

apihelper.proxy = {'http': 'http://qaw7Mx:4bNrcu@194.67.213.23:9558'}

bot = telebot.TeleBot('1700151459:AAF1ZXyRfsl8eSabSMRgcYCVlMCP4RVxRFQ')


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        print('***', file_info.file_path)
        downloaded_file = bot.download_file(file_info.file_path)

        with open(f"telegram_files/{message.document.file_name}", 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, "Файл успешно загружен на сервер.")
    except Exception:
        bot.reply_to(message, "Произошла ошибка при загрузке файла.")


@bot.message_handler(commands=['upfiles'])
def download_chat_files(message):
    pass

bot.polling()


import telebot
import config
import time
import os
import pickle

try:
    data = pickle.load(open(config.way, "rb"))
except FileNotFoundError:
    pickle.dump({}, open(config.way, "wb"))
    data = {}

if not os.path.exists('photos'):
    os.mkdir('photos')

bots = []
bot = telebot.TeleBot(config.TOKENS[0])

for x in range(0, len(config.TOKENS)):
    bots.append(telebot.TeleBot(config.TOKENS[x]))


def flooding(message_chat_id):
    global data
    data = pickle.load(open(config.way, "rb"))
    if data[message_chat_id]['i'] == len(config.TOKENS):
        data[message_chat_id]['i'] = 0
    if data[message_chat_id]['type'] == 'text':
        bots[data[message_chat_id]['i']].send_message(message_chat_id, data[message_chat_id]['text'])
        time.sleep(2.5 / len(config.TOKENS))
    elif data[message_chat_id]['type'] == 'sticker':
        bots[data[message_chat_id]['i']].send_sticker(message_chat_id, data[message_chat_id]['sticker'])
        time.sleep(2.5 / len(config.TOKENS))
    elif data[message_chat_id]['type'] == 'photo':
        bots[data[message_chat_id]['i']].send_photo(message_chat_id,
                                                    photo=open('photos/'+str(message_chat_id)+'/image.jpg', 'rb'))
        time.sleep(2.5 / len(config.TOKENS))
    data[message_chat_id]['i'] = data[message_chat_id]['i'] + 1
    pickle.dump(data, open(config.way, "wb"))


def begin(message):
    global data
    data[message.chat.id] = {'flood': False, 'type': None, 'text': None, 'sticker': None, 'photo': None,
                             'expecting_text': False, 'i': 0}
    pickle.dump(data, open(config.way, "wb"))
    try:
        os.mkdir('photos/'+str(message.chat.id))
    except OSError:
        pass


@bot.message_handler(commands=['start'])
def answer(message):
    if not os.path.exists('photos/'+str(message.chat.id)):
        begin(message)
    global data
    data = pickle.load(open(config.way, "rb"))
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if data[message.chat.id]['type']:
        data[message.chat.id]['flood'] = True
        pickle.dump(data, open(config.way, "wb"))
        bot.send_message(message.chat.id, 'started')
        while data[message.chat.id]['flood']:
            flooding(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'First, enter the message text')


@bot.message_handler(commands=['stop'])
def answer(message):
    if not os.path.exists('photos/'+str(message.chat.id)):
        begin(message)
    global data
    data = pickle.load(open(config.way, "rb"))
    data[message.chat.id]['flood'] = False
    data[message.chat.id]['i'] = 0
    pickle.dump(data, open(config.way, "wb"))
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.send_message(message.chat.id, 'stopped')
    while data[message.chat.id]['flood']:
        flooding(message.chat.id)


@bot.message_handler(commands=['text'])
def answer(message):
    if not os.path.exists('photos/'+str(message.chat.id)):
        begin(message)
    global data
    data = pickle.load(open(config.way, "rb"))
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.send_message(message.chat.id, 'Enter the text or the sticker or the photo:')
    data[message.chat.id]['expecting_text'] = True
    pickle.dump(data, open(config.way, "wb"))


@bot.message_handler(content_types=['text', 'sticker', 'photo'])
def answer(message):
    global data
    data = pickle.load(open(config.way, "rb"))
    if data[message.chat.id]['expecting_text']:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        data[message.chat.id]['expecting_text'] = False
        if message.text:
            data[message.chat.id]['type'] = 'text'
            data[message.chat.id]['text'] = message.text
            bot.send_message(message.chat.id, 'Now text is ' + data[message.chat.id]['text'])
        elif message.sticker:
            data[message.chat.id]['type'] = 'sticker'
            data[message.chat.id]['sticker'] = message.sticker.file_id
            bot.send_message(message.chat.id, 'Now sticker is ')
            bot.send_sticker(message.chat.id, message.sticker.file_id)
        elif message.photo:
            if os.path.exists(str(message.chat.id)+'/image.jpg'):
                os.remove(str(message.chat.id)+'/image.jpg')
            data[message.chat.id]['type'] = 'photo'
            bot.send_message(message.chat.id, 'Now photo is ')
            bot.send_photo(message.chat.id, message.photo[0].file_id)
            fileid = message.photo[-1].file_id
            file_info = bot.get_file(fileid)
            downloaded_file = bot.download_file(file_info.file_path)
            with open("photos/%s/image.jpg" % message.chat.id, 'wb') as new_file:
                new_file.write(downloaded_file)
        pickle.dump(data, open(config.way, "wb"))


while 1:
    bot.polling(none_stop=True)

import os
import subprocess
from telebot import TeleBot, types
import redis

token = ""
bot = TeleBot(token)
admins = [
    205746695
] # Admins
db = redis.Redis("localhost", decode_responses=True)
''


@bot.message_handler(commands=['start', 'help'])
def start(msg):
    text = '''
سلام {} خوش اومدی...
کافیه عکس مورد نظرتو برای من بفرستی تا اونو به حالات مختلف (پیر و جوان و مرد و زن و...) رو تبدیل کنم
'''.format(msg.from_user.first_name)
    bot.send_chat_action(msg.chat.id, "typing")
    bot.send_message(msg.chat.id, text)
    db.sadd("faceapp:users", msg.from_user.id)


@bot.message_handler(content_types=['photo'])
def send_photo(msg):
    try:
        file_info = bot.get_file(msg.photo[len(msg.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("pics/pic:{}.jpg".format(str(msg.from_user.id)), 'wb') as fl:
            fl.write(downloaded_file)
        key = types.InlineKeyboardMarkup()
        key.add(types.InlineKeyboardButton("جذاب", callback_data="hot"),
                types.InlineKeyboardButton("خندان", callback_data="smile_2"),
                types.InlineKeyboardButton("مرد", callback_data="male"))
        key.add(types.InlineKeyboardButton("زن", callback_data="female"),
                types.InlineKeyboardButton("کودک", callback_data="young"),
                types.InlineKeyboardButton("پیر", callback_data="old"))
        text = 'عکس شما ثبت شد...\nلطفا یک مورد را انتخاب کنید.'
        bot.send_message(msg.chat.id, text, reply_markup=key)
    except:
        bot.send_message(msg.chat.id, "مشکلی پیش آمد...\nعکس را دوباره ارسال کنید")


@bot.callback_query_handler(func=lambda call: call.data)
def send_edited_photo(call):
    try:
        tp = call.data
        bot.send_chat_action(call.message.chat.id, "upload_photo")
        subprocess.call(["faceapp", tp, "pics/pic:{}.jpg".format(str(call.from_user.id)), "out.jpg"],
                        stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        fl = open("out.jpg", "rb")
        bot.send_photo(call.message.chat.id, fl)
        fl.close()
    except:
        bot.send_message(call.message.chat.id, "مشکلی پیش آمد...\nعکس را دوباره ارسال کنید")


@bot.message_handler(func=lambda msg: msg.from_user.id in admins)
def admins_handler(msg):
    if msg.text:
        if msg.text == '/stats':
            users = db.scard("faceapp:users")
            bot.send_message(msg.chat.id, "USERS: {}".format(str(users)))
        if msg.text.startswith('/bc '):
            users = db.smembers("faceapp:users")
            text = msg.text.replace("/bc ", "")
            for i in users:
                try:
                    bot.send_message(i, text, parse_mode="HTML")
                except:
                    pass


bot.polling()

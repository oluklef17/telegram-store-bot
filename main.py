import telebot
from telebot.types import Message
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from datetime import datetime, timedelta
import flask
from flask import Flask, render_template, request
from threading import Thread

app = Flask(__name__)

bot_token = ''

conn = sqlite3.connect("telebotUsers.db")

curs = conn.cursor()

curs.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    exp_date TEXT
)
""")


def add_user(connect, cursor, name, exp_date):
    cursor.execute("""
SELECT COUNT(*) FROM users
WHERE name = ?
""", (name,))
    result = cursor.fetchone()
    if result[0] > 0:
        print("User already exists.")
    else:
        cursor.execute("""
    INSERT INTO users (name, exp_date)
    VALUES (?, ?)
    """, (name, exp_date))
        connect.commit()




bot = telebot.TeleBot(bot_token, threaded=False)
bot.remove_webhook()
#bot.set_webhook(url='https://jarvistrade.pythonanywhere.com')
bot.set_webhook(url='https://127.0.0.1')

app = Flask(__name__)

def create_keys(id, num_of_btns, btn_texts, btn_cmds, title="Please select"):
    try:
        buttons = list()
        for i in range(num_of_btns):
            buttons.append(InlineKeyboardButton(text=btn_texts[i], callback_data=btn_cmds[i]))
        bot.send_message(id, title, reply_markup=InlineKeyboardMarkup(
            [
            buttons
            ]
        ))
    except Exception as e:
         print('Failed to create keys. Error => ',str(e))

@app.route('/', methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@bot.message_handler()
def send_welcome(message):
    try:
        user_msg = message.text
        if user_msg == 'start' or user_msg == '/start':
            if message.chat.username == None:
                bot.send_message(message.chat.id, 'Please create a telegram username, then restart chat by sending the following command: /start')
                return
            bot.send_message(message.chat.id, "Hello, %s!.\n\nWelcome to Jarvistrade, your no. 1 hub of trading technologies. Automation is powering the next generation of successful traders. At Jarvistrade, we offer you the very best of awesome trading tools to trade like the very best in the game.\n\n From trading indicators, scripts to expert advisors, we give you the very best tools that successful traders use to stay clear of the losing herd."%message.from_user.first_name,
                            reply_markup=InlineKeyboardMarkup(
                                [
                                [
                                    InlineKeyboardButton(text="Get free EAs and indicators", callback_data="Market clicked")
                                ],
                                [
                                    InlineKeyboardButton(text="Request your custom EAs/Indicators", callback_data="Order clicked")
                                ],
                                [
                                    InlineKeyboardButton(text="Questions & Comments", callback_data="FAQ clicked")
                                ],
                                [
                                    InlineKeyboardButton(text="Social Media", callback_data="SM clicked")
                                ]
                                ]
                            ))
        else:
            bot.send_message(1380098782,'@'+str(message.chat.username)+' sent: '+str(message.text))
    except Exception as e:
        print('Failed to send messages. Error => ',str(e))

@bot.callback_query_handler(func=lambda m: True)
def callback_query_handle(callback_query):
    try:
        connect = sqlite3.connect("telebotUsers.db")
        cursor = connect.cursor()
        name = callback_query.from_user.username
        next_week = str(datetime.now() + timedelta(weeks=1))
        bot.answer_callback_query(callback_query.id)
        if callback_query.data=="SM clicked":
            bot.send_message(callback_query.from_user.id, "You can find us on\nTwitter: https://twitter.com/jarvistrade_ai?t=zy2PkV1ItbQhulxWYcEeHg&s=35\n\nWhatsApp: https://wa.me/message/UTIZGS6QFBOOA1")
        #MARKET
        elif callback_query.data=="Market clicked":
            texts = ['Telegram to MT4 copier (FREE)']
            cmds  = ['Copier clicked']
            create_keys(callback_query.from_user.id,1,texts,cmds, 'Please select one of our products')
        #COPIER
        elif callback_query.data=="Copier clicked":
            add_user(connect, cursor, name, next_week)
            texts = ['Try our telegram copier for free for 7 days']
            cmds  = ['Copier download clicked']
            create_keys(callback_query.from_user.id,1,texts,cmds, 'Our telegram copier can copy all signal formats from any channel/group of your choosing. Try it out for free.')
        #DOWNLOAD COPIER
        elif callback_query.data=="Copier download clicked":
            bot.send_document(callback_query.from_user.id, open(r'jt_telegram_copier.zip', 'rb'))
            bot.send_message(1380098782, '@'+str(callback_query.from_user.username)+' just downloaded telegram copier.')
        #FILTER
        elif callback_query.data=="Filter clicked":
            add_user(connect, cursor, name, next_week)
            texts = ['Try our news filter for free for 7 days']
            cmds  = ['Filter download clicked']
            create_keys(callback_query.from_user.id,1,texts,cmds, 'Our news filter helps protect your account from high impact news.')
        #DOWNLOAD FILTER
        elif callback_query.data=="Filter download clicked":
            bot.send_document(callback_query.from_user.id, open(r'mt4totg.ex4', 'rb'))
            bot.send_message(1380098782, '@'+str(callback_query.from_user.username)+' just downloaded news filter.')

        elif callback_query.data=="Order clicked":
            bot.send_message(callback_query.from_user.id, "Please describe the EA/Indicator you would like us to create in details.")
        elif callback_query.data=="FAQ clicked":
            bot.send_message(callback_query.from_user.id, "Please send us your question/comment.")
    except Exception as e:
        print('Callback query failed. Error => ', str(e))


if __name__ == '__main__':
 app.run(host='0.0.0.0', port=80, debug=False)
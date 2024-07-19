import os
from random import randint
import wikipedia
import requests
import telebot
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv
from g4f.client import Client
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from generate_img_with_sber import gen_img
from googletrans import Translator
trans = Translator()
session = {}
load_dotenv(find_dotenv())
token = os.getenv('token')

bot = telebot.TeleBot(token, parse_mode='HTML')

wikipedia.set_lang('ru')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chatID = message.from_user.id
    session[chatID] = {'bot_message':None}
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('секретная функция')
    button2 = KeyboardButton('гифка')
    button3 = KeyboardButton('сгенерировать картинку')
    btn4 = KeyboardButton('википедия')
    btn5 = KeyboardButton('погода')
    btn6 = KeyboardButton('словарь')
    btn7 = KeyboardButton('чат gpt')
    markup.row(btn7, btn6)
    markup.row(btn4, btn5)
    markup.row(button3)
    markup.row(button1)
    bot.send_message(chatID,'привет 👋👋👋 я - бот информатор, я могу помочь найти информацию для 🫵вас🫵. Отправляйте запросы кратко, иначе будут ошибки')
    bot.send_message(chatID, '👇👇👇выберите нужную функцию👇👇👇', reply_markup=markup)

@bot.message_handler(func=lambda callback: True)
def handle_callback(message):
    chatID = message.from_user.id
    button_call = message.text
    if button_call == 'секретная функция':
        bot.send_photo(chatID, open('кот.png', 'rb'))
    elif button_call == 'сгенерировать картинку':
        gen_image(message)
    elif button_call == 'википедия':
        wiki(message)
    elif button_call == 'погода':
        weather(message)
    elif button_call == 'словарь':
        word(message)
    elif button_call == 'чат gpt':
        gpt1(message)
    elif button_call == 'Пермь':
        weatherPerm(chatID)
    elif button_call == 'Москва':
        weatherMoskva(chatID)
    elif button_call == 'отправить геопозицию':
        weather1(message)
    else:
        bot.send_message(chatID, 'кнопка в разработке')

def wiki(message):
    bot.send_message(message.chat.id, 'про что хотите найти информацию?')
    bot.register_next_step_handler(message, wiki2)
def wiki2(message):
    wiki_page = wikipedia.page(message.text)
    try:
        print(wiki_page.html, wiki_page.summary)
        bot.send_message(message.chat.id, wiki_page.summary)
    except:
        bot.send_message(message.chat.id, f'извините текст слишком большой, https://ru.wikipedia.org/wiki/{message.text}')

@bot.message_handler(commands=['gen_img'])
def gen_image(message):
    bot.send_message(message.chat.id, 'что хотите сгенерировать?')
    bot.register_next_step_handler(message, gen_img2)
def gen_img2(message):
    try:
        content = gen_img(message.text, 'C12C1BD6B4AB2A8DA8F62ED242410B4D', '910D77FDD2A8F96AAA4D48E6555A6C54')
        bot.send_photo(message.chat.id, content)
    except:
        bot.send_message(message.chat.id, 'не понял')


@bot.message_handler(commands=['gpt'])
def gpt1(message):
    chatID = message.from_user.id
    bot.send_message(chatID,'введите промпт')
    bot.register_next_step_handler(message, gpt2)
def gpt2(message):
    bot.send_message(message.from_user.id, trans.translate(text=gpt(message.text),scr='auto',dest='ru').text)
def gpt(query):
    client = Client()
    try:
        response = client.chat.completions.create(
            model = 'gpt-3.5-turbo',

            messages=[{'role':'user','content': query}]
        )
        return response.choices[0].message.content
    except:
        bot.send_message(query.chat.id, 'не понял')




@bot.message_handler(commands=['weather'])
def weather(message):
    button_call = message.text
    chatID = message.from_user.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    key = KeyboardButton('отправить геопозицию', request_location=True)
    btn1 = KeyboardButton('Пермь')
    btn2 = KeyboardButton('Москва')
    markup.row(key)
    markup.row(btn1, btn2)
    bot.send_message(chatID, 'где выхотите узнать текущую погоду?', reply_markup=markup)

@bot.message_handler(func=lambda callback: True)
def handle_callback(message):
    chatID = message.from_user.id
    button_call = message.text
    if button_call == 'Пермь':
        weatherPerm(chatID)
    elif button_call == 'Москва':
        weatherMoskva(chatID)
    elif button_call == 'отправить геопозицию':
        weather1(message)

def weather1(message):
    chatID = message.from_user.id
    lat = 0
    lon = 0
    current_weather = get_temp(lat, lon)
    bot.send_message(chatID, f'Текущая температура: {current_weather} градусов цельсия')
def weatherPerm(chatID):
    lat = 56
    lon = 56
    current_weather = get_temp(lat, lon)
    bot.send_message(chatID, f'Текущая температура: {current_weather} градусов цельсия')
def weatherMoskva(chatID):

    lat = 55
    lon = 37
    current_weather = get_temp(lat, lon)
    bot.send_message(chatID, f'Текущая температура: {current_weather} градусов цельсия')

def get_temp(lat, lon):
    url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}.52&longitude={lon}.41&current=temperature_2m,cloud_cover,wind_speed_10m&hourly=temperature_2m'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        current_temp = str(data['current']['temperature_2m'])
        return current_temp
    else:
        print(f'ошибка: {response.status_code}')
        return 'не удалось определить погоду'



@bot.message_handler(commands=['word'])
def word(message):
    bot.send_message(message.chat.id, 'введите слово')
    bot.register_next_step_handler(message, get_info_word)

def get_info_word(message):
    url = f'https://ru.wiktionary.org/wiki/{message.text.lower()}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    answer = soup.find('ol')
    bot.send_message(message.chat.id, f'{message.text} - {answer.text}')


@bot.message_handler(commands=['photo'])
def photo(message):
    chat_ID = message.from_user.id
    rand = randint(1,6)
    list = [{'1':'https://s0.rbk.ru/v6_top_pics/media/img/5/31/756806793338315.png','2':'https://s0.rbk.ru/v6_top_pics/media/img/5/31/756806793338315.png','3':'data:image/jpeg;base64,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','4':'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSZ0d3iXC0HZ_58_rrLix37HHDeP6SNA54NDQ&s','5':'https://habrastorage.org/getpro/habr/upload_files/15d/0eb/491/15d0eb491d6909df70ee6d9190346d82.png'}]
    bot.send_photo(chat_ID, list[rand])

@bot.message_handler(commands=['gif'])
def gif(message):
    chat_id = message.from_user.id
    bot.send_photo(chat_id, open('nasa-black-hole-visualization-1.gif', 'rb'))



bot.infinity_polling()
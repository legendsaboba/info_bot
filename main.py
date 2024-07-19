import os
import requests
import telebot
from dotenv import load_dotenv, find_dotenv
from g4f.client import Client
from generate_img_with_sber import gen_img
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import wikipedia
from bs4 import BeautifulSoup
from googletrans import Translator
trans = Translator()
load_dotenv(find_dotenv())
token = os.getenv('token')
bot = telebot.TeleBot(token, parse_mode='HTML')
wikipedia.set_lang('ru')
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chatID = message.from_user.id
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
bot.infinity_polling()
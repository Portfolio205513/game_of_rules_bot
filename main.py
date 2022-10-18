import telebot
from telebot import types
import random as rnd
from time import sleep
import json
import urllib3.exceptions
import requests.exceptions
import socket

with open("tokens.json", "r") as file:
    token = json.load(file)["game_of_rules"]
file.close()

with open("words.json", "r") as file:
    words = json.load(file)
file.close()

GameOfRules = telebot.TeleBot(token)
users = [576109089, 1055941724]
current = {'position': 0, 'answer': False, 'questions': [], 'write_ans': 0}


def number_of_syllable(word):
    vowels = 'аеёиоуэыюяaoye'
    return sum(letter in vowels for letter in word.lower())


def give_answer(word):
    vowels = 'аеёиоуэыюяaoye'
    answer = 0
    for letter in word:
        if letter in vowels:
            answer += 1
        elif letter.isupper():
            answer += 1
            break
    return answer


@GameOfRules.message_handler(commands=['start'])
def starter(message):
    if message.from_user.id not in users:
        GameOfRules.send_message(message.from_user.id, 'Вам отказано в доступе')
        print(f"\033[31m{message.from_user.username} access denied\n"
              f"\033[35m write\033[0m: \"{message.text}\"\n"
              f"\033[31mUser full\033[0m: {message.from_user}")
        return
    print(f"\033[31m{message.from_user.username}\033[32m reconnected \n"
          f"\033[35m write\033[0m: \"{message.text}\"\n")
    if current['questions'] != [] and current['position'] != 0 and current['position'] != len(current['questions']):
        GameOfRules.send_message(message.from_user.id,
                                 f"Конец, твой результат: {current['write_ans']} из {current['position']}.")
    current['questions'] = rnd.sample(words,
                                      int(message.text.split()[-1]) if message.text.split()[-1].isdigit() else 10)
    current['position'] = 0
    current['write_ans'] = 0
    current['answer'] = give_answer(current['questions'][current['position']])
    q = current['questions'][current['position']]
    num_of_variants = number_of_syllable(current['questions'][current['position']])
    markup = types.ReplyKeyboardMarkup()
    for item in range(1, num_of_variants + 1):
        markup.add(str(item))
    markup.add('/start')
    GameOfRules.send_message(message.from_user.id,
                             text=f'На какой слог падает ударение?\n{q.lower()}', reply_markup=markup)
    print(f"\033[31m bot\033[0m to \033[31m{message.from_user.username} \033[35mwrite: \033[0m\n"
          f'"На какой слог падает ударение?\n{q.lower()}"'
          f"\033[31mUser full\033[0m: {message.from_user}")


@GameOfRules.message_handler(content_types=['text'])
def questions(message):
    if message.from_user.id not in users:
        GameOfRules.send_message(message.from_user.id, 'Вам отказано в доступе')
        print(f"\033[31m{message.from_user.username} access denied\n"
              f"\033[35m write\033[0m: \"{message.text}\"\n"
              f"\033[31mUser full\033[0m: {message.from_user}")
        return
    print(f'\033[31m{message.from_user.username}\033[35m write\033[0m: "{message.text}"')
    if not current['questions']:
        markup = types.ReplyKeyboardMarkup()
        markup.add('/start')
        GameOfRules.send_message(message.from_user.id, text=f"\nНажми \"/start\"", reply_markup=markup)
        print(f"\033[31m bot\033[0m to \033[31m{message.from_user.username} \033[35mwrite: \033[0m\n"
              f'"\nНажми \"/start\""'
              f"\033[31mUser full\033[0m: {message.from_user}")
    else:
        if int(message.text) == current['answer']:
            current['write_ans'] += 1
            current['position'] += 1
            GameOfRules.send_message(message.from_user.id, 'Правильно!')
            print(f"\033[31m bot\033[0m to \033[31m{message.from_user.username} \033[35mwrite: \033[0m\n"
                  '"Правильно!"'
                  f"\033[31mUser full\033[0m: {message.from_user}")
        else:
            ans = current['questions'][current['position']]
            GameOfRules.send_message(message.from_user.id, f'Неверно, в следующий раз повезёт...\nОтвет: {ans}')
            current['position'] += 1
            print(f"\033[31m bot\033[0m to \033[31m{message.from_user.username} \033[35mwrite: \033[0m\n"
                  f'"Неверно, в следующий раз повезёт...\nОтвет: {ans}"'
                  f"\033[31mUser full\033[0m: {message.from_user}")
        if current['position'] == len(current['questions']):
            markup = types.ReplyKeyboardMarkup()
            markup.add('/start')
            GameOfRules.send_message(message.from_user.id,
                                     text=f"Конец, твой результат: {current['write_ans']} из {current['position']}."
                                          f"\nНачать заново - нажми \"/start\"", reply_markup=markup)
            print(f"\033[31m bot\033[0m to \033[31m{message.from_user.username} \033[35mwrite: \033[0m\n"
                  f'"Конец, твой результат: {current["write_ans"]} из {current["position"]}."'
                  f"\nНачать заново - нажми \"/start\""
                  f"\033[31mUser full\033[0m: {message.from_user}")
        else:
            q = current['questions'][current['position']]
            current['answer'] = give_answer(current['questions'][current['position']])
            num_of_variants = number_of_syllable(current['questions'][current['position']])
            markup = types.ReplyKeyboardMarkup()
            for item in range(1, num_of_variants + 1):
                markup.add(str(item))
            markup.add('/start')
            GameOfRules.send_message(message.from_user.id,
                                     text=f'На какой слог падает ударение?\n{q.lower()}', reply_markup=markup)
            print(f"\033[31m bot\033[0m to \033[31m{message.from_user.username} \033[35mwrite: \033[0m\n"
                  f'"На какой слог падает ударение?\n{q.lower()}"'
                  f"\033[31mUser full\033[0m: {message.from_user}")


def polling():
    try:
        GameOfRules.polling(none_stop=True, interval=0)
    except Exception:
        sleep(1)
        polling()


polling()

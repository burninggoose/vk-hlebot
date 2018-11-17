import vk_api
import random
import os
from vk_api.longpoll import VkLongPoll, VkEventType
import atexit
import pyowm
from datetime import datetime


def main():
    # Инициализируем vk_api
    vk_session = vk_api.VkApi(
        login=None, password=None, token=os.environ['VK_TOKEN'])
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    # Инициализируем погодный api
    owm = pyowm.OWM(os.environ['OWM_TOKEN'])
    observation = owm.weather_at_id(524901)
    w = observation.get_weather()

    # Ловим все выходы
    def exit_handler():
        vk.messages.send(
            chat_id=10, message='Хлебот: ' + 'я выключился или крашнулся')
    atexit.register(exit_handler)

    # Начинаем слушать longpoll
    while True:
        try:
            for event in longpoll.listen():
                if hasattr(event, 'type'):
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.from_chat:
                            if (event.text.lower() == '!флип'):
                                # Кидаем монетку
                                vk.messages.send(
                                    chat_id=event.chat_id, message='Хлебот: ' + random.choice(['Орел', 'Решка']))
                            if (event.text.lower() == '!погода'):
                                # Берем метку времени прошлой погоды
                                ts = int(w.get_reference_time('unix'))
                                # Смотрим не прошло ли полчаса
                                if (ts - datetime.now().timestamp() > 3600):
                                    # Получаем погоду заново если да
                                    w = observation.get_weather()
                                    ts = int(w.get_reference_time('unix'))
                                # Отправляем
                                vk.messages.send(chat_id=event.chat_id, message='Хлебот: ' + 'сейчас в Москве %d°C. Последнее обновление: %s' % (
                                    round(w.get_temperature('celsius')['temp']), datetime.utcfromtimestamp(
                                        ts + 10800).strftime('%H:%M')))
                            if (event.text.lower() == '!команды' or event.text.lower() == '!помощь'):
                                # Отправляем команды
                                vk.messages.send(
                                    chat_id=event.chat_id, message='Команды Хлебота:\n!погода - Погда в Москве на текущий момент\nФлип - подкидывание монетки\n!помощь или !команды - эта документация')
        except AttributeError:
            print('error')


if __name__ == '__main__':
    main()

import vk_api
import random
import os
from vk_api.longpoll import VkLongPoll, VkEventType
import atexit
import pyowm
from datetime import datetime


def degree_to_text(degree):
    if (degree > 0.0 and degree <= 22.5):
        return 'северный'
    if (degree > 22.5 and degree <= 67.5):
        return 'северо-восточный'
    if (degree > 67.5 and degree <= 112.5):
        return 'восточный'
    if (degree > 112.5 and degree <= 157.5):
        return 'юго-восточный'
    if (degree > 157.5 and degree <= 202.5):
        return 'южный'
    if (degree > 202.5 and degree <= 247.5):
        return 'юго-западный'
    if (degree > 247.5 and degree <= 292.5):
        return 'западный'
    if (degree > 292.5 and degree <= 337.5):
        return 'северо-западный'
    if (degree > 337.5 and degree <= 0.0):
        return 'северный'


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
    wind = w.get_wind()

    # Ловим все выходы
    def exit_handler():
        vk.messages.send(
            chat_id=10, message='Хлебот: ' + 'я выключился или крашнулся')
    atexit.register(exit_handler)

    # Начинаем слушать longpoll
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
                        if (datetime.now().timestamp() - ts > 3600):
                            # Получаем погоду заново если да
                            observation = owm.weather_at_id(524901)
                            w = observation.get_weather()
                            wind = w.get_wind()
                            ts = int(w.get_reference_time('unix'))
                        # Отправляем
                        vk.messages.send(chat_id=event.chat_id, message='Хлебот:\nСейчас в Москве %d°C.\nВетер %s, %dм/сек\nПоследнее обновление: %s' % (
                            round(w.get_temperature('celsius')['temp']), degree_to_text(wind['deg']), wind['speed'], datetime.utcfromtimestamp(
                                ts + 10800).strftime('%H:%M')))
                    if (event.text.lower() == '!команды' or event.text.lower() == '!помощь'):
                        # Отправляем команды
                        vk.messages.send(
                            chat_id=event.chat_id, message='Команды Хлебота:\n!погода - Погда в Москве на текущий момент\n!флип - подкидывание монетки\n!помощь или !команды - эта документация')


if __name__ == '__main__':
    main()

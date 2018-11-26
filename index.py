import vk_api
import random
import os
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import atexit
import pyowm
from datetime import datetime
from coinmarketcap import Market
import re


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


def decide_emoji(percent):
    if (percent > 0):
        return '📈'
    return '📉'


def parse_price(data):
    string = '%d. %s (%s) → %.2f USD (%.2f%%) %s\n' % (data['rank'], data['name'], data['symbol'],
                                                       data['quotes']['USD']['price'], data['quotes']['USD']['percent_change_24h'], decide_emoji(
        data['quotes']['USD']['percent_change_24h']))
    return string


def parse_prices(data):
    string = ''
    for i in data['data']:
        string += parse_price(data['data'][i])
    string += 'Последнее обновление: %s\n' % datetime.utcfromtimestamp(
        data['metadata']['timestamp'] + 10800).strftime('%H:%M')
    return string


def main():
    # Инициализируем vk_api
    vk_session = vk_api.VkApi(token=os.environ['VK_TOKEN'])
    longpoll = VkBotLongPoll(vk_session, '174462552')
    vk = vk_session.get_api()

    # Инициализируем погодный api
    owm = pyowm.OWM(os.environ['OWM_TOKEN'], language='ru')
    observation = owm.weather_at_id(524901)
    w = observation.get_weather()
    wind = w.get_wind()

    # Получаем данные крипты
    coinmarketcap = Market()
    data = coinmarketcap.ticker(
        start=0, limit=10, convert='USD')
    datatimestamp = 0

    # Ловим все выходы

    def exit_handler():
        vk.messages.send(
            chat_id=10, message='Хлебот: ' + 'я выключился или крашнулся')
    atexit.register(exit_handler)

    # Начинаем слушать longpoll
    for event in longpoll.listen():
        print(event.obj.peer_id)
        if hasattr(event, 'type'):
            if event.type == VkBotEventType.MESSAGE_NEW:
                if (re.match(r'!флип', event.obj.text.lower())):
                    # Кидаем монетку
                    vk.messages.send(
                        peer_id=event.obj.peer_id, random_id=event.obj.random_id, message='Хлебот: ' + random.choice(['Орел', 'Решка']))
                elif (re.match(r'!погода', event.obj.text.lower())):
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
                    vk.messages.send(peer_id=event.obj.peer_id, random_id=event.obj.random_id, message='Хлебот:\nСейчас в Москве: %d°C, %s\nВетер: %s, %dм/сек\nВлажность: %d%%\nПоследнее обновление: %s' % (
                        round(w.get_temperature('celsius')['temp']), w.get_detailed_status(), degree_to_text(wind['deg']), wind['speed'], w.get_humidity(), datetime.utcfromtimestamp(
                            ts + 10800).strftime('%H:%M')))
                elif (re.match(r'!курс', event.obj.text.lower())):
                    # Смотрим не прошли ли 5 минут
                    if (datetime.now().timestamp() - datatimestamp > 60):
                        data = coinmarketcap.ticker(
                            start=0, limit=10, convert='USD')
                        datatimestamp = datetime.now().timestamp()
                        vk.messages.send(peer_id=event.obj.peer_id, random_id=event.obj.random_id, message='Хлебот:\n%s' % parse_prices(
                            data))
                    else:
                        vk.messages.send(
                            peer_id=event.obj.peer_id, random_id=event.obj.random_id, message='Хлебот: команду !курс можно использовать раз в минуту')
                elif ((re.match(r'!команды', event.obj.text.lower())) or (re.match(r'!помощь', event.obj.text.lower()))):
                    # Отправляем команды
                    vk.messages.send(
                        peer_id=event.obj.peer_id, random_id=event.obj.random_id, message='Команды Хлебота:\n!погода - Погда в Москве на текущий момент\n!флип - подкидывание монетки\n!курс - состояние топ-10 криптовалют\n!помощь или !команды - эта документация')


if __name__ == '__main__':
    main()

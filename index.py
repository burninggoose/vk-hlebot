import vk_api
import random
import os
from vk_api.longpoll import VkLongPoll, VkEventType
import atexit
import pyowm
from datetime import datetime
from coinmarketcap import Market
import schedule


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
    vk_session = vk_api.VkApi(
        login=None, password=None, token=os.environ['VK_TOKEN'])
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

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

    def send_morning():
        forecast = owm.three_hours_forecast('Moscow,RU')
        fc9 = forecast.get_weather_at(int(datetime.now().timestamp()) + 3600)
        fc13 = forecast.get_weather_at(
            int(datetime.now().timestamp()) + 3600 * 5)
        fc18 = forecast.get_weather_at(
            int(datetime.now().timestamp()) + 3600 * 9)
        vk.messages.send(
            chat_id=10, message='Хлебот:\nДоброе утро, чат!\nПрогноз погоды на день:\n9:00: %d°C, %s\n13:00: %d°C, %s\n18:00: %d°C, %s' % (
                round(fc9.get_temperature('celsius')['temp']), fc9.get_detailed_status(), round(fc13.get_temperature('celsius')['temp']), fc13.get_detailed_status(), round(fc18.get_temperature('celsius')['temp']), fc18.get_detailed_status()))

    schedule.every().day.at("5:21").do(send_morning)

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
                        vk.messages.send(chat_id=event.chat_id, message='Хлебот:\nСейчас в Москве: %d°C, %s\nВетер: %s, %dм/сек\nВлажность: %d%%\nПоследнее обновление: %s' % (
                            round(w.get_temperature('celsius')['temp']), w.get_detailed_status(), degree_to_text(wind['deg']), wind['speed'], w.get_humidity(), datetime.utcfromtimestamp(
                                ts + 10800).strftime('%H:%M')))
                    if (event.text.lower() == '!курс'):
                        # Смотрим не прошли ли 5 минут
                        if (datetime.now().timestamp() - datatimestamp > 60):
                            data = coinmarketcap.ticker(
                                start=0, limit=10, convert='USD')
                            datatimestamp = datetime.now().timestamp()
                            vk.messages.send(chat_id=event.chat_id, message='Хлебот:\n%s' % parse_prices(
                                data))
                        else:
                            vk.messages.send(
                                chat_id=event.chat_id, message='Хлебот: команду !курс можно использовать раз в минуту')
                    if (event.text.lower() == '!команды' or event.text.lower() == '!помощь'):
                        # Отправляем команды
                        vk.messages.send(
                            chat_id=event.chat_id, message='Команды Хлебота:\n!погода - Погда в Москве на текущий момент\n!флип - подкидывание монетки\n!курс - состояние топ-10 криптовалют\n!помощь или !команды - эта документация')


if __name__ == '__main__':
    main()

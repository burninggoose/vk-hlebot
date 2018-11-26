import vk_api
from datetime import datetime, date, time
import pyowm
import schedule
import os
import inspect
import time as time2

vk_session = vk_api.VkApi(
    login=None, password=None, token=os.environ['VK_TOKEN'])
vk = vk_session.get_api()

owm = pyowm.OWM(os.environ['OWM_TOKEN'], language='ru')


def send_morning():
    forecast = owm.three_hours_forecast('Moscow,RU')
    fc9 = forecast.get_weather_at(
        int(datetime.combine(date.today(), time(6, 00)).timestamp()))
    fc13 = forecast.get_weather_at(
        int(datetime.combine(date.today(), time(10, 00)).timestamp()))
    fc18 = forecast.get_weather_at(
        int(datetime.combine(date.today(), time(15, 00)).timestamp()))
    vk.messages.send(
        peer_id=2000000002, random_id=0, message='Доброе утро, чат!\nПрогноз погоды на день:\n9:00: %d°C, %s\n13:00: %d°C, %s\n18:00: %d°C, %s' % (
            round(fc9.get_temperature('celsius')['temp']), fc9.get_detailed_status(), round(fc13.get_temperature('celsius')['temp']), fc13.get_detailed_status(), round(fc18.get_temperature('celsius')['temp']), fc18.get_detailed_status()))


def main():
    print('working')
    schedule.every().day.at("5:21").do(send_morning)
    while True:
        schedule.run_pending()
        time2.sleep(1)


if __name__ == '__main__':
    main()

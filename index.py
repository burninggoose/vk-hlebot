import vk_api
import random
import os
from vk_api.longpoll import VkLongPoll, VkEventType
import atexit


def main():
    vk_session = vk_api.VkApi(
        login=None, password=None, token=os.environ['TOKEN'])
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

   # vk.messages.send(
    #    chat_id=10, message='Бот хлеба: Выпускаем кракена')

    def exit_handler():
        vk.messages.send(
            chat_id=10, message='Хлебот: ' + 'я выключился или крашнулся')

    atexit.register(exit_handler)

    for event in longpoll.listen():
        if hasattr(event, 'type'):
            if event.type == VkEventType.MESSAGE_NEW:
                if event.from_chat:
                    if (event.chat_id == 10):
                        if (event.text == '!флип'):
                            vk.messages.send(
                                chat_id=10, message='Хлебот: ' + random.choice(['Орел', 'Решка']))


if __name__ == '__main__':
    main()

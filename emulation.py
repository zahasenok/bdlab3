import random
import atexit
from threading import Thread
from faker import Faker
from Tags import Tags
from servers.RedisServer import RedisServer
from dotenv import dotenv_values

config = dotenv_values(".env")

fake = Faker()


class User(Thread):
    def __init__(self, server: RedisServer, username, users_list, users_amount):
        Thread.__init__(self)
        self.__users_list = users_list
        self.__users_amount = users_amount
        self.__server = server

        self.__server.register(username)
        self.__user_id = self.__server.login(username)

    def run(self):
        for i in range(5):
            message_text = fake.sentence(
                nb_words=15, variable_nb_words=True, ext_word_list=None
            )
            receiver = self.__users_list[random.randint(0, self.__users_amount - 1)]
            self.__server.create_message(
                self.__user_id, receiver, message_text, Tags.get_random()
            )

        print("%s - done" % self.__user_id)


def exit_handler():
    server = RedisServer()
    online = server.get_online_users()

    for username in online:
        server.logout(username)


def emulation():
    atexit.register(exit_handler)

    users_amount = 15
    threads = []
    users = [
        fake.profile(fields=["username"], sex=None)["username"]
        for u in range(users_amount)
    ]

    for i in range(users_amount):
        threads.append(User(RedisServer(), users[i], users, users_amount))

    for t in threads:
        t.start()

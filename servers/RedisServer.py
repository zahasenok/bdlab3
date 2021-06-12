import redis
import logging
import Tags
from servers.Neo4jServer import Neo4jServer
from dotenv import dotenv_values

config = dotenv_values(".env")
logging.basicConfig(
    filename="lab3.log",
    level=logging.INFO,
    encoding="utf-8",
    format="[%(asctime)s] — %(message)s",
    datefmt="%d-%m-%YT%H:%M:%S",
)


class RedisServer:
    def __init__(self):
        self.__connection = redis.StrictRedis(
            host=config["REDIS_HOST"],
            port=config["REDIS_PORT"],
            password=config["REDIS_PASSWORD"],
            charset="utf-8",
            decode_responses=True,
        )
        self.__neo4j_server = Neo4jServer()

    def register(self, username):
        if self.__connection.hget("users", username):
            print("User already exist!")
            return

        user_id = self.__connection.incr("user:id")

        pipeline = self.__connection.pipeline(True)
        pipeline.hset("users", username, user_id)
        pipeline.hset("user:%s" % user_id, "login", username)
        pipeline.hset("user:%s" % user_id, "queue", 0)
        pipeline.hset("user:%s" % user_id, "checking", 0)
        pipeline.hset("user:%s" % user_id, "blocked", 0)
        pipeline.hset("user:%s" % user_id, "sent", 0)
        pipeline.hset("user:%s" % user_id, "delivered", 0)
        pipeline.execute()

        self.__neo4j_server.register(username, user_id)

        logging.info("User: %s\tAction: register\n" % username)

    def login(self, username) -> int:
        try:
            user_id = int(self.__connection.hget("users", username))
        except TypeError:
            print("User not found!")
            return None
        else:
            self.__connection.sadd("online", username)
            self.__connection.publish("users", "%s logged in" % username)
            logging.info("User: %s;\tAction: login" % username)

            self.__neo4j_server.login(user_id)

            return user_id

    def logout(self, username):
        # username = self.__connection.hget("user:%s" % user_id, "login")

        self.__connection.srem("online", username)
        self.__connection.publish("users", "User %s signed out" % username)

        self.__neo4j_server.logout(username)

        logging.info("User: %s;\tAction: logout" % username)

    def create_message(self, user_id, receiver, text, tags: Tags):
        try:
            receiver_id = int(self.__connection.hget("users", receiver))
        except TypeError:
            print("Receiver not found!")
            return

        message_id = int(self.__connection.incr("message:id"))
        current_user = self.__connection.hget("user:%s" % user_id, "login")

        pipeline = self.__connection.pipeline(True)

        msg_key = "message:%s" % message_id

        pipeline.hset(msg_key, "id", message_id)
        pipeline.hset(msg_key, "sender_id", user_id)
        pipeline.hset(msg_key, "receiver_id", receiver_id)
        pipeline.hset(msg_key, "text", text)
        pipeline.hset(msg_key, "tags", ",".join(tags))
        pipeline.hset(msg_key, "status", "created")

        pipeline.lpush("queue", message_id)

        pipeline.hset(msg_key, "status", "queue")

        pipeline.zincrby("sent", 1, "%s:%s" % (user_id, current_user))
        pipeline.hincrby("user:%s" % user_id, "queue", 1)

        pipeline.execute()

        self.__neo4j_server.create_message(
            user_id, receiver_id, {"id": message_id, "tags": tags}
        )

    def get_online_users(self):
        return self.__connection.smembers("online")

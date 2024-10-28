import json
from random import randint

from channels.generic.websocket import WebsocketConsumer
from time import sleep


class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        for i in range(1000):
            self.send(json.dumps({'message': randint(1, 1000)}))
            sleep(1)

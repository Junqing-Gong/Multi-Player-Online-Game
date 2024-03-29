from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.conf import settings
from django.core.cache import cache

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from match_system.src.match_server.match_service import Match
from game.models.player.player import Player
from channels.db import database_sync_to_async

class MultiPlayer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code): # 有可能用户离线了也不断开
        if self.room_name:
            await self.channel_layer.group_discard(self.room_name, self.channel_name);

    async def group_send_event(self, data): # 与下面的type内容一致
        if not self.room_name:
            keys = cache.keys('*%s*' % (self.uuid))
            if keys:
                self.room_name = keys[0]
        await self.send(text_data=json.dumps(data)) # dumps将字典变为字符串

    async def create_player(self, data):
        self.room_name = None
        self.uuid = data['uuid']

        # Make socket
        transport = TSocket.TSocket('127.0.0.1', 9090)

        # Buffering is critical. Raw sockets are very slow
        transport = TTransport.TBufferedTransport(transport)

        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(transport)

        # Create a client to use the protocol encoder
        client = Match.Client(protocol)

        def db_get_player():
            return Player.objects.get(user__username=data['username'])

        player = await database_sync_to_async(db_get_player)()

        # Connect!
        transport.open()

        client.add_player(player.score, data['uuid'], data['username'], data['photo'], self.channel_name)

        # Close!
        transport.close()


    async def move_to(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "move_to",
                'uuid': data['uuid'],
                'tx': data['tx'],
                'ty': data['ty'],
            }
        )

    async def shoot_fireball(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "shoot_fireball",
                'uuid': data['uuid'],
                'tx': data['tx'],
                'ty': data['ty'],
                'ball_uuid': data['ball_uuid'],
            }
        )

    async def attack(self, data):
        if not self.room_name:
            return

        players = cache.get(self.room_name)

        if not players:
            return

        for player in players:
            if player['uuid'] == data['attackee_uuid']:
                player['hp'] -= 25

        remain_cnt = 0
        for player in players:
            if player['hp'] > 0:
                remain_cnt += 1

        if remain_cnt > 1:
            if self.room_name:
                cache.set(self.room_name, players, 3600)
        else:
            def db_update_player_score(username, score):
                player = Player.objects.get(user__username=username) # get找不到会报异常，filter不会报异常，找不到就是空
                player.score += score
                player.save();
            for player in players:
                if player['hp'] <= 0:
                    await database_sync_to_async(db_update_player_score)(player['username'], 0) # sync同步->async异步，一定要加await
                else:
                    await database_sync_to_async(db_update_player_score)(player['username'], 0)

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "attack",
                'attackee_uuid': data['attackee_uuid'],
                'uuid': data['uuid'],
                'x': data['x'],
                'y': data['y'],
                'angle': data['angle'],
                'damage': data['damage'],
                'ball_uuid': data['ball_uuid'],
            }
        )

    async def blink(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "blink",
                'uuid': data['uuid'],
                'tx': data['tx'],
                'ty': data['ty'],
            }
        )

    async def message(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "message",
                'uuid': data['uuid'],
                'username': data['username'],
                'text': data['text'],
            }
        )

    async def shoot_frozenball(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "shoot_frozenball",
                'uuid': data['uuid'],
                'tx': data['tx'],
                'ty': data['ty'],
                'ball_uuid': data['ball_uuid'],
            }
        )

    async def frozen(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "frozen",
                'attackee_uuid': data['attackee_uuid'],
                'uuid': data['uuid'],
                'x': data['x'],
                'y': data['y'],
                'ball_uuid': data['ball_uuid'],
            }
        )

    async def receive(self, text_data): # 接收前端向后端发的请求
        data = json.loads(text_data)
        event = data['event']
        if event == "create_player":
            await self.create_player(data)
        elif event == "move_to":
            await self.move_to(data)
        elif event == "shoot_fireball":
            await self.shoot_fireball(data)
        elif event == "attack":
            await self.attack(data)
        elif event == "blink":
            await self.blink(data)
        elif event == "message":
            await self.message(data)
        elif event == "shoot_frozenball":
            await self.shoot_frozenball(data)
        elif event == "frozen":
            await self.frozen(data)

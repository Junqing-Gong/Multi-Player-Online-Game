#! /usr/bin/env python3

import glob
import sys
sys.path.insert(0, glob.glob('../../')[0]) # 将django家目录加进来，才能import django项目中的包

from match_server.match_service import Match

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from queue import Queue
import time
from threading import Thread

from acapp.asgi import channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache

queue = Queue() # 消息队列

class Player:
    def __init__(self, score, uuid, username, photo, channel_name):
        self.score = score
        self.uuid = uuid
        self.username = username
        self.photo = photo
        self.channel_name = channel_name
        self.waiting_time = 0 # 等待时间

class Pool:
    def __init__(self):
        self.players = []

    def add_player(self, player):
        print("add player: " +  player.username + f", {player.score}")
        self.players.append(player)

    def check_match(self, a, b):
        # if a.username = b.username: # 避免相同玩家匹配到一起
        #     return False
        dt = abs(a.score - b.score)
        a_max_dif = a.waiting_time * 50
        b_max_dif = b.waiting_time * 50
        return dt <= a_max_dif and dt <= b_max_dif

    def match_success(self, ps):
        print(f'Match Success: {ps[0].username}, {ps[1].username}, {ps[2].username}')
        room_name = "room-%s-%s-%s" % (ps[0].uuid, ps[1].uuid, ps[2].uuid)
        players = []
        for p in ps:
            async_to_sync(channel_layer.group_add)(room_name, p.channel_name)
            players.append({
                'uuid': p.uuid,
                'username': p.username,
                'photo': p.photo,
                'hp': 100,
            })
        cache.set(room_name, players, 3600)  # 有效时间：1小时
        for p in ps:
            async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    'type': "group_send_event",
                    'event': "create_player",
                    'uuid': p.uuid,
                    'username': p.username,
                    'photo': p.photo,
                }
            )

    def increase_waiting_time(self):
        for player in self.players:
            player.waiting_time += 1

    def match(self):
        while len(self.players) >= 3:
            self.players = sorted(self.players, key = lambda p : p.score)

            flag = False
            for i in range(len(self.players) - 2):
                a, b, c = self.players[i], self.players[i+1], self.players[i+2]
                if self.check_match(a, b) and self.check_match(b, c) and self.check_match(a, c):
                    self.match_success([a, b, c])
                    self.players = self.players[:i] + self.players[i+3:]
                    flag = True
                    break
            if not flag:
                break;

        self.increase_waiting_time()

class MatchHandler:
    def add_player(self, score, uuid, username, photo, channel_name):
        player = Player(score, uuid, username, photo, channel_name)
        queue.put(player)
        return 0 # 没有返回值会报错

def get_player_from_queue():
    try:
        return queue.get_nowait() # 见官方文档，能取就get，不能取就报empty异常
    except:
        return None

def worker():
    pool = Pool();
    while True:
        player = get_player_from_queue()
        if player:
            pool.add_player(player)
        else:
            pool.match()
            time.sleep(1)

if __name__ == '__main__':
    handler = MatchHandler()
    processor = Match.Processor(handler)
    transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    # 三种开线程的方式
    # server = TServer.TSimpleServer(processor, transport, tfactory, pfactory) # 单线程
    server = TServer.TThreadedServer( # 每一个新的请求都开一个新的server，并行度最高
         processor, transport, tfactory, pfactory)
    # server = TServer.TThreadPoolServer( # 匹配池里预先开一些线程，超过线程数量则堵塞
    #     processor, transport, tfactory, pfactory)

    Thread(target=worker, daemon=True).start() # True 关掉主线程时该线程一起关闭

    print('Starting the server...')
    server.serve() # 是一个死循环
    print('done.')

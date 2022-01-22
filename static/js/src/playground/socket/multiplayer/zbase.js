class MultiPlayerSocket {
    constructor(playground) {
        this.playground = playground;

        this.ws = new WebSocket("wss://app250.acapp.acwing.com.cn/wss/multiplayer/")

        this.start();
    }

    start() {
        this.receive();
    }

    receive() { //  接收后端传回来的消息
        let outer = this;

        this.ws.onmessage = function(e) {
            let data = JSON.parse(e.data); // parse将字符串变为字典
            let uuid = data.uuid;
            if (uuid === outer.uuid) return false;

            let event = data.event;
            if (event === "create_player") {
                outer.receive_create_player(uuid, data.username, data.photo);
            } else if (event === "move_to") {
                outer.receive_move_to(uuid, data.tx, data.ty);
            } else if (event === "shoot_fireball") {
                outer.receive_shoot_fireball(uuid, data.tx, data.ty, data.ball_uuid);
            } else if (event === "attack") {
                outer.receive_attack(uuid, data.attackee_uuid, data.x, data.y, data.angle, data.damage, data.ball_uuid);
            } else if (event === "blink") {
                outer.receive_blink(uuid, data.tx, data.ty);
            } else if (event === "message") {
                outer.receive_message(data.username, data.text);
            } else if (event === "shoot_frozenball") {
                outer.receive_shoot_frozenball(uuid, data.tx, data.ty, data.ball_uuid);
            } else if (event === "frozen") {
                outer.receive_frozen(uuid, data.attackee_uuid, data.x, data.y, data.ball_uuid);
            }
        };
    }

    get_player(uuid) {
        let players = this.playground.players;

        for (let i = 0; i < players.length; i ++ ) {
            let player = players[i];
            if (player.uuid === uuid) {
                return player
            }
        }

        return null;
    }

    send_create_player(username, photo) {
        let outer = this;

        this.ws.send(JSON.stringify({
            'event': "create_player",
            'uuid': outer.uuid,
            'username': username,
            'photo': photo,
        }));
    }

    receive_create_player(uuid, username, photo) {
        let player = new Player(
            this.playground,
            this.playground.width / 2 /this.playground.scale,
            0.5,
            0.05,
            "white",
            0.15,
            "enemy",
            username,
            photo,
        );

        player.uuid = uuid;
        this.playground.players.push(player);
    }

    send_move_to(tx, ty) {
        let outer = this;

        this.ws.send(JSON.stringify({
            'event': "move_to",
            'uuid': outer.uuid,
            'tx': tx,
            'ty': ty,
        }));
    }

    receive_move_to(uuid, tx, ty) {
        let player = this.get_player(uuid);

        if (player) {
            player.move_to(tx, ty);
        }
    }

    send_shoot_fireball(tx, ty, ball_uuid) {
        let outer = this;

        this.ws.send(JSON.stringify({
            'event': "shoot_fireball",
            'uuid': outer.uuid,
            'tx': tx,
            'ty': ty,
            'ball_uuid': ball_uuid,
        }));
    }

    receive_shoot_fireball(uuid, tx, ty, ball_uuid) {
        let player = this.get_player(uuid);

        if (player) {
            let fireball = player.shoot_fireball(tx, ty);
            fireball.uuid = ball_uuid; // 所有窗口中的一个火球对应的uuid相同
        }
    }

    send_attack(attackee_uuid, x, y, angle, damage, ball_uuid) {
        let outer = this;
        this.ws.send(JSON.stringify({
            'event': "attack",
            'uuid': outer.uuid,
            'attackee_uuid': attackee_uuid,
            'x': x,
            'y': y,
            'angle': angle,
            'damage': damage,
            'ball_uuid': ball_uuid,
        }));
    }

    receive_attack(uuid, attackee_uuid, x, y, angle, damage, ball_uuid) {
        let attacker = this.get_player(uuid);
        let attackee = this.get_player(attackee_uuid);
        if (attacker && attackee) {
            attackee.receive_attack(x, y, angle, damage, ball_uuid, attacker);
        }
    }

    send_blink(tx, ty) {
        let outer = this;

        this.ws.send(JSON.stringify({
            'event': "blink",
            'uuid': outer.uuid,
            'tx': tx,
            'ty': ty,
        }));
    }

    receive_blink(uuid, tx, ty) {
        let player = this.get_player(uuid);

        if (player) {
            player.blink(tx, ty);
        }
    }

    send_message(username ,text) {
        let outer = this;

        this.ws.send(JSON.stringify({
            'event': "message",
            'uuid': outer.uuid,
            'username': username,
            'text': text,
        }));
    }

    receive_message(username, text) {
        this.playground.chat_field.add_message(username, text);
    }

    send_shoot_frozenball(tx, ty, ball_uuid) {
        let outer = this;

        this.ws.send(JSON.stringify({
            'event': "shoot_frozenball",
            'uuid': outer.uuid,
            'tx': tx,
            'ty': ty,
            'ball_uuid': ball_uuid,
        }));
    }

    receive_shoot_frozenball(uuid, tx, ty, ball_uuid) {
        let player = this.get_player(uuid);

        if (player) {
            let frozenball = player.shoot_frozenball(tx, ty);
            frozenball.uuid = ball_uuid; // 所有窗口中的一个冰球对应的uuid相同
        }
    }

    send_frozen(attackee_uuid, x, y, ball_uuid) {
        let outer = this;
        this.ws.send(JSON.stringify({
            'event': "frozen",
            'uuid': outer.uuid,
            'attackee_uuid': attackee_uuid,
            'x': x,
            'y': y,
            'ball_uuid': ball_uuid,
        }));
    }

    receive_frozen(uuid, attackee_uuid, x, y, ball_uuid) {
        let attacker = this.get_player(uuid);
        let attackee = this.get_player(attackee_uuid);
        if (attacker && attackee) {
            attackee.receive_frozen(x, y, ball_uuid, attacker);
        }
    }

}

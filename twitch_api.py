import socket
import time
from typing import Dict
import re

import settings


twitch_host = 'irc.chat.twitch.tv'
twitch_port = 6667
chat_msg_re = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
max_message_size = 250


def chat(sock: socket.socket, channel: str, msg: str):
    print("Sending message: {}".format(msg))
    sock.send('PRIVMSG {} :{}\r\n'.format(channel, msg).encode('utf-8'))
    time.sleep(1 / settings.bot_rate)


def setup_socket(token: str, username: str, channel: str) -> socket.socket:
    s = socket.socket()
    s.connect((twitch_host, 6667))
    s.send("PASS {}\r\n".format(token).encode("utf-8"))
    s.send("NICK {}\r\n".format(username).encode("utf-8"))
    s.send("JOIN {}\r\n".format(channel).encode("utf-8"))
    chat(s, channel, '/me has landed!')
    return s


def parse_twitch_message(s: str) -> Dict[str, str]:
    result = {}
    username = re.search(r"\w+", s).group(0)  # return the entire match
    message = chat_msg_re.sub("", s)
    result['username'] = username
    result['message'] = message
    return result


class TwitchRPBot:
    def __init__(self, token: str, username: str, channel: str):
        self.s = setup_socket(token, username, channel)
        self.token = token
        self.username = username
        self.channel = channel
        self.commands = set()
        self.setup_commands()

    def __del__(self):
        self.s.close()

    def setup_commands(self):
        pass

    def get_msg(self) -> str:
        while True:
            response = self.s.recv(1024).decode("utf-8")
            if response == "PING :tmi.twitch.tv\r\n":
                self.s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            else:
                return response
            time.sleep(1 / settings.bot_rate)

    def chat(self, msg: str):
        if len(msg) > max_message_size:
            msg_count = len(msg) // max_message_size + 1
            iter = 1
            while iter <= msg_count:
                prepart = "Part {}/{} ".format(iter, msg_count)
                print("Sending message: {}{}".format(prepart, msg[:(max_message_size - len(prepart) - 1)]
                if len(msg) > (max_message_size - len(prepart) - 1)
                else msg))

                chat(self.s, self.channel, '{}{}'.format(prepart,
                                                         msg[:(max_message_size - len(prepart) - 1)]
                                                         if len(msg) > (max_message_size - len(prepart) - 1)
                                                         else msg))
                iter += 1
                if len(msg) > (max_message_size - len(prepart) - 1):
                    msg = msg[(max_message_size - len(prepart) - 1):]
            return
        chat(self.s, self.channel, msg)

    def run(self):
        while True:
            msg = self.get_msg().strip()
            print(msg)
            d = parse_twitch_message(msg)
            if d['username'] != self.username:
                words = d['message'].split(' ')
                print('{}: {}'.format(d['username'], d['message']))
                if len(words) > 0 and words[0].startswith(settings.bot_prefix):
                    # print("Found a command {}".format(words[0]))
                    cmd = words[0][1:].lower().strip()
                    if cmd in self.commands:
                        # print("Command {} was in the commands list".format(cmd))
                        exec('self.{}("{}", {})'.format(cmd,
                                                        d['username'],
                                                        words[1:] if len(words) > 1 else []))
                    else:
                        print("{} is not in list of {}".format(cmd, self.commands))


if __name__ == '__main__':
    cb = TwitchRPBot(settings.tmi_token, settings.bot_nick, settings.channel)
    while True:
        print(cb.get_msg())
        chat(cb.s, cb.channel, 'hello.')
        time.sleep(1 / settings.bot_rate)

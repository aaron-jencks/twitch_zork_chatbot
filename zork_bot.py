from typing import List

from twitch_api import TwitchRPBot
from zork_api import *


class ZorkBot(TwitchRPBot):
    def __init__(self, token: str, username: str, channel: str):
        super().__init__(token, username, channel)
        self.players = {}

    def setup_commands(self):
        self.commands.add('restart')
        self.commands.add('refresh')
        self.commands.add('do')
        self.commands.add('start')
        self.commands.add('help')
        print(self.commands)

    def start(self, user: str, args: List[str]):
        print('Starting off player')
        self.players[user] = reset_player(user)
        self.chat("@{} your new number is n={}".format(user, self.players[user]))
        self.refresh(user, args)

    def restart(self, user: str, args: List[str]):
        self.start(user, args)

    def refresh(self, user: str, args: List[str]):
        print("Refreshing player")
        if user not in self.players:
            self.players[user] = -1
        resp = find_statuses(send_command(user, 'look'))[-1]
        self.chat('@{} {}'.format(user, resp))

    def do(self, user: str, args: List[str]):
        if user not in self.players:
            self.players[user] = -1
        cmd = ' '.join(args).strip()
        print("Executing a command {}".format(cmd))
        resp = find_statuses(send_command(user, cmd))[-1]
        self.chat('@{} {}'.format(user, resp))

    def help(self, user: str, args: List[str]):
        self.chat("Welcome to Zork Adventure Bot v1.0, "
                  "to start playing a new game use the !start or !restart commands, "
                  "use !do to play, use !refresh to display your current location, "
                  "and use !help to display this message, "
                  "for a list of helpful commands, "
                  "try http://mirrors.ibiblio.org/interactive-fiction/infocom/demos/ztuu.pdf")


if __name__ == '__main__':
    import settings
    cb = ZorkBot(settings.tmi_token, settings.bot_nick, settings.channel)
    cb.run()

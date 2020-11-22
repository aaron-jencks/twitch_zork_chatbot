import requests
from bs4 import BeautifulSoup
import re
from typing import List


zork_url = 'http://www.web-adventures.org/cgi-bin/webfrotz'
status_re = re.compile(r'<p.*>(.(?!</p>))+\s*</p>(?P<response>(.(?!(&gt;|</td>)))+)\s*(&gt;|</td>)')


def send_command(user: str, cmd: str) -> requests.Response:
    resp = requests.post(zork_url, data={'a': cmd, 'x': user, 's': 'ZorkDungeon'})
    return resp


def format_status(s: str) -> str:
    return s.replace('<br/>', '  ').strip(' \n').replace('<b>', '').replace('</b>', '')


def find_statuses(resp: requests.Response) -> List[str]:
    s = resp.content
    soup = BeautifulSoup(s, 'html.parser')
    r = soup.find_all('td')[1].prettify().replace('\n', '').replace('<font', '\n<font').replace('</td', ' </td')
    return [format_status(d[1]) for d in status_re.findall(r)]


def reset_player(user: str) -> int:
    resp = send_command(user, 'look')
    soup = BeautifulSoup(resp.content, 'html.parser')
    links = soup.find_all('a')
    reset_link = [l['href'] for l in links if l.text == 'restart']
    n = int(reset_link[0][reset_link[0].rfind('=') + 1:])
    requests.post(zork_url, data={'s': 'ZorkDungeon',
                                  'x': user,
                                  'n': n})
    return n


if __name__ == '__main__':
    print('Welcome to Zork!')
    cmd = 'look'
    while cmd != 'quit':
        resps = find_statuses(send_command('iggy', cmd, 0))
        print(resps[-1])
        cmd = input('>>> ').lower()

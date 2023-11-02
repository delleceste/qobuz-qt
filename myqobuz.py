# This Python file uses the following encoding: utf-8
import os
import sys
import termios
import tty
from minim import qobuz as q

def login():
    gia = q.Session(email='delleceste@gmail.com',password='Nautilus803',authenticate=True)
    # print(gia)
    return gia

def unbuf_in():
    stdin = sys.stdin.fileno()
    tattr = termios.tcgetattr(stdin)
    buf = ''
    try:
        tty.setraw(stdin)
        buf = sys.stdin.read(1)
    finally:
        termios.tcsetattr(stdin, termios.TCSANOW, tattr)
    return buf

def menu():
    print('a. Album search')
    print('t. ArTist search')
    print('l. Label search')
    choice = unbuf_in()
    return choice

if __name__ == "__main__":
    gia = login()
    me = gia.get_me()
    if 'streaming-studio' != me['credential']['label']:
        print(f'error: user credential type is not "streaming-studio"')
    else:
        n = me['firstname']
        print(f'logged in as \033[1;32m{n}\033[0m')

        choice = menu()
        print(f'choice: {choice}')

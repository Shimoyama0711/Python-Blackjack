import datetime
import socket
import sys


# 引数エラー #
def args_exception():
    msg = f"""
\u001b[31mArguments Exception:\u001b[0m

How to use:
\u001b[97m$ \u001b[33mpython\u001b[97m blackjack_client.py \u001b[91m<Server IP Address>\u001b[0m
"""
    print(msg)


N = 2048

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# host = "172.16.14.0"

try:
    host = sys.argv[1]
except IndexError:
    args_exception()
    exit(1)


port = 8000
s.connect((host, port))


while True:
    # s.send(bytes("\u001b[31mThe quick brown fox jumped over the lazy dog. :)\u001b[0m\n", "utf-8"))

    data = s.recv(N)
    decoded = data.decode("utf-8")

    print(f"[{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}] {decoded}")

    if decoded.find("[EOF]") != -1:
        s.close()
        break

    if decoded.find("[*]") != -1:
        message = input("> ")
        s.send(message.encode("utf-8"))

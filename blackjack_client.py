import datetime
import socket
import sys

N = 2048

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# host = "172.16.14.0"
host = sys.argv[1]
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

import socket
import threading
import datetime
import time
import mysql.connector as mydb
import random

PORT = 8000  # ポート
BUFFER_SIZE = 2048  # バッファサイズ
client_no = 0  # クライアント番号

dictionary = {}  # 持っているカードを保持
suits = ["♥", "♦", "♣", "♠"]  # スート
numbers = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]  # 数字

in_game = False  # ゲーム中かどうかを判定


# 「ようこそ」メッセージ
def send_welcome_message(client):
    data = f"""
  ____  _            _    _            _    
 |  _ \\| |          | |  (_)          | |   
 | |_) | | __ _  ___| | ___  __ _  ___| | __
 |  _ <| |/ _` |/ __| |/ / |/ _` |/ __| |/ /
 | |_) | | (_| | (__|   <| | (_| | (__|   < 
 |____/|_|\\__,_|\\___|_|\\_\\ |\\__,_|\\___|_|\\_\\
                        _/ |                
                       |__/                                
    
Welcome to BlackJack Game!

Created by: Group G @ ComputerNetwork II
GitHub Repository: https://github.com/Shimoyama0711/Python-Blackjack

"""
    client.send(data.encode("utf-8"))


# 「YOU WIN!」メッセージ
win_message = f"""
\u001b[92m
__   __ _____  _   _   _    _  _____  _   _  _ 
\\ \\ / /|  _  || | | | | |  | ||_   _|| \\ | || |
 \\ V / | | | || | | | | |  | |  | |  |  \\| || |
  \\ /  | | | || | | | | |/\\| |  | |  | . ` || |
  | |  \\ \\_/ /| |_| | \\  /\\  / _| |_ | |\\  ||_|
  \\_/   \\___/  \\___/   \\/  \\/  \\___/ \\_| \\_/(_)
\u001b[0m                                            
"""

# 「YOU LOSE...」メッセージ
lose_message = f"""
\u001b[36m
__   __ _____  _   _   _      _____  _____  _____          
\\ \\ / /|  _  || | | | | |    |  _  |/  ___||  ___|         
 \\ V / | | | || | | | | |    | | | |\\ `--. | |__           
  \\ /  | | | || | | | | |    | | | | `--. \\|  __|          
  | |  \\ \\_/ /| |_| | | |____\\ \\_/ //\\__/ /| |___  _  _  _ 
  \\_/   \\___/  \\___/  \\_____/ \\___/ \\____/ \\____/ (_)(_)(_)
\u001b[0m                                            
"""

# 「DRAW」メッセージ
draw_message = f"""
\u001b[37m
  _____    _____              __          __
 |  __ \\  |  __ \\      /\\     \\ \\        / /
 | |  | | | |__) |    /  \\     \\ \\  /\\  / / 
 | |  | | |  _  /    / /\\ \\     \\ \\/  \\/ /  
 | |__| | | | \\ \\   / ____ \\     \\  /\\  /   
 |_____/  |_|  \\_\\ /_/    \\_\\     \\/  \\/    
 \u001b[0m
"""


# 山札をリセットしてシャッフルした配列を返します
def reset_deck():
    array = []  # 山札の配列の定義

    # スートのループ
    for suit in suits:
        # A, 2～10, J, Q, K のループ
        for number in numbers:
            array.append(f"{suit}{number}")  # 山札の配列に追加

    random.shuffle(array)  # 山札をシャッフルします

    return array  # 山札を返す


# IPアドレスのデータが存在しなければ INSERT IGNORE INTO を実行します
def create_user_data(ip_address):
    conn = mydb.connect(
        host='localhost',
        port='3306',
        user='root',
        password='BTcfrLkK1FFU',
        database='blackjack'
    )

    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"INSERT IGNORE INTO users VALUES ('{ip_address}', 'Anonymous', '0', '0', './static/img/anonymous.png')")
    conn.commit()
    cursor.close()


# 勝利した場合の処理を行います
def update_score_win(ip_address, additional):
    conn = mydb.connect(
        host='localhost',
        port='3306',
        user='root',
        password='BTcfrLkK1FFU',
        database='blackjack'
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM users WHERE ip_address = '{ip_address}'")

    user = cursor.fetchone()
    streak = int(user["streak"])
    final_additional = int(additional * (1 + streak / 10))  # 倍率設定

    cursor.execute(
        f"UPDATE users SET score = (score + {final_additional}), streak = streak + 1 WHERE ip_address = '{ip_address}'")
    conn.commit()
    cursor.close()
    conn.close()


# 引き分け・敗北した場合の処理を行います
def update_score_draw_or_lose(ip_address, additional):
    conn = mydb.connect(
        host='localhost',
        port='3306',
        user='root',
        password='BTcfrLkK1FFU',
        database='blackjack'
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute(f"UPDATE users SET score = (score + {additional}), streak = 0 WHERE ip_address = '{ip_address}'")
    conn.commit()
    cursor.close()
    conn.close()


# クライアントへの時間送信
def main(client, client_no):
    host = socket.gethostname()
    print(f"host: {host}")

    ip_address = socket.gethostbyname(host)
    print(f"ip_address: {ip_address}")

    create_user_data(ip_address)
    send_welcome_message(client)

    deck = reset_deck()

    dictionary[f"server_{client_no}"] = 0
    dictionary[f"client_{client_no}"] = 0

    send_data = f"Your Client Number: {client_no}"
    client.send(send_data.encode("utf-8"))

    # Client のターン
    while True:
        send_data = f"""
Your Hand Total: \u001b[31m{dictionary[f'client_{client_no}']}\u001b[0m\n
[*] HIT [H] or STAND [S] ?
"""
        client.send(send_data.encode("utf-8"))

        recv_data = client.recv(BUFFER_SIZE).decode("utf-8")

        if recv_data in "H":
            r = random.randint(0, len(deck) - 1)  # 山札
            hit = deck.pop(r)  # カードを1枚山札からランダムに引く
            hit_number = hit[1:]  # スートを取り除く

            send_data = f"You HIT: {hit}\n"
            client.send(send_data.encode("utf-8"))

            if hit_number == "A":
                while True:
                    send_data = "[*] Please choose \u001b[31m1\u001b[0m or \u001b[31m11\u001b[0m.\n"
                    client.send(send_data.encode())

                    recv_data = client.recv(BUFFER_SIZE).decode("utf-8")
                    try:
                        add = int(recv_data)

                        if add != 1 and add != 11:
                            add = 11  # 1 か 11 じゃなければ強制的に 11

                        break
                    except ValueError:
                        send_data = "Invalid number.\n"
                        client.send(send_data.encode())
            elif hit_number == "J" or hit_number == "Q" or hit_number == "K":
                add = 10
            else:
                add = int(hit_number)

            # カードを1枚取り出して数を追加
            dictionary[f"client_{client_no}"] += add

            # Bust
            if dictionary[f"client_{client_no}"] >= 22:
                send_data = f"You are Bust..."
                client.send(send_data.encode("utf-8"))

                break

        if recv_data in "S":
            data = f"You chose STAND, now Server Side Turn\n"
            client.send(data.encode("utf-8"))
            break

        if recv_data == "[EOF]":
            client.close()

    # Server のターン
    while True:
        print(f"""
Your Hand Total: \u001b[31m{dictionary[f'server_{client_no}']}\u001b[0m\n
[*] Hit [H] or Stand [S] ?
""")

        if dictionary[f'server_{client_no}'] <= 16:
            print("Your Hand Total is less than 17, Press [H] to HIT.")
            answer = input("> ")

            r = random.randint(0, len(deck) - 1)  # 山札
            hit = deck.pop(r)  # カードを1枚山札からランダムに引く
            hit_number = hit[1:]  # スートを取り除く

            print(f"You HIT: {hit}\n")

            if hit_number == "A":
                while True:
                    print("[*] Please choose \u001b[31m1\u001b[0m or \u001b[31m11\u001b[0m.\n")

                    answer = input("> ")

                    try:
                        add = int(answer)

                        if add != 1 and add != 11:
                            add = 11  # 1 か 11 じゃなければ強制的に 11

                        break
                    except ValueError:
                        print("Invalid number.\n")
            elif hit_number == "J" or hit_number == "Q" or hit_number == "K":
                add = 10
            else:
                add = int(hit_number)

            # カードを1枚取り出して数を追加
            dictionary[f"server_{client_no}"] += add

            # Bust
            if dictionary[f"server_{client_no}"] >= 22:
                print(f"You are Bust...")

                break
        else:
            print("Your Hand Total is greater than 16, Press [S] to STAND.")

            input("> ")

            break

        if recv_data == "[EOF]":
            client.close()

    c_total = dictionary[f'client_{client_no}']
    s_total = dictionary[f'server_{client_no}']

    result_text = f"""
==========[ RESULT ]==========

Client: {c_total}
Server: {s_total}

==============================
"""

    print(result_text)
    client.send(result_text.encode("utf-8"))

    # 勝敗判定
    if c_total <= 21:  # C が21以下ならば
        if s_total <= 21:  # S が21以下ならば
            if c_total > s_total:  # C の勝利
                print(lose_message)
                client.send(win_message.encode("utf-8"))
                update_score_win(ip_address, 50)
            elif c_total < s_total:  # S の勝利
                print(win_message)
                client.send(lose_message.encode("utf-8"))
                update_score_draw_or_lose(ip_address, -10)
            else:  # 引き分け
                print(draw_message)
                client.send(draw_message.encode("utf-8"))
                update_score_draw_or_lose(ip_address, 3)
        else:  # S が Bust ならば C の勝利
            print(lose_message)
            client.send(win_message.encode("utf-8"))
            update_score_win(ip_address, 50)
    else:  # C が Bust したならば
        if s_total <= 21:  # S が21以下ならば S の勝利
            print(win_message)
            client.send(lose_message.encode("utf-8"))
            update_score_draw_or_lose(ip_address, -10)
        else:  # S が Bust ならば引き分け
            print(draw_message)
            client.send(draw_message.encode("utf-8"))
            update_score_draw_or_lose(ip_address, 3)

    in_game = False  # ゲーム中のフラグを解除

    send_data = f"[EOF]"
    client.send(send_data.encode("utf-8"))

    client.close()


def busy(client, client_no):
    data = "The server is in a match. Please try later."
    client.send(data.encode("utf-8"))
    client.close()


# メイン
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", PORT))
server.listen(0)

while True:
    client_no += 1
    client, addr = server.accept()

    if in_game == False:
        # スレッド
        p = threading.Thread(target=main, args=(client, client_no))
        p.start()
    else:
        # スレッド
        p = threading.Thread(target=busy, args=(client, client_no))
        p.start()

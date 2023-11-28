from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector as mydb
import base64
from PIL import Image
from io import BytesIO


app = Flask(__name__)

# Set Secret Key
app.secret_key = "11451419114514191145141911451419"

conn = mydb.connect(
    host="localhost",
    port=3306,
    user="root",
    password="BTcfrLkK1FFU",
    database="blackjack"
)

conn.ping(reconnect=True)
print(conn.is_connected())


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/navbar")
def navbar():
    return render_template("navbar.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    method = request.method

    if method == "GET":
        return render_template("login.html")
    elif method == "POST":
        form = request.form

        ip_address = request.remote_addr
        username = form.get("username")

        select_sql = f"SELECT * FROM users WHERE ip_address = '{ip_address}'"

        # sql = f"INSERT INTO users (`email`, `username`, `score`, `streak`, `avatar`) VALUES ('{email}', '{username}', '0', '0', NULL) ON DUPLICATE KEY UPDATE `username` = VALUES(username)"

        cur = conn.cursor(dictionary=True)

        print(select_sql)
        cur.execute(select_sql)

        # ユーザーが存在するならば
        if cur.fetchone():
            cur.execute(f"UPDATE users SET username = '{username}' WHERE ip_address = '{ip_address}'")
        else:  # 存在しないならば
            print(f"INSERT INTO users (ip_address, username, score, streak, avatar) VALUES ('{ip_address}', '{username}', 0, 0, NULL)")
            cur.execute(f"INSERT INTO users (ip_address, username, score, streak, avatar) VALUES ('{ip_address}', '{username}', 0, 0, NULL)")

        session["loggedin"] = True
        session["username"] = username
        msg = "ログインに成功しました"

        conn.commit()
        cur.close()

        return render_template("index.html", msg=msg, level="success")


@app.route("/leaderboard")
def leaderboard():
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, score, streak, avatar FROM users ORDER BY score DESC")
    users = cursor.fetchall()

    return render_template("leaderboard.html", users=users)


@app.route("/settings", methods=["GET", "POST"])
def settings():
    method = request.method

    if method == "GET":
        return render_template("settings.html", msg="", level="success")
    elif method == "POST":
        form = request.form

        ip_address = request.remote_addr
        username = form.get("username")
        avatar = "./static/img/anonymous.png"

        if 'avatar' in request.files:
            image_file = request.files['avatar']

            if image_file.filename != '':
                img = Image.open(image_file)
                img_resized = img.resize((48, 48))

                buffered = BytesIO()
                img_resized.save(buffered, format="PNG")
                base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

                avatar = f"data:image/png;base64,{base64_image}"

                # ここでbase64形式のデータを使って何かしらの処理を行うことができます
                # print(avatar)

        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"UPDATE users SET username = '{username}', avatar = '{avatar}' WHERE ip_address = '{ip_address}'")
        conn.commit()
        cursor.close()

        return render_template("settings.html", msg="設定の変更に成功しました", level="success")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
from flask import Flask, render_template, request, session
import mysql.connector as mydb
import base64
from PIL import Image
from io import BytesIO


app = Flask(__name__)

# Set Secret Key
app.secret_key = "12345678901234567890123456789012"


@app.route("/")
@app.route("/index")
def index():
    ip_address = request.remote_addr

    try:
        username = session["username"]

        conn = mydb.connect(
            host="localhost",
            port=3306,
            user="root",
            password="BTcfrLkK1FFU",
            database="blackjack"
        )

        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM users WHERE ip_address = '{ip_address}'")
        user = cursor.fetchone()

        return render_template("index.html", user=user)
    except KeyError:
        return render_template("index.html")


@app.route("/navbar")
def navbar():
    ip_address = request.remote_addr

    try:
        username = session["username"]

        conn = mydb.connect(
            host="localhost",
            port=3306,
            user="root",
            password="BTcfrLkK1FFU",
            database="blackjack"
        )

        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM users WHERE ip_address = '{ip_address}'")
        user = cursor.fetchone()

        return render_template("navbar.html", avatar=user["avatar"])
    except KeyError:
        return render_template("navbar.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    conn = mydb.connect(
        host="localhost",
        port=3306,
        user="root",
        password="BTcfrLkK1FFU",
        database="blackjack"
    )

    method = request.method

    if method == "GET":
        return render_template("login.html")
    elif method == "POST":
        form = request.form

        ip_address = request.remote_addr
        username = form.get("username")

        select_sql = f"SELECT * FROM users WHERE ip_address = '{ip_address}'"

        # sql = f"INSERT INTO users (`email`, `username`, `score`, `streak`, `avatar`) VALUES ('{email}', '{username}', '0', '0', NULL) ON DUPLICATE KEY UPDATE `username` = VALUES(username)"

        cursor = conn.cursor(dictionary=True)

        print(select_sql)
        cursor.execute(select_sql)

        # ユーザーが存在するならば
        if cursor.fetchone():
            cursor.execute(f"UPDATE users SET username = '{username}' WHERE ip_address = '{ip_address}'")
        else:  # 存在しないならば
            print(f"INSERT INTO users (ip_address, username, score, streak, avatar) VALUES ('{ip_address}', '{username}', '0', '0', '/static/img/anonymous.png')")
            cursor.execute(f"INSERT INTO users (ip_address, username, score, streak, avatar) VALUES ('{ip_address}', '{username}', '0', '0', '/static/img/anonymous.png')")

        session["loggedin"] = True
        session["username"] = username
        msg = "ログインに成功しました"

        cursor.execute(f"SELECT * FROM users WHERE ip_address = '{ip_address}'")
        user = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return render_template("index.html", user=user, msg=msg, level="success")


@app.route("/logout")
def logout():
    session["loggedin"] = False
    session["username"] = ""
    msg = "ログアウトしました"

    return render_template("index.html", msg=msg, level="success")


@app.route("/leaderboard")
def leaderboard():
    conn = mydb.connect(
        host="localhost",
        port=3306,
        user="root",
        password="BTcfrLkK1FFU",
        database="blackjack"
    )

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, score, streak, avatar FROM users ORDER BY score DESC")
    users = cursor.fetchall()

    return render_template("leaderboard.html", users=users)


@app.route("/settings", methods=["GET", "POST"])
def settings():
    conn = mydb.connect(
        host="localhost",
        port=3306,
        user="root",
        password="BTcfrLkK1FFU",
        database="blackjack"
    )

    method = request.method

    if method == "GET":
        return render_template("settings.html", msg="", level="success")
    elif method == "POST":
        form = request.form

        ip_address = request.remote_addr
        username = form.get("username")
        avatar = "/static/img/anonymous.png"

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
        conn.close()


        return render_template("settings.html", msg="設定の変更に成功しました", level="success")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

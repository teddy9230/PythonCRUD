from flask import Flask, request, session, redirect, url_for, render_template
from flaskext.mysql import MySQL
import pymysql
import re


app = Flask(__name__)

app.secret_key = "cairocoders-ednalan"


mysql = MySQL()

# 修改這裡
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = "password"
app.config["MYSQL_DATABASE_DB"] = "pythonNasdb"
app.config["MYSQL_DATABASE_HOST"] = "localhost"


mysql.init_app(app)


@app.route("/pythonlogin/", methods=["GET", "POST"])
def login():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    msg = ""

    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM accounts WHERE username = %s AND password = %s",
            (username, password),
        )

        account = cursor.fetchone()

        if account:
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]

            return redirect(url_for("home"))
        else:
            msg = "帳號 或 密碼 有錯誤 請重新輸入!"

    return render_template("index.html", msg=msg)


@app.route("/register", methods=["GET", "POST"])
def register():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    msg = ""

    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
    ):
        fullname = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        cursor.execute("SELECT * FROM accounts WHERE username = %s", (username))
        account = cursor.fetchone()
        if account:
            msg = "此 會員 已被註冊!"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "此 信箱 已被註冊!"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "只能包含字符和數字!"
        elif not username or not password or not email:
            msg = "請優先登入!"
        else:
            cursor.execute(
                "INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s)",
                (fullname, username, password, email),
            )
            conn.commit()

            msg = "會員註冊成功!"
    elif request.method == "POST":
        msg = "請優先登入!"

    return render_template("register.html", msg=msg)


@app.route("/")
def home():
    if "loggedin" in session:
        return render_template("home.html", username=session["username"])

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)

    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if "loggedin" in session:
        cursor.execute("SELECT * FROM accounts WHERE id = %s", [session["id"]])
        account = cursor.fetchone()

        return render_template("profile.html", account=account)

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)

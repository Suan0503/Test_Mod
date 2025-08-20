import re
import psycopg2
import psycopg2.extras
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template, flash

app = Flask(__name__)
app.secret_key = "change-me-please"

PG_URL = "postgresql://postgres:JRmQnieaMhLmlDiJmcQCfcGpQXPahcfX@shuttle.proxy.rlwy.net:20364/railway"

def get_conn():
    return psycopg2.connect(PG_URL)

def normalize_phone(s: str) -> str:
    if not s: return ""
    digits = re.sub(r"\D", "", s)
    digits = re.sub(r"^(886|00886|000886)", "", digits)
    if digits.startswith("9") and len(digits) == 9:
        digits = "0" + digits
    return digits

@app.route("/")
def home():
    return redirect(url_for("search"))

# 查詢 records 主表
@app.route("/search", methods=["GET", "POST"])
def search():
    phone = ""
    rows = []
    columns = []
    searched = False
    if request.method == "POST":
        phone = normalize_phone(request.form.get("phone", ""))
        searched = True
        conn = get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if phone:
            c.execute("SELECT * FROM records WHERE phone = %s ORDER BY updated_at DESC", (phone,))
        else:
            c.execute("SELECT * FROM records ORDER BY updated_at DESC")
        rows = c.fetchall()
        columns = [desc.name for desc in c.description]
        conn.close()
    return render_template("search.html", phone=phone, rows=rows, columns=columns, searched=searched, active="search", now=datetime.now())

# 白名單總覽
@app.route("/white_list")
def white_list():
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT * FROM whitelist ORDER BY created_at DESC")
    rows = c.fetchall()
    columns = [desc.name for desc in c.description]
    conn.close()
    return render_template("white_list.html", rows=rows, columns=columns, active="white", now=datetime.now())

# 黑名單總覽
@app.route("/black_list")
def black_list():
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT * FROM blacklist ORDER BY created_at DESC")
    rows = c.fetchall()
    columns = [desc.name for desc in c.description]
    conn.close()
    return render_template("black_list.html", rows=rows, columns=columns, active="black", now=datetime.now())

# 新增白名單（同步寫入 records 及 whitelist）
@app.route("/add_white", methods=["GET", "POST"])
def add_white():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = normalize_phone(request.form.get("phone", ""))
        line_id = request.form.get("line_id", "").strip()
        reason = request.form.get("reason", "").strip()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not name or not phone:
            flash("姓名/電話為必填")
        else:
            conn = get_conn()
            c = conn.cursor()
            c.execute("""
                INSERT INTO records (name, phone, line_id, type, reason, operator, created_at, updated_at)
                VALUES (%s, %s, %s, 'white', %s, '', %s, %s)
            """, (name, phone, line_id, reason, now, now))
            c.execute("""
                INSERT INTO whitelist (name, phone, line_id, reason, operator, created_at, updated_at)
                VALUES (%s, %s, %s, %s, '', %s, %s)
            """, (name, phone, line_id, reason, now, now))
            conn.commit()
            conn.close()
            flash("新增成功！")
            return redirect(url_for("white_list"))
    return render_template("add_white.html", active="addwhite", now=datetime.now())

# 新增黑名單（同步寫入 records 及 blacklist）
@app.route("/add_black", methods=["GET", "POST"])
def add_black():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = normalize_phone(request.form.get("phone", ""))
        line_id = request.form.get("line_id", "").strip()
        reason = request.form.get("reason", "").strip()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not name or not phone:
            flash("姓名/電話為必填")
        else:
            conn = get_conn()
            c = conn.cursor()
            c.execute("""
                INSERT INTO records (name, phone, line_id, type, reason, operator, created_at, updated_at)
                VALUES (%s, %s, %s, 'black', %s, '', %s, %s)
            """, (name, phone, line_id, reason, now, now))
            c.execute("""
                INSERT INTO blacklist (name, phone, line_id, reason, operator, created_at, updated_at)
                VALUES (%s, %s, %s, %s, '', %s, %s)
            """, (name, phone, line_id, reason, now, now))
            conn.commit()
            conn.close()
            flash("新增成功！")
            return redirect(url_for("black_list"))
    return render_template("add_black.html", active="addblack", now=datetime.now())

if __name__ == "__main__":
    app.run(debug=True)

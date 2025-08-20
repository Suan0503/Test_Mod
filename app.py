import os, re, sqlite3
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template, flash

app = Flask(__name__)
app.secret_key = "change-me-please"

DB_PATH = os.path.join(os.path.dirname(__file__), "md_checker.db")
if not os.access(os.path.dirname(DB_PATH), os.W_OK):
    DB_PATH = "/tmp/md_checker.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # 主資料表
    c.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            line_id TEXT,
            type TEXT NOT NULL CHECK (type IN ('white','black')),
            reason TEXT,
            operator TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_records_phone ON records(phone)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_records_type ON records(type)")
    # 白名單表
    c.execute("""
        CREATE TABLE IF NOT EXISTS whitelist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            line_id TEXT,
            reason TEXT,
            operator TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_whitelist_phone ON whitelist(phone)")
    # 黑名單表
    c.execute("""
        CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            line_id TEXT,
            reason TEXT,
            operator TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_blacklist_phone ON blacklist(phone)")
    conn.commit()
    conn.close()

init_db()

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
        c = conn.cursor()
        if phone:
            rows = c.execute("SELECT * FROM records WHERE phone = ? ORDER BY updated_at DESC", (phone,)).fetchall()
        else:
            rows = c.execute("SELECT * FROM records ORDER BY updated_at DESC").fetchall()
        columns = [desc[0] for desc in c.description]
        conn.close()
    return render_template("search.html", phone=phone, rows=rows, columns=columns, searched=searched, active="search", now=datetime.now())

# 白名單總覽
@app.route("/white_list")
def white_list():
    conn = get_conn()
    c = conn.cursor()
    rows = c.execute("SELECT * FROM whitelist ORDER BY created_at DESC").fetchall()
    columns = [desc[0] for desc in c.description]
    conn.close()
    return render_template("white_list.html", rows=rows, columns=columns, active="white", now=datetime.now())

# 黑名單總覽
@app.route("/black_list")
def black_list():
    conn = get_conn()
    c = conn.cursor()
    rows = c.execute("SELECT * FROM blacklist ORDER BY created_at DESC").fetchall()
    columns = [desc[0] for desc in c.description]
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
                VALUES (?, ?, ?, 'white', ?, '', ?, ?)
            """, (name, phone, line_id, reason, now, now))
            c.execute("""
                INSERT INTO whitelist (name, phone, line_id, reason, operator, created_at, updated_at)
                VALUES (?, ?, ?, ?, '', ?, ?)
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
                VALUES (?, ?, ?, 'black', ?, '', ?, ?)
            """, (name, phone, line_id, reason, now, now))
            c.execute("""
                INSERT INTO blacklist (name, phone, line_id, reason, operator, created_at, updated_at)
                VALUES (?, ?, ?, ?, '', ?, ?)
            """, (name, phone, line_id, reason, now, now))
            conn.commit()
            conn.close()
            flash("新增成功！")
            return redirect(url_for("black_list"))
    return render_template("add_black.html", active="addblack", now=datetime.now())

if __name__ == "__main__":
    app.run(debug=True)

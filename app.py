import os
import re
import sqlite3
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template, flash

APP_TITLE = "茗殿專用查詢系統"
DB_PATH = os.path.join(os.path.dirname(__file__), "md_checker.db")

app = Flask(__name__)
app.secret_key = "change-me-please"  # 記得換掉呦～

# ---------- 資料庫初始化 ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
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
    conn.commit()
    conn.close()

def normalize_phone(s: str) -> str:
    """只保留數字；09…或+8869…都轉成0912…格式"""
    if not s:
        return ""
    digits = re.sub(r"\D", "", s)
    digits = re.sub(r"^(886|00886|000886)", "", digits)
    if digits.startswith("9") and len(digits) == 9:
        digits = "0" + digits
    return digits

def validate_type(t: str) -> bool:
    return t in ("white", "black")

# ---------- 路由：前台查詢 ----------
@app.route("/", methods=["GET", "POST"])
def index():
    phone = ""
    search_result = []
    searched = False

    if request.method == "POST":
        phone = normalize_phone(request.form.get("phone", ""))
        searched = True
        if phone:
            conn = get_conn()
            c = conn.cursor()
            c.execute("SELECT * FROM records WHERE phone = ? ORDER BY updated_at DESC", (phone,))
            rows = c.fetchall()
            conn.close()
            for r in rows:
                search_result.append({
                    "type": r["type"],
                    "record": {
                        "name": r["name"],
                        "phone": r["phone"],
                        "line_id": r["line_id"],
                        "reason": r["reason"],
                        "created_at": r["created_at"],
                        "updated_at": r["updated_at"],
                    }
                })
        else:
            flash("請輸入電話～")
    return render_template("search.html", phone=phone, search_result=search_result, searched=searched, now=datetime.now())

# ---------- 啟動 ----------
if __name__ == "__main__":
    init_db()
    # 預先塞一兩筆示範資料（若資料表為空）
    conn = get_conn()
    cur = conn.cursor()
    count = cur.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    if count == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        demo = [
            ("小白", "0912345678", "white_user", "white", "熟客", "小幫手糖糖", now, now),
            ("小黑", "0987654321", None, "black", "曾經放鳥", "小幫手糖糖", now, now),
        ]
        cur.executemany("""
            INSERT INTO records (name, phone, line_id, type, reason, operator, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, demo)
        conn.commit()
    conn.close()

    app.run(debug=True)

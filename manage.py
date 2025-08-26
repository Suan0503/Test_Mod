<<<<<<< HEAD
"""
管理腳本：建立資料表
"""
=======
# 簡易管理腳本：建立資料表
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
import os
from app import app
from extensions import db

<<<<<<< HEAD

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("資料表已建立 (如尚未建立)。")
=======
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("資料表已建立 (如果尚未建立)。")
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde

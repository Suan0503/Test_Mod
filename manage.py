# 簡易管理腳本：建立資料表
import os
from app import app
from extensions import db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("資料表已建立 (如果尚未建立)。")

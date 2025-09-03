#!/bin/sh
echo "[INFO] 執行資料庫升級..."
flask db upgrade
echo "[INFO] 啟動 Gunicorn..."
exec gunicorn app:app -b 0.0.0.0:8080

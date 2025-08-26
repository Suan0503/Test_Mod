```markdown
# 名單管理模組（白名單 / 黑名單） - 安裝與使用說明

新增了以下檔案（放入 repo）：
- extensions.py
- models/whitelist.py
- models/blacklist.py
- routes/list_admin.py
- templates/admin/index.html
- templates/admin/whitelist_form.html
- templates/admin/blacklist_form.html
- manage.py
(改動) app.py：註冊了 list_admin blueprint，並預設 sqlite db 位置 fallback

快速上手：
1. 安裝套件
   pip install -r requirements.txt
   （至少需要 flask, flask_sqlalchemy, python-dotenv）

2. 設定環境變數（可選）
   - DATABASE_URL: (Postgres 或 sqlite)
   - SECRET_KEY: Flask session 用

3. 建表
   python manage.py

4. 啟動
   python app.py

到瀏覽器查看： http://localhost:5000/admin/list

操作說明：
- 新增黑名單時，若 identifier 在白名單中，會自動把該白名單移除並新增黑名單（轉移）。
- 若要反向把黑名單轉為白名單，請先在黑名單中刪除，然後新增白名單或擴充一個「轉移回白名單」按鈕。
- 可在 index 的搜尋欄輸入 identifier / name / phone / email 做模糊搜尋。

可擴充：
- 權限 (Flask-Login) 限制管理介面
- 批次匯入 / 匯出 (CSV)
- 操作日誌（誰做了新增/修改/刪除）
- REST API endpoints（JSON），提供給其他服務查詢
```

from flask import Blueprint, render_template, request, redirect, url_for
from utils.schedule_sync import get_schedule_from_google
import gspread
from oauth2client.service_account import ServiceAccountCredentials

bp = Blueprint('schedule', __name__)

# 取得妹妹名單（可根據 Google Sheets 班表欄位自動整理）
def get_sisters():
    schedule = get_schedule_from_google()
    names = set(row.get('妹妹') for row in schedule if row.get('妹妹'))
    return sorted(names)

@bp.route('/schedule', methods=['GET'])
def schedule():
    schedule_data = get_schedule_from_google()
    sisters = get_sisters()
    return render_template('schedule.html', schedule=schedule_data, sisters=sisters)

@bp.route('/schedule/add', methods=['POST'])
def add_schedule():
    sister = request.form['sister']
    hour = request.form['hour']
    minute = request.form['minute']
    plan = request.form['plan']
    time_str = f"{hour}:{minute}"
    # 寫入 Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('你的Google文件名稱').sheet1  # 請改成你的 Google Sheets 名稱
    sheet.append_row([sister, time_str, plan])
    return redirect(url_for('schedule.schedule'))

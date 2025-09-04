import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_schedule_from_google():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('當日 預約表').sheet1  # 請改成你的 Google Sheets 名稱
    return sheet.get_all_records()

# 用於暫存用戶驗證流程狀態
_temp_users = {}

def get_temp_user(user_id):
    return _temp_users.get(user_id)

def set_temp_user(user_id, data):
    _temp_users[user_id] = data

def clear_temp_user(user_id):
    _temp_users.pop(user_id, None)

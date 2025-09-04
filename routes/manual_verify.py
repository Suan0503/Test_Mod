
from flask import Blueprint, render_template, request, session, redirect, url_for
from models import Whitelist
from extensions import db
import secrets
from datetime import datetime

bp = Blueprint('manual_verify', __name__)

@bp.route('/manual_verify', methods=['GET', 'POST'])
def manual_verify():
    code = None
    success = False
    error = None
    # 第一步：填表產生驗證碼
    if request.method == 'POST' and 'nickname' in request.form:
        nickname = request.form['nickname']
        phone = request.form['phone']
        line_id = request.form['line_id']
        code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
        session['manual_verify'] = {
            'nickname': nickname,
            'phone': phone,
            'line_id': line_id,
            'code': code
        }
        return render_template('manual_verify.html', code=code)
    # 第二步：輸入驗證碼
    if request.method == 'POST' and 'input_code' in request.form:
        input_code = request.form['input_code']
        data = session.get('manual_verify')
        if data and input_code == data['code']:
            wl = Whitelist()
            wl.name = data.get('nickname')
            wl.phone = data.get('phone')
            wl.line_id = data.get('line_id')
            wl.line_user_id = 'manual_verify'
            db.session.add(wl)
            db.session.commit()
            success = True
            session.pop('manual_verify', None)
            return render_template('manual_verify.html', success=success)
        else:
            code = data['code'] if data else None
            error = '驗證碼錯誤，請重新輸入'
            return render_template('manual_verify.html', code=code, error=error)
    return render_template('manual_verify.html')

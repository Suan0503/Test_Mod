# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash

schedule_bp = Blueprint('schedule', __name__)

# 假設時段和妹妹選項暫時硬編碼
TIME_SLOTS = ['早班', '午班', '晚班']
GIRLS = ['小美', '小芳', '小玲']

@schedule_bp.route('/schedule', methods=['GET', 'POST'])
def schedule():
	if request.method == 'POST':
		new_girl = request.form.get('new_girl')
		time = request.form.get('time')
		girl = request.form.get('girl')
		amount = request.form.get('amount')
		plan = request.form.get('plan')
		# 新增妹妹（如果有填寫）
		if new_girl and new_girl.strip():
			if new_girl not in GIRLS:
				GIRLS.append(new_girl.strip())
			girl = new_girl.strip()
		# 這裡可以加上資料庫儲存或其他邏輯
		flash(f'已提交：妹妹={girl}, 時間={time}, 金額={amount}, 方案={plan}', 'success')
		return redirect(url_for('schedule.schedule'))
	return render_template('schedule.html', girls=GIRLS)

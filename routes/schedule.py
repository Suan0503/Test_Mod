# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

schedule_bp = Blueprint('schedule', __name__)


# 假設時段和妹妹選項暫時硬編碼
GIRLS = ['小美', '小芳', '小玲']
# 暫存班表資料
SCHEDULE = []


@schedule_bp.route('/schedule', methods=['GET', 'POST'])
@login_required
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
		# 新增到班表
		SCHEDULE.append({
			'girl': girl,
			'time': time,
			'amount': amount,
			'plan': plan
		})
		flash(f'已提交：妹妹={girl}, 時間={time}, 金額={amount}, 方案={plan}', 'success')
		return redirect(url_for('schedule.schedule'))
	return render_template('schedule.html', girls=GIRLS, schedule=SCHEDULE, user=current_user)

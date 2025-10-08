from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('登入成功', 'success')
            return redirect(url_for('schedule.schedule'))
        else:
            flash('帳號或密碼錯誤', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已登出', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')
        if User.query.filter_by(username=username).first():
            flash('帳號已存在', 'danger')
        else:
            pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(username=username, password_hash=pw_hash, role=role)
            db.session.add(user)
            db.session.commit()
            flash('註冊成功，請登入', 'success')
            return redirect(url_for('auth.login'))
    return render_template('register.html')

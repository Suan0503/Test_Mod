from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'supersecret')
db = SQLAlchemy(app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin'] = admin.username
            flash('登入成功！')
            return redirect(url_for('admin'))
        else:
            flash('帳號或密碼錯誤')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('已登出')
    return redirect(url_for('login'))

@app.before_request
def require_login():
    if request.endpoint in ['admin', 'add', 'edit', 'delete'] and 'admin' not in session:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import csv
from io import StringIO, BytesIO
from sqlalchemy import or_
from flask_sqlalchemy import SQLAlchemy
from extensions import db
from models import Whitelist, Blacklist
from models.operation_log import OperationLog
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'supersecret')
db.init_app(app)

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
    protected = ['admin', 'add', 'edit', 'delete', 'import_csv', 'export']
    if request.endpoint in protected and 'admin' not in session:
        return redirect(url_for('login'))



def get_model_columns(Model):
    # SQLAlchemy: 取得 Model 欄位名稱
    return [c.key for c in Model.__table__.columns]

@app.route('/admin/export', methods=['POST'])
def export():
    query_type = request.form.get('type', 'whitelist')
    Model = Whitelist if query_type == 'whitelist' else Blacklist
    entries = Model.query.all()
    si = StringIO()
    columns = get_model_columns(Model)
    writer = csv.writer(si)
    writer.writerow(columns)
    for e in entries:
        writer.writerow([getattr(e, col, '') for col in columns])
    output = si.getvalue().encode('utf-8')
    return send_file(BytesIO(output), mimetype='text/csv', as_attachment=True, download_name=f'{query_type}_export.csv')

@app.route('/admin/import', methods=['POST'])
def import_csv():
    query_type = request.form.get('type', 'whitelist')
    Model = Whitelist if query_type == 'whitelist' else Blacklist
    file = request.files['csvfile']
    reader = csv.DictReader(StringIO(file.stream.read().decode('utf-8')))
    count = 0
    columns = get_model_columns(Model)
    for row in reader:
        entry = Model()
        for col in columns:
            if col in row:
                setattr(entry, col, row[col])
        db.session.add(entry)
        count += 1
    db.session.commit()
    flash(f'成功匯入 {count} 筆資料！')
    return redirect(url_for('admin'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    query_type = request.form.get('type', 'whitelist') if request.method == 'POST' else request.args.get('type', 'whitelist')
    phone = request.form.get('phone', '').strip() if request.method == 'POST' else request.args.get('phone', '').strip()
    line_id = request.form.get('line_id', '').strip() if request.method == 'POST' else request.args.get('line_id', '').strip()
    name = request.form.get('name', '').strip() if request.method == 'POST' else request.args.get('name', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 10
    results = []
    total = 0
    Model = Whitelist if query_type == 'whitelist' else Blacklist
    q = Model.query
    # 模糊搜尋
    if phone:
        q = q.filter(Model.phone.like(f"%{phone}%"))
    if line_id and hasattr(Model, 'line_id'):
        col = getattr(Model, 'line_id', None)
        if col is not None:
            q = q.filter(col.like(f"%{line_id}%"))
    if name:
        q = q.filter(Model.name.like(f"%{name}%"))
    total = q.count()
    results = q.order_by(Model.id.desc()).offset((page-1)*per_page).limit(per_page).all()
    return render_template('admin_panel.html', results=results, query_type=query_type, page=page, per_page=per_page, total=total)

@app.route('/admin/add', methods=['GET', 'POST'])
def add():
    entry_type = request.args.get('type', 'whitelist')
    Model = Whitelist if entry_type == 'whitelist' else Blacklist
    if request.method == 'POST':
        data = {k: v for k, v in request.form.items()}
        entry = Model(**data)
        db.session.add(entry)
        db.session.commit()
        flash(f'{entry_type.title()} 新增成功！')
        return redirect(url_for('admin'))
    return render_template('admin_add.html', entry_type=entry_type)

@app.route('/admin/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit(entry_id):
    entry_type = request.args.get('type', 'whitelist')
    Model = Whitelist if entry_type == 'whitelist' else Blacklist
    entry = Model.query.get_or_404(entry_id)
    if request.method == 'POST':
        for k, v in request.form.items():
            setattr(entry, k, v)
        db.session.commit()
        flash(f'{entry_type.title()} 修改成功！')
        return redirect(url_for('admin'))
    return render_template('admin_edit.html', entry=entry, entry_type=entry_type)

@app.route('/admin/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
    entry_type = request.form.get('type', 'whitelist')
    Model = Whitelist if entry_type == 'whitelist' else Blacklist
    entry = Model.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash(f'{entry_type.title()} 刪除成功！')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from werkzeug.security import generate_password_hash
        if not Admin.query.filter_by(username='admin').first():
            admin_obj = Admin()
            admin_obj.username = 'admin'
            admin_obj.password_hash = generate_password_hash('ming666', method='pbkdf2:sha256')
            db.session.add(admin_obj)
            db.session.commit()
    app.run(debug=True)

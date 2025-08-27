from admin_auth import db, Admin
from werkzeug.security import generate_password_hash

def create_admin():
    db.create_all()
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', password_hash=generate_password_hash('ming666'))
        db.session.add(admin)
        db.session.commit()
        print('管理員帳號已建立')
    else:
        print('管理員帳號已存在')

if __name__ == '__main__':
    create_admin()

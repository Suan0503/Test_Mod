
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import Whitelist, Blacklist, Coupon
from extensions import db

def init_admin(app):
    admin = Admin(app, name='後台管理', template_mode='bootstrap3')
    admin.add_view(ModelView(Whitelist, db.session))
    admin.add_view(ModelView(Blacklist, db.session))
    admin.add_view(ModelView(Coupon, db.session))
    return admin

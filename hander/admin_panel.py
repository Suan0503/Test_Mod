
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import Whitelist, Blacklist, Coupon
from extensions import db


from flask_admin import helpers as admin_helpers


class ModernModelView(ModelView):
    create_modal = True
    edit_modal = True
    can_view_details = True
    column_display_pk = True
    page_size = 20
    def render(self, template, **kwargs):
        if 'admin_custom_css' not in kwargs:
            kwargs['admin_custom_css'] = '/static/admin_custom.css'
        return super().render(template, **kwargs)


class WhitelistModelView(ModernModelView):
    column_searchable_list = ['phone', 'line_id', 'name']

class BlacklistModelView(ModernModelView):
    column_searchable_list = ['phone', 'name']  # 根據 Blacklist 欄位

class CouponModelView(ModernModelView):
    column_searchable_list = ['line_user_id', 'report_no', 'type', 'date']  # 依 models.py 實際欄位

def init_admin(app):
    admin = Admin(app, name='後台管理', template_mode='bootstrap4', base_template='admin_custom_master.html')
    admin.add_view(WhitelistModelView(Whitelist, db.session, name='<i class="fa fa-list"></i> 白名單', endpoint='whitelist'))
    admin.add_view(BlacklistModelView(Blacklist, db.session, name='<i class="fa fa-ban"></i> 黑名單', endpoint='blacklist'))
    admin.add_view(CouponModelView(Coupon, db.session, name='<i class="fa fa-ticket"></i> 抽獎券', endpoint='coupon'))
    # 確保自訂 CSS 被載入
    @app.context_processor
    def override_admin_css():
        return dict(admin_custom_css='/static/admin_custom.css')
    return admin

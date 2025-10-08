from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Whitelist
from extensions import db

whitelist_bp = Blueprint('whitelist_page', __name__)

@whitelist_bp.route('/whitelist', methods=['GET'])
@login_required
def whitelist_list():
    whitelists = Whitelist.query.order_by(Whitelist.created_at.desc()).all()
    return render_template('whitelist_list.html', whitelists=whitelists)

@whitelist_bp.route('/whitelist/delete/', methods=['POST'])
@login_required
def whitelist_delete():
    wid = request.form.get('id')
    w = Whitelist.query.get(wid)
    if w:
        db.session.delete(w)
        db.session.commit()
        flash('已移除白名單', 'success')
    else:
        flash('找不到該白名單', 'danger')
    return redirect(url_for('whitelist_page.whitelist_list'))

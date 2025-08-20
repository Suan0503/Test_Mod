from flask import Blueprint, render_template, request, redirect, url_for
from models import Whitelist, Blacklist
from extensions import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# 這裡可以根據你的權限判斷做登入檢查

@admin_bp.route("/whitelist", methods=["GET"])
def show_whitelist():
    query_phone = request.args.get("phone", "")
    if query_phone:
        data = Whitelist.query.filter(Whitelist.phone.like(f"%{query_phone}%")).all()
    else:
        data = Whitelist.query.order_by(Whitelist.id.desc()).limit(100).all()
    return render_template("admin_whitelist.html", data=data, query_phone=query_phone)

@admin_bp.route("/blacklist", methods=["GET"])
def show_blacklist():
    query_phone = request.args.get("phone", "")
    if query_phone:
        data = Blacklist.query.filter(Blacklist.phone.like(f"%{query_phone}%")).all()
    else:
        data = Blacklist.query.order_by(Blacklist.id.desc()).limit(100).all()
    return render_template("admin_blacklist.html", data=data, query_phone=query_phone)

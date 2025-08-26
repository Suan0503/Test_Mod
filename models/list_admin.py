from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.whitelist import Whitelist
from models.blacklist import Blacklist
from extensions import db

list_admin_bp = Blueprint('list_admin', __name__, url_prefix="/admin/list")

@list_admin_bp.route("/")
def index():
    whitelists = Whitelist.query.all()
    blacklists = Blacklist.query.all()
    return render_template("admin/index.html", whitelists=whitelists, blacklists=blacklists)

# 新增/修改/查詢等功能可依需求新增

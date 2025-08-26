"""
管理員清單後台路由
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.whitelist import Whitelist
from models.blacklist import Blacklist
from sqlalchemy import or_
list_admin_bp = Blueprint("list_admin", __name__, template_folder="../templates", url_prefix="/admin/list")


@list_admin_bp.route("/", methods=["GET"])
def index():
    q = request.args.get("q", "").strip()
    if q:
        wl_filters = []
        for col in ("identifier", "name", "phone", "email", "line_id", "line_user_id"):
            if hasattr(Whitelist, col):
                wl_filters.append(getattr(Whitelist, col).ilike(f"%{q}%"))
        bl_filters = []
        for col in ("identifier", "name", "phone", "email"):
            if hasattr(Blacklist, col):
                bl_filters.append(getattr(Blacklist, col).ilike(f"%{q}%"))
        whitelists = Whitelist.query.filter(or_(*wl_filters)).all() if wl_filters else []
        blacklists = Blacklist.query.filter(or_(*bl_filters)).all() if bl_filters else []
    else:
        try:
            whitelists = Whitelist.query.order_by(Whitelist.created_at.desc()).limit(200).all()
        except Exception:
            whitelists = Whitelist.query.limit(200).all()
        try:
            blacklists = Blacklist.query.order_by(Blacklist.created_at.desc()).limit(200).all()
        except Exception:
            blacklists = Blacklist.query.limit(200).all()
    return render_template("admin/index.html", whitelists=whitelists, blacklists=blacklists, q=q)


@list_admin_bp.route("/whitelist/new", methods=["GET"])
def new_whitelist_form():
    return render_template("admin/whitelist_form.html", item=None)


@list_admin_bp.route("/whitelist/new", methods=["POST"])
def new_whitelist():
    identifier = request.form.get("identifier", "").strip()
    if not identifier:
        flash("Identifier 為必填欄位", "danger")
        return redirect(url_for(".new_whitelist_form"))

    existing_black = Blacklist.query.filter_by(identifier=identifier).first() if hasattr(Blacklist, "identifier") else None
    if existing_black:
        flash("此 identifier 已在黑名單中，請先從黑名單移除再加入白名單", "warning")
        return redirect(url_for(".index"))

    existing = Whitelist.query.filter_by(identifier=identifier).first() if hasattr(Whitelist, "identifier") else None
    if existing:
        flash("此 identifier 已在白名單中", "info")
        return redirect(url_for(".edit_whitelist", id=existing.id))

    item = Whitelist()
    for key in ["identifier", "name", "phone", "email", "note"]:
        val = request.form.get(key)
        if val:
            setattr(item, key, val)
    db.session.add(item)
    db.session.commit()
    flash("新增白名單成功", "success")
    return redirect(url_for(".index"))


@list_admin_bp.route("/whitelist/<int:id>/edit", methods=["GET"])
def edit_whitelist(id):
    item = Whitelist.query.get_or_404(id)
    return render_template("admin/whitelist_form.html", item=item)


@list_admin_bp.route("/whitelist/<int:id>/edit", methods=["POST"])
def update_whitelist(id):
    item = Whitelist.query.get_or_404(id)
    identifier = request.form.get("identifier", "").strip()
    if not identifier:
        flash("Identifier 為必填欄位", "danger")
        return redirect(url_for(".edit_whitelist", id=id))

    if hasattr(Blacklist, "identifier") and Blacklist.query.filter_by(identifier=identifier).first():
        flash("欲修改的 identifier 已存在於黑名單中，請先處理黑名單", "danger")
        return redirect(url_for(".edit_whitelist", id=id))

    if hasattr(Whitelist, "identifier"):
        other = Whitelist.query.filter(Whitelist.identifier == identifier, Whitelist.id != id).first()
        if other:
            flash("此 identifier 已存在於其他白名單項目", "danger")
            return redirect(url_for(".edit_whitelist", id=id))

    item.identifier = identifier
    for key in ["name", "phone", "email", "note"]:
        val = request.form.get(key)
        if val:
            setattr(item, key, val)
    db.session.commit()
    flash("白名單更新成功", "success")
    return redirect(url_for(".index"))


@list_admin_bp.route("/blacklist/new", methods=["GET"])
def new_blacklist_form():
    return render_template("admin/blacklist_form.html", item=None)


@list_admin_bp.route("/blacklist/new", methods=["POST"])
def new_blacklist():
    identifier = request.form.get("identifier", "").strip()
    if not identifier:
        flash("Identifier 為必填欄位", "danger")
        return redirect(url_for(".new_blacklist_form"))
    existing_white = Whitelist.query.filter_by(identifier=identifier).first() if hasattr(Whitelist, "identifier") else None
    if existing_white:
        flash("此 identifier 已在白名單中，請先從白名單移除再加入黑名單", "warning")
        return redirect(url_for(".index"))
    existing = Blacklist.query.filter_by(identifier=identifier).first() if hasattr(Blacklist, "identifier") else None
    if existing:
        flash("此 identifier 已在黑名單中", "info")
        return redirect(url_for(".edit_blacklist", id=existing.id))
    item = Blacklist()
    for key in ["identifier", "name", "phone", "email", "note", "reason"]:
        val = request.form.get(key)
        if val:
            setattr(item, key, val)
    db.session.add(item)
    db.session.commit()
    flash("新增黑名單成功", "success")
    return redirect(url_for(".index"))


@list_admin_bp.route("/blacklist/<int:id>/edit", methods=["GET"])
def edit_blacklist(id):
    item = Blacklist.query.get_or_404(id)
    return render_template("admin/blacklist_form.html", item=item)


@list_admin_bp.route("/blacklist/<int:id>/edit", methods=["POST"])
def update_blacklist(id):
    item = Blacklist.query.get_or_404(id)
    identifier = request.form.get("identifier", "").strip()
    if not identifier:
        flash("Identifier 為必填欄位", "danger")
        return redirect(url_for(".edit_blacklist", id=id))
    if hasattr(Whitelist, "identifier") and Whitelist.query.filter_by(identifier=identifier).first():
        flash("欲修改的 identifier 已存在於白名單中，請先處理白名單", "danger")
        return redirect(url_for(".edit_blacklist", id=id))
    if hasattr(Blacklist, "identifier"):
        other = Blacklist.query.filter(Blacklist.identifier == identifier, Blacklist.id != id).first()
        if other:
            flash("此 identifier 已存在於其他黑名單項目", "danger")
            return redirect(url_for(".edit_blacklist", id=id))
    item.identifier = identifier
    for key in ["name", "phone", "email", "note", "reason"]:
        val = request.form.get(key)
        if val:
            setattr(item, key, val)
    db.session.commit()
    flash("黑名單更新成功", "success")
    return redirect(url_for(".index"))


@list_admin_bp.route("/whitelist/<int:id>/delete", methods=["POST"])
def delete_whitelist(id):
    item = Whitelist.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash("刪除白名單成功", "success")
    return redirect(url_for(".index"))


@list_admin_bp.route("/blacklist/<int:id>/delete", methods=["POST"])
def delete_blacklist(id):
    item = Blacklist.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash("刪除黑名單成功", "success")
    return redirect(url_for(".index"))

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from extensions import db
from models import Whitelist, Blacklist
from sqlalchemy import or_
import csv
import io
import math
from datetime import datetime

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Helper: pagination
def paginate_query(query, page, per_page):
    total = query.count()
    total_pages = math.ceil(total / per_page) if per_page else 1
    items = query.offset((page - 1) * per_page).limit(per_page).all() if per_page else query.all()
    return items, total, total_pages

# ----- Whitelist -----
@admin_bp.route("/whitelist")
def whitelist():
    q = request.args.get("q", "").strip()
    page = max(int(request.args.get("page", 1)), 1)
    per_page = int(request.args.get("per_page", 20))
    query = Whitelist.query.order_by(Whitelist.id.desc())
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Whitelist.name.ilike(like),
                Whitelist.phone.ilike(like),
                Whitelist.line_id.ilike(like),
                Whitelist.line_user_id.ilike(like),
            )
        )
    users, total, total_pages = paginate_query(query, page, per_page)
    return render_template("whitelist.html", users=users, q=q, page=page, total=total, total_pages=total_pages)

@admin_bp.route("/whitelist/view/<int:id>")
def whitelist_view(id):
    u = Whitelist.query.get_or_404(id)
    return render_template("whitelist_view.html", u=u)

@admin_bp.route("/whitelist/add", methods=["GET", "POST"])
def whitelist_add():
    if request.method == "POST":
        data = {
            "date": request.form.get("date"),
            "phone": request.form.get("phone"),
            "reason": request.form.get("reason"),
            "name": request.form.get("name"),
            "line_id": request.form.get("line_id"),
            "line_user_id": request.form.get("line_user_id"),
            "created_at": datetime.utcnow(),
        }
        try:
            w = Whitelist(**data)
            db.session.add(w)
            db.session.commit()
            flash("已新增白名單。", "success")
            return redirect(url_for("admin.whitelist"))
        except Exception as e:
            db.session.rollback()
            flash(f"新增失敗：{str(e)}", "danger")
    return render_template("whitelist_edit.html", u=None)

@admin_bp.route("/whitelist/edit/<int:id>", methods=["GET", "POST"])
def whitelist_edit(id):
    u = Whitelist.query.get_or_404(id)
    if request.method == "POST":
        u.date = request.form.get("date")
        u.phone = request.form.get("phone")
        u.reason = request.form.get("reason")
        u.name = request.form.get("name")
        u.line_id = request.form.get("line_id")
        u.line_user_id = request.form.get("line_user_id")
        try:
            db.session.commit()
            flash("已更新白名單。", "success")
            return redirect(url_for("admin.whitelist"))
        except Exception as e:
            db.session.rollback()
            flash(f"更新失敗：{str(e)}", "danger")
    return render_template("whitelist_edit.html", u=u)

@admin_bp.route("/whitelist/delete/<int:id>", methods=["POST"])
def whitelist_delete(id):
    u = Whitelist.query.get_or_404(id)
    try:
        db.session.delete(u)
        db.session.commit()
        flash("已刪除白名單。", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"刪除失敗：{str(e)}", "danger")
    return redirect(url_for("admin.whitelist"))

@admin_bp.route("/whitelist/move_to_blacklist/<int:id>", methods=["POST"])
def move_to_blacklist(id):
    u = Whitelist.query.get_or_404(id)
    try:
        b = Blacklist(date=u.date, phone=u.phone, reason=u.reason, name=u.name, created_at=u.created_at)
        db.session.add(b)
        db.session.delete(u)
        db.session.commit()
        flash("已將使用者移至黑名單。", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"移動失敗：{str(e)}", "danger")
    return redirect(url_for("admin.whitelist"))

@admin_bp.route("/whitelist/export")
def export_whitelist():
    q = request.args.get("q", "").strip()
    query = Whitelist.query.order_by(Whitelist.id.desc())
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Whitelist.name.ilike(like),
                Whitelist.phone.ilike(like),
                Whitelist.line_id.ilike(like),
                Whitelist.line_user_id.ilike(like),
            )
        )
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["id", "created_at", "date", "name", "phone", "line_id", "line_user_id", "reason"])
    for u in query.all():
        cw.writerow([u.id, u.created_at, u.date or "", u.name or "", u.phone or "", u.line_id or "", u.line_user_id or "", (u.reason or "").replace("\n", " ")])
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=whitelist.csv"})

# ----- Blacklist -----
@admin_bp.route("/blacklist")
def blacklist():
    q = request.args.get("q", "").strip()
    page = max(int(request.args.get("page", 1)), 1)
    per_page = int(request.args.get("per_page", 20))
    query = Blacklist.query.order_by(Blacklist.id.desc())
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Blacklist.name.ilike(like),
                Blacklist.phone.ilike(like),
                Blacklist.reason.ilike(like),
            )
        )
    users, total, total_pages = paginate_query(query, page, per_page)
    return render_template("blacklist.html", users=users, q=q, page=page, total=total, total_pages=total_pages)

@admin_bp.route("/blacklist/view/<int:id>")
def blacklist_view(id):
    u = Blacklist.query.get_or_404(id)
    return render_template("blacklist_view.html", u=u)

@admin_bp.route("/blacklist/add", methods=["GET", "POST"])
def blacklist_add():
    if request.method == "POST":
        data = {
            "date": request.form.get("date"),
            "phone": request.form.get("phone"),
            "reason": request.form.get("reason"),
            "name": request.form.get("name"),
            "created_at": datetime.utcnow(),
        }
        try:
            b = Blacklist(**data)
            db.session.add(b)
            db.session.commit()
            flash("已新增黑名單。", "success")
            return redirect(url_for("admin.blacklist"))
        except Exception as e:
            db.session.rollback()
            flash(f"新增失敗：{str(e)}", "danger")
    return render_template("blacklist_edit.html", u=None)

@admin_bp.route("/blacklist/edit/<int:id>", methods=["GET", "POST"])
def blacklist_edit(id):
    u = Blacklist.query.get_or_404(id)
    if request.method == "POST":
        u.date = request.form.get("date")
        u.phone = request.form.get("phone")
        u.reason = request.form.get("reason")
        u.name = request.form.get("name")
        try:
            db.session.commit()
            flash("已更新黑名單。", "success")
            return redirect(url_for("admin.blacklist"))
        except Exception as e:
            db.session.rollback()
            flash(f"更新失敗：{str(e)}", "danger")
    return render_template("blacklist_edit.html", u=u)

@admin_bp.route("/blacklist/delete/<int:id>", methods=["POST"])
def blacklist_delete(id):
    u = Blacklist.query.get_or_404(id)
    try:
        db.session.delete(u)
        db.session.commit()
        flash("已刪除黑名單。", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"刪除失敗：{str(e)}", "danger")
    return redirect(url_for("admin.blacklist"))

@admin_bp.route("/blacklist/move_to_whitelist/<int:id>", methods=["POST"])
def move_to_whitelist(id):
    u = Blacklist.query.get_or_404(id)
    try:
        w = Whitelist(date=u.date, phone=u.phone, reason=u.reason, name=u.name, created_at=u.created_at)
        db.session.add(w)
        db.session.delete(u)
        db.session.commit()
        flash("已將使用者移至白名單。", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"移動失敗：{str(e)}", "danger")
    return redirect(url_for("admin.blacklist"))

@admin_bp.route("/blacklist/export")
def export_blacklist():
    q = request.args.get("q", "").strip()
    query = Blacklist.query.order_by(Blacklist.id.desc())
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Blacklist.name.ilike(like),
                Blacklist.phone.ilike(like),
                Blacklist.reason.ilike(like),
            )
        )
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["id", "created_at", "date", "name", "phone", "reason"])
    for u in query.all():
        cw.writerow([u.id, u.created_at, u.date or "", u.name or "", u.phone or "", (u.reason or "").replace("\n", " ")])
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=blacklist.csv"})

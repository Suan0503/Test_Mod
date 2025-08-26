from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.whitelist import Whitelist
from models.blacklist import Blacklist
from sqlalchemy import or_

list_admin_bp = Blueprint("list_admin", __name__, template_folder="../templates", url_prefix="/admin/list")

# 列表頁（含查詢）
@list_admin_bp.route("/", methods=["GET"])
def index():
    q = request.args.get("q", "").strip()
    if q:
        # 根據模型實際存在的欄位動態建立搜尋條件，避免缺欄位導致錯誤
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
        # 若無搜尋字串，盡可能使用 created_at 排序，失敗時 fallback 為不排序的查詢
        try:
            whitelists = Whitelist.query.order_by(Whitelist.created_at.desc()).limit(200).all()
        except Exception:
            whitelists = Whitelist.query.limit(200).all()
        try:
            blacklists = Blacklist.query.order_by(Blacklist.created_at.desc()).limit(200).all()
        except Exception:
            blacklists = Blacklist.query.limit(200).all()
    return render_template("admin/index.html", whitelists=whitelists, blacklists=blacklists, q=q)

# 新增白名單 - 表單
@list_admin_bp.route("/whitelist/new", methods=["GET"])
def new_whitelist_form():
    return render_template("admin/whitelist_form.html", item=None)

# 新增白名單 - 提交
@list_admin_bp.route("/whitelist/new", methods=["POST"])
def new_whitelist():
    identifier = request.form.get("identifier", "").strip()
    if not identifier:
        flash("Identifier 為必填欄位", "danger")
        return redirect(url_for(".new_whitelist_form"))

    # 若在 blacklist 裡已存在 => 不允許加入白名單（或可選擇先移除黑名單）
    existing_black = Blacklist.query.filter_by(identifier=identifier).first() if hasattr(Blacklist, "identifier") else None
    if existing_black:
        flash("此 identifier 已在黑名單中，請先從黑名單移除再加入白名單", "warning")
        return redirect(url_for(".index"))

    existing = Whitelist.query.filter_by(identifier=identifier).first() if hasattr(Whitelist, "identifier") else None
    if existing:
        flash("此 identifier 已在白名單中", "info")
        return redirect(url_for(".edit_whitelist", id=existing.id))

    item = Whitelist(
        **({
            "identifier": identifier
        } if hasattr(Whitelist, "identifier") else {}),
        name=request.form.get("name"),
        phone=request.form.get("phone"),
        **({"email": request.form.get("email")} if hasattr(Whitelist, "email") else {}),
        **({"note": request.form.get("note")} if hasattr(Whitelist, "note") else {}),
    )
    db.session.add(item)
    db.session.commit()
    flash("新增白名單成功", "success")
    return redirect(url_for(".index"))

# 編輯白名單 - 表單
@list_admin_bp.route("/whitelist/<int:id>/edit", methods=["GET"])
def edit_whitelist(id):
    item = Whitelist.query.get_or_404(id)
    return render_template("admin/whitelist_form.html", item=item)

# 編輯白名單 - 提交
@list_admin_bp.route("/whitelist/<int:id>/edit", methods=["POST"])
def update_whitelist(id):
    item = Whitelist.query.get_or_404(id)
    identifier = request.form.get("identifier", "").strip()
    if not identifier:
        flash("Identifier 為必填欄位", "danger")
        return redirect(url_for(".edit_whitelist", id=id))

    # 若 identifier 被改成已存在於 blacklist -> 拒絕
    if hasattr(Blacklist, "identifier") and Blacklist.query.filter_by(identifier=identifier).first():
        flash("欲修改的 identifier 已存在於黑名單中，請先處理黑名單", "danger")
        return redirect(url_for(".edit_whitelist", id=id))

    # 若 identifier 重複於別的白名單 item -> 拒絕
    if hasattr(Whitelist, "identifier"):
        other = Whitelist.query.filter(Whitelist.identifier == identifier, Whitelist.id != id).first()
        if other:
            flash("Identifier 與其他白名單重複", "danger")
            return redirect(url_for(".edit_whitelist", id=id))
        item.identifier = identifier

    item.name = request.form.get("name")
    item.phone = request.form.get("phone")
    if hasattr(Whitelist, "email"):
        item.email = request.form.get("email")
    if hasattr(Whitelist, "note"):
        item.note = request.form.get("note")
    db.session.commit()
    flash("修改白名單成功", "success")
    return redirect(url_for(".index"))

# 新增黑名單 - 表單
@list_admin_bp.route("/blacklist/new", methods=["GET"])
def new_blacklist_form():
    return render_template("admin/blacklist_form.html", item=None)

# 新增黑名單 - 提交（如果在白名單內，轉移）
@list_admin_bp.route("/blacklist/new", methods=["POST"])
def new_blacklist():
    identifier = request.form.get("identifier", "").strip()
    if not identifier:
        flash("Identifier 為必填欄位", "danger")
        return redirect(url_for(".new_blacklist_form"))

    # 已在 blacklist 中
    existing_bl = Blacklist.query.filter_by(identifier=identifier).first() if hasattr(Blacklist, "identifier") else None
    if existing_bl:
        flash("此 identifier 已在黑名單中", "info")
        return redirect(url_for(".index"))

    # 如果存在於白名單，則移除白名單（轉移）
    whitelist_item = Whitelist.query.filter_by(identifier=identifier).first() if hasattr(Whitelist, "identifier") else None
    try:
        if whitelist_item:
            # create blacklist from whitelist info + reason/note if provided
            bl_kwargs = {"identifier": identifier} if hasattr(Blacklist, "identifier") else {}
            if hasattr(Blacklist, "name"):
                bl_kwargs["name"] = whitelist_item.name
            if hasattr(Blacklist, "phone"):
                bl_kwargs["phone"] = whitelist_item.phone
            if hasattr(Blacklist, "email") and hasattr(whitelist_item, "email"):
                bl_kwargs["email"] = whitelist_item.email
            if hasattr(Blacklist, "reason"):
                bl_kwargs["reason"] = request.form.get("reason")
            if hasattr(Blacklist, "note"):
                bl_kwargs["note"] = request.form.get("note")

            bl = Blacklist(**bl_kwargs)
            db.session.add(bl)
            db.session.delete(whitelist_item)
            db.session.commit()
            flash("已由白名單轉為黑名單", "success")
            return redirect(url_for(".index"))
        else:
            bl = Blacklist(
                **({"identifier": identifier} if hasattr(Blacklist, "identifier") else {}),
                name=request.form.get("name"),
                phone=request.form.get("phone"),
                **({"email": request.form.get("email")} if hasattr(Blacklist, "email") else {}),
                reason=request.form.get("reason"),
                **({"note": request.form.get("note")} if hasattr(Blacklist, "note") else {}),
            )
            db.session.add(bl)
            db.session.commit()
            flash("新增黑名單成功", "success")
            return redirect(url_for(".index"))
    except Exception as e:
        db.session.rollback()
        flash(f"發生錯誤: {e}", "danger")
        return redirect(url_for(".index"))

# 編輯黑名單 - 表單
@list_admin_bp.route("/blacklist/<int:id>/edit", methods=["GET"])
def edit_blacklist(id):
    item = Blacklist.query.get_or_404(id)
    return render_template("admin/blacklist_form.html", item=item)

# 編輯黑名單 - 提交
@list_admin_bp.route("/blacklist/<int:id>/edit", methods=["POST"])
def update_blacklist(id):
    item = Blacklist.query.get_or_404(id)
    identifier = request.form.get("identifier", "").strip()
    if not identifier:
        flash("Identifier 為必填欄位", "danger")
        return redirect(url_for(".edit_blacklist", id=id))

    # 若 identifier 被改成已存在於白名單 -> 拒絕
    if hasattr(Whitelist, "identifier") and Whitelist.query.filter_by(identifier=identifier).first():
        flash("欲修改的 identifier 已在白名單中，請先處理白名單。", "danger")
        return redirect(url_for(".edit_blacklist", id=id))

    if hasattr(Blacklist, "identifier"):
        other = Blacklist.query.filter(Blacklist.identifier == identifier, Blacklist.id != id).first()
        if other:
            flash("Identifier 與其他黑名單重複", "danger")
            return redirect(url_for(".edit_blacklist", id=id))
        item.identifier = identifier

    item.name = request.form.get("name")
    item.phone = request.form.get("phone")
    if hasattr(Blacklist, "email"):
        item.email = request.form.get("email")
    item.reason = request.form.get("reason")
    if hasattr(Blacklist, "note"):
        item.note = request.form.get("note")
    db.session.commit()
    flash("修改黑名單成功", "success")
    return redirect(url_for(".index"))

# 可擴充：刪除白/黑名單 API（這裡提供簡單刪除）
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

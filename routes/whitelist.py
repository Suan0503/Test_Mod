from flask import Blueprint, render_template, request, redirect, url_for
from models.whitelist import Whitelist
from extensions import db

whitelist_bp = Blueprint("whitelist", __name__, template_folder="../templates")

@whitelist_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        note = request.form.get("note", "")
        db.session.add(Whitelist(name=name, note=note))
        db.session.commit()
        return redirect(url_for("whitelist.index"))
    items = Whitelist.query.all()
    return render_template("whitelist.html", items=items)

@whitelist_bp.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    item = Whitelist.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("whitelist.index"))

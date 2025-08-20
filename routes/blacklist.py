from flask import Blueprint, render_template, request, redirect, url_for
from models.blacklist import Blacklist
from extensions import db

blacklist_bp = Blueprint("blacklist", __name__, template_folder="../templates")

@blacklist_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        reason = request.form.get("reason", "")
        db.session.add(Blacklist(name=name, reason=reason))
        db.session.commit()
        return redirect(url_for("blacklist.index"))
    items = Blacklist.query.all()
    return render_template("blacklist.html", items=items)

@blacklist_bp.route("/delete/<int:item_id>", methods=["POST"])
def delete(item_id):
    item = Blacklist.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("blacklist.index"))

from flask import Blueprint, render_template, request
from models.blacklist import Blacklist
from models.whitelist import Whitelist

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates")

@dashboard_bp.route("/search", methods=["GET", "POST"])
def search():
    results = []
    keyword = ""
    if request.method == "POST":
        keyword = request.form["keyword"]
        blist = Blacklist.query.filter(Blacklist.name.contains(keyword)).all()
        wlist = Whitelist.query.filter(Whitelist.name.contains(keyword)).all()
        results = [{"type": "黑名單", "name": i.name, "reason": i.reason} for i in blist] + \
                  [{"type": "白名單", "name": i.name, "note": i.note} for i in wlist]
    return render_template("search.html", results=results, keyword=keyword)

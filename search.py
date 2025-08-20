from flask import Blueprint, render_template, request
from extensions import db
from models import Whitelist, Blacklist

search_bp = Blueprint('search', __name__, template_folder='templates')

@search_bp.route("/", methods=["GET", "POST"])
def home():
    search_result = []
    phone = ""
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        query_phones = [phone]
        if len(phone) == 9 and not phone.startswith("0"):
            query_phones.append("0" + phone)
        for p in query_phones:
            whitelist = db.session.query(Whitelist).filter_by(phone=p).first()
            blacklist = db.session.query(Blacklist).filter_by(phone=p).first()
            if whitelist:
                search_result.append({"type": "white", "phone": p, "record": whitelist})
            if blacklist:
                search_result.append({"type": "black", "phone": p, "record": blacklist})
    return render_template("search.html", search_result=search_result, phone=phone)

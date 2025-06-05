from flask import Blueprint, request, abort

message_bp = Blueprint('message', __name__)

@message_bp.route("/callback", methods=["POST"])
def callback():
    return "OK"

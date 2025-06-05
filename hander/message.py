{\rtf1\ansi\ansicpg950\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage\
from app import handler, line_bot_api\
from models import db, Whitelist, Blacklist, Coupon\
from utils.draw_utils import draw_coupon, get_today_coupon_flex, has_drawn_today, save_coupon_record\
from utils.image_verification import extract_lineid_phone\
from utils.special_case import is_special_case\
from flask import current_app\
import pytz\
import re\
from datetime import datetime\
\
# \uc0\u36889 \u35041 \u20551 \u35373  temp_users \u33287  manual_verify_pending \u23526 \u20316 \u26044  app.py \u25110  storage.py\u65292 \u35531 \u26681 \u25818 \u23560 \u26696 \u23526 \u38555 \u24773 \u27841 \u35519 \u25972 \
from app import temp_users, manual_verify_pending, ADMIN_IDS\
\
@handler.add(MessageEvent, message=TextMessage)\
def handle_message(event):\
    user_id = event.source.user_id\
    user_text = event.message.text.strip()\
    tz = pytz.timezone("Asia/Taipei")\
    profile = line_bot_api.get_profile(user_id)\
    display_name = profile.display_name\
\
    # === \uc0\u25163 \u21205 \u39511 \u35657  - \u20677 \u38480 \u31649 \u29702 \u21729 \u27969 \u31243  ===\
    if user_text.startswith("\uc0\u25163 \u21205 \u39511 \u35657  - "):\
        if user_id not in ADMIN_IDS:\
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="\uc0\u10060  \u21482 \u26377 \u31649 \u29702 \u21729 \u21487 \u20351 \u29992 \u27492 \u21151 \u33021 "))\
            return\
        parts = user_text.split(" - ", 1)\
        if len(parts) == 2:\
            temp_users[user_id] = \{"manual_step": "wait_lineid", "name": parts[1]\}\
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="\uc0\u35531 \u36664 \u20837 \u35442 \u29992 \u25142 \u30340  LINE ID"))\
        else:\
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="\uc0\u26684 \u24335 \u37679 \u35492 \u65292 \u35531 \u29992 \u65306 \u25163 \u21205 \u39511 \u35657  - \u26289 \u31281 "))\
        return\
\
    if user_id in temp_users and temp_users[user_id].get("manual_step") == "wait_lineid":\
        temp_users[user_id]['line_id'] = user_text\
        temp_users[user_id]['manual_step'] = "wait_phone"\
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="\uc0\u35531 \u36664 \u20837 \u35442 \u29992 \u25142 \u30340 \u25163 \u27231 \u34399 \u30908 "))\
        return\
\
    if user_id in temp_users and temp_users[user_id].get("manual_step") == "wait_phone":\
        temp_users[user_id]['phone'] = user_text\
        code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))\
        manual_verify_pending[code] = \{\
            'name': temp_users[user_id]['name'],\
            'line_id': temp_users[user_id]['line_id'],\
            'phone': temp_users[user_id]['phone'],\
            'step': 'wait_user_input'\
        \}\
        del temp_users[user_id]\
        line_bot_api.reply_message(\
            event.reply_token,\
            TextSendMessage(text=f"\uc0\u39511 \u35657 \u30908 \u29986 \u29983 \u65306 \{code\}\\n\u35531 \u23559 \u27492 8\u20301 \u39511 \u35657 \u30908 \u33258 \u34892 \u36664 \u20837 \u32842 \u22825 \u23460 ")\
        )\
        return\
\
    # \uc0\u39511 \u35657 \u30908 \u65288 \u20219 \u20309 \u20154 \u37117 \u21487 \u36664 \u20837 \u65292 \u21482 \u33021 \u29992 \u19968 \u27425 \u65289 \
    if len(user_text) == 8 and user_text in manual_verify_pending:\
        record = manual_verify_pending[user_text]\
        temp_users[user_id] = \{\
            "manual_step": "wait_confirm",\
            "name": record['name'],\
            "line_id": record['line_id'],\
            "phone": record['phone'],\
            "verify_code": user_text\
        \}\
        reply = (\
            f"\uc0\u55357 \u56561  \u25163 \u27231 \u34399 \u30908 \u65306 \{record['phone']\}\\n"\
            f"\uc0\u55356 \u57144  \u26289 \u31281 \u65306 \{record['name']\}\\n"\
            f"       \uc0\u20491 \u20154 \u32232 \u34399 \u65306 \u24453 \u39511 \u35657 \u24460 \u29986 \u29983 \\n"\
            f"\uc0\u55357 \u56599  LINE ID\u65306 \{record['line_id']\}\\n"\
            f"\uc0\u65288 \u27492 \u29992 \u25142 \u28858 \u25163 \u21205 \u36890 \u36942 \u65289 \\n"\
            f"\uc0\u35531 \u21839 \u20197 \u19978 \u36039 \u26009 \u26159 \u21542 \u27491 \u30906 \u65311 \u27491 \u30906 \u35531 \u22238 \u24489  1\\n"\
            f"\uc0\u9888 \u65039 \u36664 \u20837 \u37679 \u35492 \u35531 \u24478 \u26032 \u36664 \u20837 \u25163 \u27231 \u34399 \u30908 \u21363 \u21487 \u9888 \u65039 "\
        )\
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))\
        manual_verify_pending.pop(user_text, None)\
        return\
\
    if user_id in temp_users and temp_users[user_id].get("manual_step") == "wait_confirm" and user_text == "1":\
        data = temp_users[user_id]\
        now = datetime.now(tz)\
        data["date"] = now.strftime("%Y-%m-%d")\
        # \uc0\u23526 \u20316  update_or_create_whitelist_from_data\
        from utils.db_utils import update_or_create_whitelist_from_data  # \uc0\u35531 \u25918 \u21040  utils/db_utils.py\
        record, is_new = update_or_create_whitelist_from_data(data, user_id)\
        if is_new:\
            reply = (\
                f"\uc0\u55357 \u56561  \u25163 \u27231 \u34399 \u30908 \u65306 \{data['phone']\}\\n"\
                f"\uc0\u55356 \u57144  \u26289 \u31281 \u65306 \{data['name']\}\\n"\
                f"       \uc0\u20491 \u20154 \u32232 \u34399 \u65306 \{record.id\}\\n"\
                f"\uc0\u55357 \u56599  LINE ID\u65306 \{data['line_id']\}\\n"\
                f"\uc0\u9989  \u39511 \u35657 \u25104 \u21151 \u65292 \u27489 \u36814 \u21152 \u20837 \u33559 \u27583 "\
            )\
        else:\
            reply = (\
                f"\uc0\u55357 \u56561  \u25163 \u27231 \u34399 \u30908 \u65306 \{record.phone\}\\n"\
                f"\uc0\u55356 \u57144  \u26289 \u31281 \u65306 \{record.name or data.get('name')\}\\n"\
                f"       \uc0\u20491 \u20154 \u32232 \u34399 \u65306 \{record.id\}\\n"\
                f"\uc0\u55357 \u56599  LINE ID\u65306 \{record.line_id or data.get('line_id')\}\\n"\
                f"\uc0\u9989  \u20320 \u30340 \u36039 \u26009 \u24050 \u35036 \u20840 \u65292 \u27489 \u36814 \u21152 \u20837 \u33559 \u27583 "\
            )\
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))\
        temp_users.pop(user_id)\
        return\
\
    if user_text == "\uc0\u25163 \u21205 \u36890 \u36942 ":\
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="\uc0\u10060  \u27492 \u21151 \u33021 \u24050 \u38364 \u38281 "))\
        return\
\
    if user_text == "\uc0\u39511 \u35657 \u36039 \u35338 ":\
        existing = Whitelist.query.filter_by(line_user_id=user_id).first()\
        if existing:\
            reply = (\
                f"\uc0\u55357 \u56561  \{existing.phone\}\\n"\
                f"\uc0\u55356 \u57144  \u26289 \u31281 \u65306 \{existing.name or display_name\}\\n"\
                f"       \uc0\u20491 \u20154 \u32232 \u34399 \u65306 \{existing.id\}\\n"\
                f"\uc0\u55357 \u56599  LINE ID\u65306 \{existing.line_id or '\u26410 \u30331 \u35352 '\}\\n"\
                f"\uc0\u55357 \u56658  \{existing.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')\}\\n"\
                f"\uc0\u9989  \u39511 \u35657 \u25104 \u21151 \u65292 \u27489 \u36814 \u21152 \u20837 \u33559 \u27583 \\n"\
                f"\uc0\u55356 \u57119  \u21152 \u20837 \u23494 \u30908 \u65306 ming666"\
            )\
            line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=reply), get_today_coupon_flex(user_id, display_name, 0)])\
        else:\
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="\uc0\u9888 \u65039  \u20320 \u23578 \u26410 \u23436 \u25104 \u39511 \u35657 \u65292 \u35531 \u36664 \u20837 \u25163 \u27231 \u34399 \u30908 \u36914 \u34892 \u39511 \u35657 \u12290 "))\
        return\
\
    if user_text == "\uc0\u27599 \u26085 \u25277 \u29518 ":\
        today_str = datetime.now(tz).strftime("%Y-%m-%d")\
        if has_drawn_today(user_id, Coupon):\
            coupon = Coupon.query.filter_by(line_user_id=user_id, date=today_str).first()\
            flex = get_today_coupon_flex(user_id, display_name, coupon.amount)\
            line_bot_api.reply_message(event.reply_token, flex)\
            return\
        amount = draw_coupon()\
        save_coupon_record(user_id, amount, Coupon, db)\
        flex = get_today_coupon_flex(user_id, display_name, amount)\
        line_bot_api.reply_message(event.reply_token, flex)\
        return\
\
    existing = Whitelist.query.filter_by(line_user_id=user_id).first()\
    if existing:\
        if user_text == existing.phone:\
            reply = (\
                f"\uc0\u55357 \u56561  \{existing.phone\}\\n"\
                f"\uc0\u55356 \u57144  \u26289 \u31281 \u65306 \{existing.name or display_name\}\\n"\
                f"       \uc0\u20491 \u20154 \u32232 \u34399 \u65306 \{existing.id\}\\n"\
                f"\uc0\u55357 \u56599  LINE ID\u65306 \{existing.line_id or '\u26410 \u30331 \u35352 '\}\\n"\
                f"\uc0\u55357 \u56658  \{existing.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')\}\\n"\
                f"\uc0\u9989  \u39511 \u35657 \u25104 \u21151 \u65292 \u27489 \u36814 \u21152 \u20837 \u33559 \u27583 \\n"\
                f"\uc0\u55356 \u57119  \u21152 \u20837 \u23494 \u30908 \u65306 ming666"\
            )\
            line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=reply), get_today_coupon_flex(user_id, display_name, 0)])\
        else:\
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="\uc0\u9888 \u65039  \u20320 \u24050 \u39511 \u35657 \u23436 \u25104 \u65292 \u35531 \u36664 \u20837 \u25163 \u27231 \u34399 \u30908 \u26597 \u30475 \u39511 \u35657 \u36039 \u35338 "))\
        return\
\
    if re.match(r"^09\\d\{8\}$", user_text):\
        black = Blacklist.query.filter_by(phone=user_text).first()\
        if black:\
            return\
        repeated = Whitelist.query.filter_by(phone=user_text).first()\
        data = \{"phone": user_text, "name": display_name\}\
        from utils.db_utils import update_or_create_whitelist_from_data\
        if repeated and repeated.line_user_id:\
            # \uc0\u30452 \u25509 \u35036 \u36039 \u26009 \u65288 \u21482 \u35036 \u31354 \u27396 \u20301 \u65289 \
            update_or_create_whitelist_from_data(data)\
            line_bot_api.reply_message(\
                event.reply_token,\
                TextSendMessage(text="\uc0\u9888 \u65039  \u27492 \u25163 \u27231 \u34399 \u30908 \u24050 \u34987 \u20351 \u29992 \u65292 \u24050 \u35036 \u20840 \u32570 \u22833 \u36039 \u26009 \u12290 ")\
            )\
            return\
        temp_users[user_id] = \{"phone": user_text, "name": display_name, "step": "waiting_lineid"\}\
        line_bot_api.reply_message(\
            event.reply_token,\
            [\
                TextSendMessage(text="\uc0\u55357 \u56561  \u25163 \u27231 \u24050 \u30331 \u35352 \u22217 \u65374 \u35531 \u25509 \u33879 \u36664 \u20837 \u24744 \u30340  LINE ID"),\
                TextSendMessage(text="\uc0\u33509 \u24744 \u26377 \u35373 \u23450  LINE ID \u8594  \u9989  \u30452 \u25509 \u36664 \u20837 \u21363 \u21487 \\n\u33509 \u23578 \u26410 \u35373 \u23450  ID \u8594  \u35531 \u36664 \u20837 \u65306 \u12300 \u23578 \u26410 \u35373 \u23450 \u12301 \\n\u33509 \u24744 \u30340  LINE ID \u26159 \u25163 \u27231 \u34399 \u30908 \u26412 \u36523 \u65288 \u20363 \u22914  09xxxxxxxx\u65289 \u8594  \u35531 \u22312 \u38283 \u38957 \u21152 \u19978 \u12300 ID\u12301 \u20841 \u20491 \u23383 ")\
            ]\
        )\
        return\
\
    if user_id in temp_users and temp_users[user_id].get("step", "waiting_lineid") == "waiting_lineid" and len(user_text) >= 2:\
        record = temp_users[user_id]\
        input_lineid = user_text.strip()\
        if input_lineid.lower().startswith("id") and len(input_lineid) >= 11:\
            phone_candidate = re.sub(r"[^\\d]", "", input_lineid)\
            if len(phone_candidate) == 10 and phone_candidate.startswith("09"):\
                record["line_id"] = phone_candidate\
            else:\
                record["line_id"] = input_lineid\
        elif input_lineid in ["\uc0\u23578 \u26410 \u35373 \u23450 ", "\u28961 ID", "\u28961 ", "\u27794 \u26377 ", "\u26410 \u35373 \u23450 "]:\
            record["line_id"] = "\uc0\u23578 \u26410 \u35373 \u23450 "\
        else:\
            record["line_id"] = input_lineid\
        record["step"] = "waiting_screenshot"\
        temp_users[user_id] = record\
\
        line_bot_api.reply_message(\
            event.reply_token,\
            TextSendMessage(\
                text=(\
                    "\uc0\u35531 \u19978 \u20659 \u24744 \u30340  LINE \u20491 \u20154 \u38913 \u38754 \u25130 \u22294 \u65288 \u38656 \u28165 \u26970 \u39023 \u31034 \u25163 \u27231 \u34399 \u33287  LINE ID\u65289 \u20197 \u20379 \u39511 \u35657 \u12290 \\n"\
                    "\uc0\u55357 \u56568  \u25805 \u20316 \u25945 \u23416 \u65306 LINE\u20027 \u38913  > \u21491 \u19978 \u35282 \u35373 \u23450  > \u20491 \u20154 \u27284 \u26696 \u65288 \u40670 \u36914 \u21435 \u20043 \u24460 \u25130 \u22294 \u65289 "\
                )\
            )\
        )\
        return\
\
    if user_text == "1" and user_id in temp_users and temp_users[user_id].get("step") == "waiting_confirm":\
        data = temp_users[user_id]\
        now = datetime.now(tz)\
        data["date"] = now.strftime("%Y-%m-%d")\
        from utils.db_utils import update_or_create_whitelist_from_data\
        record, is_new = update_or_create_whitelist_from_data(data, user_id)\
        if is_new:\
            reply = (\
                f"\uc0\u55357 \u56561  \{data['phone']\}\\n"\
                f"\uc0\u55356 \u57144  \u26289 \u31281 \u65306 \{data['name']\}\\n"\
                f"       \uc0\u20491 \u20154 \u32232 \u34399 \u65306 \{record.id\}\\n"\
                f"\uc0\u55357 \u56599  LINE ID\u65306 \{data['line_id']\}\\n"\
                f"\uc0\u55357 \u56658  \{record.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')\}\\n"\
                f"\uc0\u9989  \u39511 \u35657 \u25104 \u21151 \u65292 \u27489 \u36814 \u21152 \u20837 \u33559 \u27583 \\n"\
                f"\uc0\u55356 \u57119  \u21152 \u20837 \u23494 \u30908 \u65306 ming666"\
            )\
        else:\
            reply = (\
                f"\uc0\u55357 \u56561  \{record.phone\}\\n"\
                f"\uc0\u55356 \u57144  \u26289 \u31281 \u65306 \{record.name or data.get('name')\}\\n"\
                f"       \uc0\u20491 \u20154 \u32232 \u34399 \u65306 \{record.id\}\\n"\
                f"\uc0\u55357 \u56599  LINE ID\u65306 \{record.line_id or data.get('line_id')\}\\n"\
                f"\uc0\u55357 \u56658  \{record.created_at.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S')\}\\n"\
                f"\uc0\u9989  \u20320 \u30340 \u36039 \u26009 \u24050 \u35036 \u20840 \u65292 \u27489 \u36814 \u21152 \u20837 \u33559 \u27583 \\n"\
                f"\uc0\u55356 \u57119  \u21152 \u20837 \u23494 \u30908 \u65306 ming666"\
            )\
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=reply)])\
        temp_users.pop(user_id)\
        return}
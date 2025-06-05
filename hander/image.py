{\rtf1\ansi\ansicpg950\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 \\\\\\from linebot.models import MessageEvent, ImageMessage, TextSendMessage\
from app import handler, line_bot_api\
from utils.image_verification import extract_lineid_phone\
from utils.special_case import is_special_case\
from app import temp_users\
import os\
\
@handler.add(MessageEvent, message=ImageMessage)\
def handle_image(event):\
    user_id = event.source.user_id\
    if user_id not in temp_users or temp_users[user_id].get("step") != "waiting_screenshot":\
        return\
\
    if is_special_case(user_id):\
        record = temp_users[user_id]\
        reply = (\
            f"\uc0\u55357 \u56561  \{record['phone']\}\\n"\
            f"\uc0\u55356 \u57144  \u26289 \u31281 \u65306 \{record['name']\}\\n"\
            f"       \uc0\u20491 \u20154 \u32232 \u34399 \u65306 \u24453 \u39511 \u35657 \u24460 \u29986 \u29983 \\n"\
            f"\uc0\u55357 \u56599  LINE ID\u65306 \{record['line_id']\}\\n"\
            f"\uc0\u65288 \u27492 \u29992 \u25142 \u32147 \u25163 \u21205 \u36890 \u36942 \u65289 \\n"\
            f"\uc0\u35531 \u21839 \u20197 \u19978 \u36039 \u26009 \u26159 \u21542 \u27491 \u30906 \u65311 \u27491 \u30906 \u35531 \u22238 \u24489  1\\n"\
            f"\uc0\u9888 \u65039 \u36664 \u20837 \u37679 \u35492 \u35531 \u24478 \u26032 \u36664 \u20837 \u25163 \u27231 \u34399 \u30908 \u21363 \u21487 \u9888 \u65039 "\
        )\
        record["step"] = "waiting_confirm"\
        temp_users[user_id] = record\
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))\
        return\
\
    message_content = line_bot_api.get_message_content(event.message.id)\
    image_path = f"/tmp/\{user_id\}_line_profile.png"\
    with open(image_path, 'wb') as fd:\
        for chunk in message_content.iter_content():\
            fd.write(chunk)\
\
    phone_ocr, lineid_ocr, ocr_text = extract_lineid_phone(image_path)\
    os.remove(image_path)\
    input_phone = temp_users[user_id].get("phone")\
    input_lineid = temp_users[user_id].get("line_id")\
    record = temp_users[user_id]\
\
    if input_lineid == "\uc0\u23578 \u26410 \u35373 \u23450 ":\
        if phone_ocr == input_phone:\
            reply = (\
                f"\uc0\u55357 \u56561  \{record['phone']\}\\n"\
                f"\uc0\u55356 \u57144  \u26289 \u31281 \u65306 \{record['name']\}\\n"\
                f"       \uc0\u20491 \u20154 \u32232 \u34399 \u65306 \u24453 \u39511 \u35657 \u24460 \u29986 \u29983 \\n"\
                f"\uc0\u55357 \u56599  LINE ID\u65306 \u23578 \u26410 \u35373 \u23450 \\n"\
                f"\uc0\u35531 \u21839 \u20197 \u19978 \u36039 \u26009 \u26159 \u21542 \u27491 \u30906 \u65311 \u27491 \u30906 \u35531 \u22238 \u24489  1\\n"\
                f"\uc0\u9888 \u65039 \u36664 \u20837 \u37679 \u35492 \u35531 \u24478 \u26032 \u36664 \u20837 \u25163 \u27231 \u34399 \u30908 \u21363 \u21487 \u9888 \u65039 "\
            )\
            record["step"] = "waiting_confirm"\
            temp_users[user_id] = record\
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))\
        else:\
            line_bot_api.reply_message(\
                event.reply_token,\
                TextSendMessage(text="\uc0\u10060  \u25130 \u22294 \u20013 \u30340 \u25163 \u27231 \u34399 \u30908 \u33287 \u24744 \u36664 \u20837 \u30340 \u19981 \u31526 \u65292 \u35531 \u37325 \u26032 \u19978 \u20659 \u27491 \u30906 \u30340  LINE \u20491 \u20154 \u38913 \u38754 \u25130 \u22294 \u12290 ")\
            )\
    else:\
        lineid_match = (lineid_ocr is not None and input_lineid is not None and lineid_ocr.lower() == input_lineid.lower())\
        if phone_ocr == input_phone and (lineid_match or lineid_ocr == "\uc0\u23578 \u26410 \u35373 \u23450 "):\
            reply = (\
                f"\uc0\u55357 \u56561  \{record['phone']\}\\n"\
                f"\uc0\u55356 \u57144  \u26289 \u31281 \u65306 \{record['name']\}\\n"\
                f"       \uc0\u20491 \u20154 \u32232 \u34399 \u65306 \u24453 \u39511 \u35657 \u24460 \u29986 \u29983 \\n"\
                f"\uc0\u55357 \u56599  LINE ID\u65306 \{record['line_id']\}\\n"\
                f"\uc0\u35531 \u21839 \u20197 \u19978 \u36039 \u26009 \u26159 \u21542 \u27491 \u30906 \u65311 \u27491 \u30906 \u35531 \u22238 \u24489  1\\n"\
                f"\uc0\u9888 \u65039 \u36664 \u20837 \u37679 \u35492 \u35531 \u24478 \u26032 \u36664 \u20837 \u25163 \u27231 \u34399 \u30908 \u21363 \u21487 \u9888 \u65039 "\
            )\
            record["step"] = "waiting_confirm"\
            temp_users[user_id] = record\
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))\
        else:\
            line_bot_api.reply_message(\
                event.reply_token,\
                TextSendMessage(\
                    text=(\
                        "\uc0\u10060  \u25130 \u22294 \u20013 \u30340 \u25163 \u27231 \u34399 \u30908 \u25110  LINE ID \u33287 \u24744 \u36664 \u20837 \u30340 \u19981 \u31526 \u65292 \u35531 \u37325 \u26032 \u19978 \u20659 \u27491 \u30906 \u30340  LINE \u20491 \u20154 \u38913 \u38754 \u25130 \u22294 \u12290 \\n"\
                        f"\uc0\u12304 \u22294 \u29255 \u20597 \u28204 \u32080 \u26524 \u12305 \u25163 \u27231 :\{phone_ocr or '\u26410 \u35672 \u21029 '\}\\nLINE ID:\{lineid_ocr or '\u26410 \u35672 \u21029 '\}"\
                    )\
                )\
            )}
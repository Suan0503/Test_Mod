{\rtf1\ansi\ansicpg950\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from linebot.models import FollowEvent, TextSendMessage\
from app import handler, line_bot_api\
\
@handler.add(FollowEvent)\
def handle_follow(event):\
    msg = (\
        "\uc0\u27489 \u36814 \u21152 \u20837 \u55356 \u57205 \u33559 \u27583 \u55356 \u57205 \\n"\
        "\uc0\u35531 \u27491 \u30906 \u25353 \u29031 \u27493 \u39519 \u25552 \u20379 \u36039 \u26009 \u37197 \u21512 \u24555 \u36895 \u39511 \u35657 \\n\\n"\
        "\uc0\u10145 \u65039  \u35531 \u36664 \u20837 \u25163 \u27231 \u34399 \u30908 \u36914 \u34892 \u39511 \u35657 \u65288 \u21547 09\u38283 \u38957 \u65289 "\
    )\
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))}
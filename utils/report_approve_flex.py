from linebot.models import FlexSendMessage

def get_admin_approve_flex(report, admin_id):
    return FlexSendMessage(
        alt_text="回報文審核",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "text", "text": "--申請回報文--", "weight": "bold", "size": "md", "color": "#7D5FFF"},
                    {"type": "separator"},
                    {"type": "text", "text": f"🌸 暱稱：{report.nickname}"},
                    {"type": "text", "text": f"      個人編號：{report.member_id}"},
                    {"type": "text", "text": f"🔗 LINE ID：{report.line_id}"},
                    {"type": "text", "text": f"網址：{report.url}", "wrap": True},
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "spacing": "md",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "通過",
                            "data": f"report_approve:{report.id}:{admin_id}"
                        },
                        "style": "primary",
                        "color": "#A3DEE6"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "拒絕",
                            "data": f"report_reject:{report.id}:{admin_id}"
                        },
                        "style": "secondary",
                        "color": "#FFB6B6"
                    }
                ]
            }
        }
    )

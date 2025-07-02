from linebot.models import FlexSendMessage

def get_menu_carousel():
    bubbles = []

    # 第一頁
    bubbles.append({
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {"type": "text", "text": "🌸 茗殿功能選單 1/2", "weight": "bold", "size": "lg", "align": "center", "color": "#7D5FFF"},
                {"type": "separator"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "📱 驗證資訊", "text": "驗證資訊"},
                            "style": "primary",
                            "color": "#FFB6B6"
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🎁 每日抽獎", "text": "每日抽獎"},
                            "style": "primary",
                            "color": "#A3DEE6"
                        },
                        {
                            "type": "button",
                            "action": {"type": "uri", "label": "📬 預約諮詢", "uri": "https://line.me/ti/p/g7TPO_lhAL"},
                            "style": "primary",
                            "color": "#B889F2"
                        },
                        {
                            "type": "button",
                            "action": {"type": "uri", "label": "📅 每日班表", "uri": "https://t.me/+LaFZixvTaMY3ODA1"},
                            "style": "secondary",
                            "color": "#FFF8B7"
                        },
                        {
                            "type": "button",
                            "action": {"type": "uri", "label": "🌸 茗殿討論區", "uri": "https://line.me/ti/g2/mq8VqBIVupL1lsIXuAulnqZNz5vw7VKrVYjNDg?utm_source=invitation&utm_medium=link_copy&u[...]"},
                            "style": "primary",
                            "color": "#FFDCFF"
                        }
                    ]
                }
            ]
        }
    })

    # 第二頁
    bubbles.append({
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {"type": "text", "text": "🌸 茗殿功能選單 2/2", "weight": "bold", "size": "lg", "align": "center", "color": "#7D5FFF"},
                {"type": "separator"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "📝 回報文登記", "text": "回報文"},
                            "style": "primary",
                            "color": "#F7B7A3"
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🛎️ 呼叫管理員", "text": "呼叫管理員"},
                            "style": "secondary",
                            "color": "#B1E1FF"
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "📖 查詢規則", "text": "規則查詢"},
                            "style": "secondary",
                            "color": "#C8C6A7"
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "💰 我的券紀錄", "text": "券紀錄"},
                            "style": "primary",
                            "color": "#A3DEA6"
                        },
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "🔔 活動快訊", "text": "活動快訊"},
                            "style": "primary",
                            "color": "#FFC2C2"
                        }
                    ]
                }
            ]
        }
    })

    return FlexSendMessage(
        alt_text="主功能選單",
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )

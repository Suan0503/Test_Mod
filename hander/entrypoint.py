from linebot.models import MessageEvent, TextMessage
from extensions import handler
from hander.verify import handle_verify
from hander.report import handle_report
from hander.admin import handle_admin
from hander.menu import handle_menu

@handler.add(MessageEvent, message=TextMessage)
def entrypoint(event):
    # 依據內容分派給不同的功能
    user_text = event.message.text.strip()

    # 先給管理員指令最高優先
    if user_text.startswith("/msg "):
        handle_admin(event)
        return

    # 回報文流程
    if user_text in ["回報文", "report", "Report"]:
        handle_report(event)
        return

    # 主選單、驗證資訊、每日抽獎等
    if user_text in ["主選單", "功能選單", "選單", "menu", "Menu", "驗證資訊", "每日抽獎"]:
        handle_menu(event)
        return

    # 先判斷是否進入驗證流程（手機號、LINE ID、截圖等）
    handle_verify(event)

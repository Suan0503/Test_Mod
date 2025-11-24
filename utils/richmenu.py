import logging
from datetime import datetime
from linebot.models import RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, PostbackAction
from extensions import line_bot_api, db
from models import RichMenuBinding

# Rich Menu 狀態常數
RICHMENU_STATES = ["DEFAULT", "VERIFIED", "ADMIN"]

# 全域快取：state -> rich_menu_id
_richmenu_cache = {}


def _build_menu_definition(state: str) -> RichMenu:
    """依狀態建立 RichMenu 物件（僅結構，不上傳圖片）。可視需要調整區塊與 actions。"""
    # 統一使用 2500x843 尺寸
    size = RichMenuSize(width=2500, height=843)
    # 基本區域切 6 塊（示意）
    areas = []
    w_each = 2500 // 3
    h_each = 843 // 2
    # 6 個功能位依狀態不同設置動作
    # DEFAULT: 驗證資訊 / 重新驗證 / 主選單 / 呼叫管理員 / 活動快訊 / 每日抽獎
    # VERIFIED: 主選單 / 驗證資訊 / 每日抽獎 / 券紀錄 / 活動快訊 / 呼叫管理員
    # ADMIN: 驗證資訊 / 手動驗證 / 主選單 / 活動快訊 / 廣告專區 / 呼叫管理員
    state_actions_map = {
        "DEFAULT": [
            ("驗證資訊", "action=verify_info"),
            ("重新驗證", "action=reverify"),
            ("主選單", "action=main_menu"),
            ("呼叫管理員", "action=call_admin"),
            ("活動快訊", "action=activity"),
            ("每日抽獎", "action=daily_draw"),
        ],
        "VERIFIED": [
            ("主選單", "action=main_menu"),
            ("驗證資訊", "action=verify_info"),
            ("每日抽獎", "action=daily_draw"),
            ("券紀錄", "action=coupon_list"),
            ("活動快訊", "action=activity"),
            ("呼叫管理員", "action=call_admin"),
        ],
        "ADMIN": [
            ("驗證資訊", "action=verify_info"),
            ("手動驗證", "action=admin_manual_verify"),
            ("主選單", "action=main_menu"),
            ("活動快訊", "action=activity"),
            ("廣告專區", "action=ad_zone"),
            ("呼叫管理員", "action=call_admin"),
        ],
    }
    actions = state_actions_map.get(state, [])
    for idx, (label, data) in enumerate(actions):
        col = idx % 3
        row = idx // 3
        bounds = RichMenuBounds(x=col * w_each, y=row * h_each, width=w_each, height=h_each)
        area = RichMenuArea(bounds=bounds, action=PostbackAction(label=label, data=data, display_text=label))
        areas.append(area)
    return RichMenu(
        size=size,
        selected=False,
        name=f"RM_{state}",
        chat_bar_text="功能選單",
        areas=areas,
    )


def ensure_rich_menus():
    """確保三種狀態的 RichMenu 已建立，若無則建立並回傳 mapping。"""
    global _richmenu_cache
    if _richmenu_cache:
        return _richmenu_cache
    try:
        # 先列出所有既有 RichMenu
        existing = line_bot_api.get_rich_menu_list()
        exist_by_name = {rm.name: rm for rm in existing}
        mapping = {}
        for state in RICHMENU_STATES:
            name = f"RM_{state}"
            if name in exist_by_name:
                mapping[state] = exist_by_name[name].rich_menu_id
            else:
                # 建立新 RichMenu
                rm_def = _build_menu_definition(state)
                rich_menu_id = line_bot_api.create_rich_menu(rm_def)
                mapping[state] = rich_menu_id
                logging.info(f"Created RichMenu for state={state} id={rich_menu_id}")
        _richmenu_cache = mapping
        return mapping
    except Exception:
        logging.exception("ensure_rich_menus failed")
        return {}


def switch_rich_menu(line_user_id: str, state: str):
    """切換使用者的 RichMenu：綁定 state 對應的 rich_menu_id。"""
    if not line_user_id or not state:
        return False
    menus = ensure_rich_menus()
    rich_menu_id = menus.get(state)
    if not rich_menu_id:
        logging.warning(f"No rich_menu_id for state={state}")
        return False
    try:
        line_bot_api.link_rich_menu_to_user(line_user_id, rich_menu_id)
        # 記錄/更新 DB 綁定
        rec = RichMenuBinding.query.filter_by(line_user_id=line_user_id).first()
        if not rec:
            rec = RichMenuBinding()
            rec.line_user_id = line_user_id
            rec.state = state
            rec.rich_menu_id = rich_menu_id
            db.session.add(rec)
        else:
            rec.state = state
            rec.rich_menu_id = rich_menu_id
            rec.updated_at = datetime.utcnow()
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        logging.exception("switch_rich_menu failed")
        return False
# end of file

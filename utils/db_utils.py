"""
utils/db_utils.py
<<<<<<< HEAD
- 提供 update_or_create_whitelist_from_data 函式：根據傳入的 data 與 user_id 建立或更新 Whitelist 紀錄
=======

- 提供 update_or_create_whitelist_from_data 函式：
  根據傳入的 data 與 user_id 建立或更新 Whitelist 紀錄，
  會盡量處理 race condition（IntegrityError）並在必要時做回滾與重試。
- 匯入方式採用明確子模組與 extensions.db（避免依賴 models.__init__ 的副作用）。
- 使用 logging 取代 print，並在 DB 操作異常時確保 rollback。
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
"""
from datetime import datetime
from typing import Tuple, Optional
import logging
import pytz
<<<<<<< HEAD
=======

>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
from sqlalchemy.exc import IntegrityError
from extensions import db
from models.whitelist import Whitelist

<<<<<<< HEAD
=======
from extensions import db
from models.whitelist import Whitelist

>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
logger = logging.getLogger(__name__)
TZ = pytz.timezone("Asia/Taipei")


def _now():
<<<<<<< HEAD
=======
    # 統一使用具時區的現在時間
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
    return datetime.now(TZ)


def _safe_commit():
<<<<<<< HEAD
=======
    """
    嘗試 commit，若失敗則 rollback 並重新拋出例外。
    """
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
    try:
        db.session.commit()
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            logger.exception("rollback failed")
        raise


<<<<<<< HEAD
def update_or_create_whitelist_from_data(data: dict, user_id: str, reverify: bool = False) -> Tuple[Optional[Whitelist], bool]:
    if not user_id:
        raise ValueError("user_id is required")
    phone: Optional[str] = data.get("phone")
    is_new = False
=======
def update_or_create_whitelist_from_data(data: dict, user_id: str, reverify: bool = False) -> Tuple[Whitelist, bool]:
    """
    根據 data 內容建立或更新 Whitelist 紀錄。

    :param data: 用戶資料 dict，建議至少包含 "phone"；可包含 "name", "line_id", "date" 等欄位
    :param user_id: LINE user id（會寫入 Whitelist.line_user_id）
    :param reverify: 是否為重新驗證（若為 True，會重設 created_at 並以當前 user_id 為 line_user_id）
    :return: (record, is_new) —— record 為 Whitelist 實例，is_new 表示是否為新建立的紀錄
    """
    if not user_id:
        raise ValueError("user_id is required")

    phone: Optional[str] = data.get("phone")
    is_new = False

    # 1) 優先以 line_user_id 找（若使用者已綁定過）
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
    try:
        record = Whitelist.query.filter_by(line_user_id=user_id).first()
    except Exception:
        logger.exception("Query by line_user_id failed")
        record = None
<<<<<<< HEAD
    if record:
=======

    if record:
        # 已有以 line_user_id 為 key 的紀錄，依 reverify 或補全欄位處理
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
        try:
            if reverify:
                record.phone = data.get("phone", record.phone)
                record.name = data.get("name", record.name)
                record.line_id = data.get("line_id", record.line_id)
                record.created_at = _now()
                _safe_commit()
            else:
                updated = False
                if (not record.phone) and data.get("phone"):
                    record.phone = data["phone"]
                    updated = True
                if (not record.name) and data.get("name"):
                    record.name = data["name"]
                    updated = True
                if (not record.line_id) and data.get("line_id"):
                    record.line_id = data["line_id"]
                    updated = True
                if updated:
                    _safe_commit()
            return record, is_new
        except Exception:
            logger.exception("Update existing record by line_user_id failed")
            raise
<<<<<<< HEAD
=======

    # 2) 若沒有以 line_user_id 找到，嘗試以 phone 找（可避免 unique constraint 衝突）
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde
    existing_by_phone = None
    if phone:
        try:
            existing_by_phone = Whitelist.query.filter_by(phone=phone).first()
        except Exception:
            logger.exception("Query by phone failed")
            existing_by_phone = None

    if existing_by_phone:
        try:
            if reverify:
                existing_by_phone.name = data.get("name", existing_by_phone.name)
                existing_by_phone.line_id = data.get("line_id", existing_by_phone.line_id)
                existing_by_phone.line_user_id = user_id
                existing_by_phone.created_at = _now()
                _safe_commit()
            else:
                updated = False
                if (not existing_by_phone.name) and data.get("name"):
                    existing_by_phone.name = data["name"]
                    updated = True
                if (not existing_by_phone.line_id) and data.get("line_id"):
                    existing_by_phone.line_id = data["line_id"]
                    updated = True
                if (not existing_by_phone.line_user_id):
                    existing_by_phone.line_user_id = user_id
                    updated = True
                if updated:
                    _safe_commit()
            return existing_by_phone, False
        except Exception:
            logger.exception("Update existing record by phone failed")
            raise

<<<<<<< HEAD
    # 3) 若 phone 也沒找到，建立新紀錄（只傳正確欄位）
    if not record and not existing_by_phone:
        try:
            new_record = Whitelist()
            for key in ["phone", "name", "line_id", "line_user_id", "date", "reason", "identifier", "email", "note"]:
                if key == "line_user_id":
                    setattr(new_record, key, user_id)
                elif data.get(key) is not None:
                    setattr(new_record, key, data.get(key))
            db.session.add(new_record)
            _safe_commit()
            is_new = True
            return new_record, is_new
        except IntegrityError:
            db.session.rollback()
            logger.exception("IntegrityError on create Whitelist")
            raise
        except Exception:
            db.session.rollback()
            logger.exception("Create Whitelist failed")
            raise
    # 若都沒建立，回傳 None, False
    return None, False
=======
    # 3) 若仍無符合的紀錄，嘗試建立新紀錄（處理 race condition）
    new_record = Whitelist(
        phone=phone,
        name=data.get("name"),
        line_id=data.get("line_id"),
        line_user_id=user_id,
        created_at=_now()
    )
    db.session.add(new_record)
    try:
        _safe_commit()
        is_new = True
        return new_record, is_new
    except IntegrityError:
        # 可能因為同時插入相同 phone 而衝突，回滾並嘗試以 phone 找回那筆紀錄再更新
        logger.warning("IntegrityError on insert Whitelist, trying fallback by phone")
        try:
            db.session.rollback()
        except Exception:
            logger.exception("rollback failed after IntegrityError")

        fallback = None
        if phone:
            try:
                fallback = Whitelist.query.filter_by(phone=phone).first()
            except Exception:
                logger.exception("Fallback query by phone failed")
                fallback = None

        if fallback:
            try:
                if reverify:
                    fallback.name = data.get("name", fallback.name)
                    fallback.line_id = data.get("line_id", fallback.line_id)
                    fallback.line_user_id = user_id
                    fallback.created_at = _now()
                    _safe_commit()
                else:
                    updated = False
                    if (not fallback.name) and data.get("name"):
                        fallback.name = data["name"]
                        updated = True
                    if (not fallback.line_id) and data.get("line_id"):
                        fallback.line_id = data["line_id"]
                        updated = True
                    if (not fallback.line_user_id):
                        fallback.line_user_id = user_id
                        updated = True
                    if updated:
                        _safe_commit()
                return fallback, False
            except Exception:
                logger.exception("Update fallback record failed")
                raise

        # 若找不到 fallback，重新拋出例外
        logger.exception("IntegrityError but no fallback found; re-raising")
        raise
>>>>>>> 9b7284caba898d7d7f82b6ee7341173a8d5d6cde

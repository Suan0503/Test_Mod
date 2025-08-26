"""
utils/db_utils.py
- 提供 update_or_create_whitelist_from_data 函式：根據傳入的 data 與 user_id 建立或更新 Whitelist 紀錄
"""
from datetime import datetime
from typing import Tuple, Optional
import logging
import pytz
from sqlalchemy.exc import IntegrityError
from extensions import db
from models.whitelist import Whitelist

logger = logging.getLogger(__name__)
TZ = pytz.timezone("Asia/Taipei")


def _now():
    return datetime.now(TZ)


def _safe_commit():
    try:
        db.session.commit()
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            logger.exception("rollback failed")
        raise


def update_or_create_whitelist_from_data(data: dict, user_id: str, reverify: bool = False) -> Tuple[Optional[Whitelist], bool]:
    if not user_id:
        raise ValueError("user_id is required")
    phone: Optional[str] = data.get("phone")
    is_new = False
    try:
        record = Whitelist.query.filter_by(line_user_id=user_id).first()
    except Exception:
        logger.exception("Query by line_user_id failed")
        record = None
    if record:
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

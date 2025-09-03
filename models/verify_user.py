from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    line_user_id = Column(String(64), unique=True, nullable=False)
    phone = Column(String(16))
    line_id = Column(String(64))
    name = Column(String(64))  # 新增，LINE個人暱稱
    screenshot_url = Column(String(256))
    status = Column(String(32), default='pending')  # whitelist, blacklist, pending
    reason = Column(String(128))  # 黑名單原因（可選）
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

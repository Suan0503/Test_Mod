from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Coupon(Base):
    __tablename__ = 'coupons'
    id = Column(Integer, primary_key=True)
    line_user_id = Column(String(64), nullable=False)
    amount = Column(Integer, default=0)
    date = Column(String(16))
    type = Column(String(16))  # draw, report
    report_no = Column(String(32))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

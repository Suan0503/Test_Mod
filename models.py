from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OCRRecord(Base):
    __tablename__ = 'ocr_records'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    text = Column(String)

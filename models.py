{\rtf1\ansi\ansicpg950\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from flask_sqlalchemy import SQLAlchemy\
from datetime import datetime\
\
db = SQLAlchemy()\
\
class Whitelist(db.Model):\
    __tablename__ = "whitelist"\
    id = db.Column(db.Integer, primary_key=True)\
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)\
    date = db.Column(db.String(20))\
    phone = db.Column(db.String(20), unique=True)\
    reason = db.Column(db.Text)\
    name = db.Column(db.String(255))\
    line_id = db.Column(db.String(100))\
    line_user_id = db.Column(db.String(255), unique=True)\
\
class Blacklist(db.Model):\
    __tablename__ = "blacklist"\
    id = db.Column(db.Integer, primary_key=True)\
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)\
    date = db.Column(db.String(20))\
    phone = db.Column(db.String(20), unique=True)\
    reason = db.Column(db.Text)\
    name = db.Column(db.String(255))\
\
class Coupon(db.Model):\
    __tablename__ = "coupon"\
    id = db.Column(db.Integer, primary_key=True)\
    line_user_id = db.Column(db.String(255))\
    date = db.Column(db.String(20))\
    amount = db.Column(db.Integer)\
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)}
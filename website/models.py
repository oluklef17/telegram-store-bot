from enum import unique
from . import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()
DB_NAME = "database.db"

class User (db.Model):
    user_id     = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(150), unique=True)
    exp_date    = db.Column(db.DateTime(timezone=True))

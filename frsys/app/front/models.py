# coding: utf-8
from exts import db
from werkzeug.security import generate_password_hash, check_password_hash
import shortuuid
from datetime import datetime
import time


class FrontUser(db.Model):
    __tablename__ = 'front_user'
    id = db.Column(db.String(100), primary_key=True, default=shortuuid.uuid)
    showid = db.Column(db.Integer, nullable=False, default=int(time.time()*10)%1000000)
    username = db.Column(db.String(20), nullable=False)
    _password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    realname = db.Column(db.String(50),nullable=False)
    join_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, *args, **kwargs):
        if "password" in kwargs:
            self.password = kwargs.get('password')
            kwargs.pop("password")
        super(FrontUser, self).__init__(*args,**kwargs)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password):
        self._password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


#coding: utf-8
from exts import db
from werkzeug.security import generate_password_hash, check_password_hash
import shortuuid


class CmsUser(db.Model):
    __tablename__ = 'cms_user'
    id = db.Column(db.String(100), primary_key=True, default=shortuuid.uuid)
    username = db.Column(db.String(20), nullable=False)
    _password = db.Column(db.String(150), nullable=False)


    def __init__(self,*args,**kwargs):
        if "password" in kwargs:
            self.password = kwargs.get('password')
            kwargs.pop("password")
        super(CmsUser, self).__init__(*args,**kwargs)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password):
        self._password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def __repr__(self):
        return "<CMS-User {}>".format(self.username)


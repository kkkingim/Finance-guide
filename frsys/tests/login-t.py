from flask import Flask
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://ksuser:ksssuser@v2.kk721.cn/fr_system"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

loginManager = LoginManager()
loginManager.init_app(app)
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    __tablename__ = 'uuser'
    uuid = db.Column(db.Integer , primary_key=True)
    uusername = db.Column(db.VARCHAR)
    upassword = db.Column(db.VARCHAR)

    def __repr__(self):
        return '<User %r>' % self.uusername

#
# @loginManager.user_loader
# def load_user(uid):
#     return User.get(uid)

@app.route("/")
def ind():
    print(User.query.all())
    return "ok"

app.run()


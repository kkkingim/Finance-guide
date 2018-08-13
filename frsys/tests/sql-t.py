from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from faker import Faker


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://ksuser:ksssuser@localhost:3306/fr_system?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Book(db.Model):
    __tablename__ = "book"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey("user.id"))

    author = db.relationship("User", backref="books")

#
# db.drop_all()
# db.create_all()

# user = User(name="xiaoming")
# book = Book(name="houheixue")
# book.author = user
#
# db.session.add(book)
# db.session.commit()

# a = User.query.filter(User.name == "xiaoming").first()
# if a:
#     db.session.delete(a)
#     db.session.commit()
#
faker = Faker()
l = []
u = []
for i in range(20):
    nm = faker.name().split(" ")[0]
    while nm in u:
        nm = faker.name().split(" ")[0]
    u.append(nm)
    print(nm)

    l.append(User(name=nm))


db.session.add_all(l)
db.session.commit()

@app.route('/')
def index():
    return "hello"

if __name__ == "__main__":
    app.run()
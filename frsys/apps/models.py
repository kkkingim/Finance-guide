from exts import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL(5,2), nullable=False)
    last_price = db.Column(db.DECIMAL(5,2), nullable=False)
    PE_ratio = db.Column(db.DECIMAL(5,2), nullable=False)
    total_increase = db.Column(db.DECIMAL(6,2), nullable=False)

class Grade(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    uid = db.Column(db.String(100))
    pid = db.Column(db.Integer)
    grade = db.Column(db.Integer, nullable=False)








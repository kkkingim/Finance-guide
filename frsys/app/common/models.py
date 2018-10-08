from exts import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL(5,2), nullable=False)
    last_price = db.Column(db.DECIMAL(5,2), nullable=False)
    PE_ratio = db.Column(db.DECIMAL(5,2), nullable=False)
    total_increase = db.Column(db.DECIMAL(6,2), nullable=False)

class Product_1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    last_price = db.Column(db.DECIMAL(10,2), nullable=False)
    change = db.Column(db.DECIMAL(10,2), nullable=False)
    chg = db.Column(db.DECIMAL(10,2), nullable=False)
    open = db.Column(db.DECIMAL(10,2), nullable=False)
    highest = db.Column(db.DECIMAL(10,2), nullable=False)
    lowest = db.Column(db.DECIMAL(10,2), nullable=False)
    pre_close = db.Column(db.DECIMAL(10,2), nullable=False)
    volume = db.Column(db.String(255), nullable=False)
    turnover = db.Column(db.String(255), nullable=False)

class Product_2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    last_price = db.Column(db.DECIMAL(10, 4), nullable=False)
    change = db.Column(db.DECIMAL(10, 4), nullable=False)
    chg = db.Column(db.DECIMAL(10, 2), nullable=False)
    highest = db.Column(db.DECIMAL(10, 4), nullable=False)
    lowest = db.Column(db.DECIMAL(10, 4), nullable=False)



class Grade(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    uid = db.Column(db.String(255), nullable=False)
    pid = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.Integer, nullable=False)

class Grade_1(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    uid = db.Column(db.String(255), nullable=False)
    pid = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.Integer, nullable=False)

class Grade_2(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    uid = db.Column(db.String(255), nullable=False)
    pid = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.Integer, nullable=False)



class Product_prop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prop = db.Column(db.String(255), nullable=False)

class Product_prop_1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prop = db.Column(db.String(255), nullable=False)

class Product_prop_2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prop = db.Column(db.String(255), nullable=False)




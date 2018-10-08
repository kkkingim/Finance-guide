# coding: utf-8
from flask import Blueprint, render_template, request, session, redirect, url_for
from flask.views import MethodView
from app.front.forms import RegForm, LoginForm
from app.front.models import FrontUser as User, db
from .decorators import login_required
from .models import FrontUser
from app.common.models import Product, Product_1, Product_2
from app.common.models import Product_prop, Product_prop_1, Product_prop_2
from app.common.models import Grade, Grade_1, Grade_2
from flask import g, jsonify
import config
from utils.Recommend_Script import pro_rec, pro_rec_1, pro_rec_2
import random

bp = Blueprint("front", __name__)


class RegView(MethodView):
    def __render(self, message=None):
        return render_template("front/register.html", message=message)

    def get(self):
        return self.__render()

    def post(self):
        form = RegForm(request.form)
        if form.validate():
            username = form.username.data
            email = form.email.data
            user = User.query.filter(db.or_(User.username == username,
                                     User.email == email)).first()
            if not user:
                password = form.password.data
                realname = form.realname.data
                user = User(username=username, password=password, email=email, realname=realname)
                db.session.add(user)
                db.session.commit()

                user = User.query.filter(User.username == username).first()

                if request.form.get("rememberme") == "remember-me":
                    session.permanent = True
                session["uid"] = user.id
                return redirect(url_for("front.index"))
            else:
                return self.__render("用户名或邮箱已存在")

        s = form.get_error()
        s = '<br/>'.join([i for i in s])
        return self.__render(s)


class LoginView(MethodView):
    def __render(self, message=None):
        return render_template("front/login.html", message=message)

    def get(self):
        return self.__render()

    def post(self):
        form = LoginForm(request.form)
        if form.validate():
            user = User.query.filter(User.username == form.username.data).first()
            if user and user.check_password(form.password.data):
                if request.form.get("rememberme") == "remember-me":
                    session.permanent = True
                session["uid"] = user.id
                next = request.args.get("next", "")
                if next:
                    return redirect(next)
                else:
                    return redirect(url_for("front.index"))
            else:
                return self.__render("用户名或密码错误")
        s = form.get_error()
        s = '<br/>'.join([i for i in s])
        return self.__render(s)


@bp.route('/')
def index():
    if "uid" in session:
        user = FrontUser.query.filter(FrontUser.id == session['uid']).first()

        if user:
            g.current_user = user

    products = []
    for pid in pro_rec.productRank[:10]:
        product = Product.query.filter(Product.id == pid).first()
        products += [product]

    products_1 = []
    for pid in pro_rec_1.productRank[:10]:
        product = Product_1.query.filter(Product_1.id == pid).first()
        products_1 += [product]

    products_2 = []
    for pid in pro_rec_2.productRank[:10]:
        product = Product_2.query.filter(Product_2.symbol == pid).first()
        products_2 += [product]

    context = {
        'products': products,
        'products_1': products_1,
        'products_2': products_2,
    }
    return render_template('front/index.html', **context)


@bp.route("/logout/")
@login_required
def logout():
    del session["uid"]
    return redirect(url_for("front.index"))


@bp.route("/personal/")
@login_required
def personal_view():
    view_type = request.args.get("type", "1")
    if view_type == "2":
        tp = "债券"
    elif view_type == "3":
        tp = "外汇"
    else:
        tp = "股票"

    user = FrontUser.query.filter(FrontUser.id == session['uid']).first()

    if user:
        g.current_user = user
    else:
        return redirect(url_for("front.login"))

    def get_lastgrade(vt):
        infos = []
        if vt == "2":
            grades = Grade_1.query.filter(Grade_1.uid == user.id).all()
            for grade in grades[::-1]:
                theg = grade.grade
                p = Product_1.query.filter(Product_1.id == grade.pid).first()
                if p:
                    l = {
                        "pid": p.id,
                        "productname": p.name,
                        "grade": theg
                    }
                    infos.append(l)
                    if len(infos) == 20:
                        break
        elif vt == "3":
            grades = Grade_2.query.filter(Grade_2.uid == user.id).all()
            for grade in grades[::-1]:
                theg = grade.grade
                p = Product_2.query.filter(Product_2.symbol == grade.pid).first()
                if p:
                    l = {
                        "pid": p.symbol,
                        "productname": p.name,
                        "grade": theg
                    }
                    infos.append(l)
                    if len(infos) == 20:
                        break
        else:
            grades = Grade.query.filter(Grade.uid == user.id).all()
            for grade in grades[::-1]:
                theg = grade.grade
                p = Product.query.filter(Product.id == grade.pid).first()
                if p:
                    l = {
                        "pid": p.id,
                        "productname": p.name,
                        "grade": theg
                    }
                    infos.append(l)
                    if len(infos) == 20:
                        break

        return infos

    infos = get_lastgrade(view_type)
    products = []
    if view_type == "2":
        for pid in pro_rec_1.get_timelyRec(session['uid'])[:10]:
            product = Product_1.query.filter(Product_1.id == pid).first()
            products += [product]
    elif view_type == "3":
        for pid in pro_rec_2.get_timelyRec(session['uid'])[:10]:
            product = Product_2.query.filter(Product_2.symbol == pid).first()
            products += [product]
    else:
        for pid in pro_rec.get_timelyRec(session['uid'])[:10]:
            product = Product.query.filter(Product.id == pid).first()
            products += [product]

    col = len(infos)//5 if len(infos)%5 == 0 else len(infos)//5 + 1

    context = {
        'grade_list': [infos[i*5:i*5+5] for i in range(col)],
        'products': products,
        'current_type': tp
    }
    return render_template("front/personal.html", **context)


@bp.route("/products/")
@login_required
def products_view():
    tp = request.args.get("type","")


    user = FrontUser.query.filter(FrontUser.id == session['uid']).first()
    if user:
        g.current_user = user
    else:
        return redirect(url_for("front.login"))

    if tp == '2':
        tmp_query = Product_1.query
        pp = Product_prop_1.query.all()
    elif tp == '3':
        tmp_query = Product_2.query
        pp = Product_prop_2.query.all()
    else:
        tmp_query = Product.query
        pp = Product_prop.query.all()

    wd = request.args.get("wd", "")
    if wd:
        t = '%{}%'.format(wd)
        if tp == '3':
            tmp_query = tmp_query.filter(db.or_(Product_2.symbol.like(t), Product_2.name.like(t)))
        elif tp == '2':
            tmp_query = tmp_query.filter(db.or_(Product_1.id.like(t), Product_1.name.like(t)))
        else:
            tmp_query = tmp_query.filter(db.or_(Product.id.like(t), Product.name.like(t)))

    amt = tmp_query.count()
    page = int(request.values.get("page", 1))
    if page < 1:
        page = 1
    elif page > amt // config.ROW_PER_PAGE:
        page = amt // config.ROW_PER_PAGE
        if amt % config.ROW_PER_PAGE != 0:
            page += 1

    if page < 1:
        page = 1

    last_page = amt // config.ROW_PER_PAGE
    if amt % config.ROW_PER_PAGE != 0:
        last_page += 1

    if amt == 0:
        products = []
    else:
        if tp == '2':
            products = tmp_query.order_by(Product_1.name).offset((page - 1) * config.ROW_PER_PAGE)[:config.ROW_PER_PAGE]
        elif tp == '3':
            products = tmp_query.order_by(Product_2.name).offset((page - 1) * config.ROW_PER_PAGE)[:config.ROW_PER_PAGE]
        else:
            products = tmp_query.order_by(Product.name).offset((page - 1) * config.ROW_PER_PAGE)[:config.ROW_PER_PAGE]


    context = {
        'products': products,
        'wd' :wd,
        'current_page': page,
        'last_page': last_page,
        'pp': pp,
        'tp': tp
    }

    return render_template("front/products.html", **context)


@bp.route("/dailyrec/")
@login_required
def dailyrec_view():
    tp = request.args.get("type", "")
    user = FrontUser.query.filter(FrontUser.id == session['uid']).first()
    if user:
        g.current_user = user
    else:
        return redirect(url_for("front.login"))

    products = []
    if tp == '2':
        pp = Product_prop_1.query.all()
        for pid in pro_rec_1.get_user_dailyRec(session["uid"]):
            product = Product_1.query.filter(Product_1.id == pid).first()
            products += [product]

    elif tp == '3':
        pp = Product_prop_2.query.all()
        for pid in pro_rec_2.get_user_dailyRec(session["uid"]):
            product = Product_2.query.filter(Product_2.symbol == pid).first()
            products += [product]
    else:
        pp = Product_prop.query.all()
        for pid in pro_rec.get_user_dailyRec(session["uid"]):
            product = Product.query.filter(Product.id == pid).first()
            products += [product]


    context = {
        'products': products,
        'pp': pp,
        'tp': tp
    }

    return render_template("front/dailyRec.html", **context)


@bp.route("/product/<id>/")
def product_detail(id):
    product = Product.query.filter(Product.id == id).first()
    t= 0
    pp = Product_prop.query.all()
    if not product:
        product = Product_1.query.filter(Product_1.id == id).first()
        t= 1
        pp = Product_prop_1.query.all()
        if not product:
            product = Product_2.query.filter(Product_2.symbol == id).first()
            t = 2
            pp = Product_prop_2.query.all()

    if product:
        l = []
        if t == 0:
            for i in range(1,6):
                gd = Grade.query.filter(Grade.pid == id).filter(Grade.grade == i).count()
                l += [gd]
        elif t==1:
            for i in range(1,6):
                gd = Grade_1.query.filter(Grade_1.pid == id).filter(Grade_1.grade == i).count()
                l += [gd]
        else:
            for i in range(1,6):
                gd = Grade_2.query.filter(Grade_2.pid == id).filter(Grade_2.grade == i).count()
                l += [gd]



        return render_template("front/product.html", product = product, t=t, pp= pp, grades = l)
    else:
        return "产品不存在"


@bp.route("/getinfo/", methods=["POST"])
@login_required
def get_info():
    wd = request.form.get("wd", "")
    tp = request.form.get("tp", "")
    if tp == "股票":
        if wd:
            wd = "%{}%".format(wd)
            products = Product.query.filter(db.or_(Product.id.like(wd), Product.name.like(wd))).all()[:5]
        else:
            products = Product.query.all()[:5]
        infos = [[product.id, product.name] for product in products]
    elif tp == "债券":
        if wd:
            wd = "%{}%".format(wd)
            products = Product_1.query.filter(db.or_(Product_1.id.like(wd), Product_1.name.like(wd))).all()[:5]
        else:
            products = Product_1.query.all()[:5]
        infos = [[product.id, product.name] for product in products]
    else:
        if wd:
            wd = "%{}%".format(wd)
            products = Product_2.query.filter(db.or_(Product_2.symbol.like(wd), Product_2.name.like(wd))).all()[:5]
        else:
            products = Product_2.query.all()[:5]
        infos = [[product.symbol, product.name] for product in products]

    return jsonify(infos)


@bp.route("/addusergrade/", methods=["POST"])
@login_required
def add_user_grade():
    tp = request.form.get("tp", "")
    pid = request.form.get("pid","")
    grade = request.form.get("grade","")

    uid = FrontUser.query.filter(FrontUser.id == session['uid']).first().id


    if pid and uid and grade:
        if tp == "股票":
            grade = Grade(uid=uid, pid=pid, grade=grade)
        elif tp == "债券":
            grade = Grade_1(uid=uid, pid=pid, grade=grade)
        else:
            grade = Grade_2(uid=uid, pid=pid, grade=grade)

        db.session.add(grade)
        db.session.commit()
        return jsonify({"statue": True})
    return jsonify({"statue": False})


@bp.route("/delusergrade/", methods=["POST"])
@login_required
def del_user_grade():

    pid = request.form.get("pid","")
    uid = FrontUser.query.filter(FrontUser.id == session['uid']).first().id
    if pid and uid:
        grade = Grade.query.filter(Grade.uid == uid, Grade.pid == pid).first()
        if grade:
            db.session.delete(grade)
            db.session.commit()
            return jsonify({"statue": True})
    return jsonify({"statue": False})


@bp.route("/getgrade/", methods=["POST"])
@login_required
def get_grade():
    user = FrontUser.query.filter(FrontUser.id == session['uid']).first()
    if user:
        g.current_user = user
    else:
        return jsonify({'statue': "400"})

    tmp = []
    grades = Grade.query.filter(Grade.uid == user.id).all()
    for grade in grades[::-1]:
        theg = grade.grade
        p = Product.query.filter(Product.id == grade.pid).first()
        if p :
            l = {
                "pid": p.id,
                "productname": p.name,
                "grade": theg
            }
            tmp.append(l)


    page = int(request.form.get("page"))
    infos = tmp[(page - 1) * 20:(page - 1) * 20 + 20]

    if infos == []:
        return jsonify({'page': -1})
    return jsonify({'page': page, 'data': infos})


@bp.route("/randomrec/", methods=["POST"])
@login_required
def random_rec():
    tp = request.form.get("tp", "")
    if tp == "股票":
        userproducts = Grade.query.filter(Grade.uid == session['uid']).all()
        products = Product.query.filter(Product.id.notin_([userproduct.pid for userproduct in userproducts])).all()
        products = random.choices(products, k=5)
        infos = [[product.id, product.name] for product in products]
    elif tp == "债券":
        userproducts = Grade_1.query.filter(Grade_1.uid == session['uid']).all()
        products = Product_1.query.filter(Product_1.id.notin_([userproduct.pid for userproduct in userproducts])).all()
        products = random.choices(products, k=5)
        infos = [[product.id, product.name] for product in products]
    else:
        userproducts = Grade_2.query.filter(Grade_2.uid == session['uid']).all()
        products = Product_2.query.filter(Product_2.symbol.notin_([userproduct.pid for userproduct in userproducts])).all()
        products = random.choices(products, k=5)
        infos = [[product.symbol, product.name] for product in products]

    return jsonify(infos)


# TODO 筛选已评价的产品不出现在评价弹窗内 !!!

bp.add_url_rule("/login/", view_func=LoginView.as_view("login"))
bp.add_url_rule("/register/", view_func=RegView.as_view("reg"))
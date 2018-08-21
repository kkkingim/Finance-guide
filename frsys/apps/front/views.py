# coding: utf-8
from flask import Blueprint, render_template, request, session, redirect, url_for
from flask.views import MethodView
from apps.front.forms import RegForm, LoginForm
from apps.front.models import FrontUser as User, db
from .decorators import login_required
from .models import FrontUser
from apps.models import Product, Grade, Product_1, Product_2
from flask import g, jsonify
import config

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
            user = User.query.filter(User.username == username,
                                     User.email == email).first()
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
        return self.__render(form.get_error())


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
                return self.__render("账号或密码错误")
        return self.__render(form.get_error())


class SettingView(MethodView):
    decorators = [login_required]

    def get(self):
        return "setting"

    def post(self):
        return "setting Post"


@bp.route('/')
def index():
    if "uid" in session:
        user = FrontUser.query.filter(FrontUser.id == session['uid']).first()

        if user:
            g.current_user = user

    # TODO get 10 hot product

    products = Product.query.all()[:10]
    products_1 = Product_1.query.all()[:10]
    products_2 = Product_2.query.all()[:10]

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

    def get_lastgrade():
        infos = []
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

    infos = get_lastgrade()
    print(infos)

    # TODO get 10 recommend product

    products = Product.query.all()[:10]

    col = len(infos)//5 if len(infos)%5 == 0 else len(infos)//5 + 1

    context = {
        'grade_list': [infos[i*5:i*5+5] for i in range(col)],
        'products': products,
        'current_type': tp
    }
    print(context['grade_list'])
    return render_template("front/personal.html", **context)

@bp.route("/products/")
@login_required
def products_view():
    user = FrontUser.query.filter(FrontUser.id == session['uid']).first()
    if user:
        g.current_user = user
    else:
        return redirect(url_for("front.login"))

    wd = request.args.get("wd", "")
    tmp_query = Product.query
    if wd:
        t = '%{}%'.format(wd)
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
        products = tmp_query.order_by(Product.name).offset((page - 1) * config.ROW_PER_PAGE)[
                  :config.ROW_PER_PAGE]

    context = {
        'products': products,
        'wd' :wd,
        'current_page': page,
        'last_page': last_page
    }

    return render_template("front/products.html", **context)

@bp.route("/product/<id>/")
def product_detail(id):
    pid = id
    return render_template("front/product.html", pid=pid)

@bp.route("/getinfo/", methods=["POST"])
@login_required
def get_info():
    wd = request.form.get("wd", "")
    if wd:
        wd = "%{}%".format(wd)
        products = Product.query.filter(db.or_(Product.id.like(wd), Product.name.like(wd))).all()[:5]
    else:
        products = Product.query.all()[:5]

    infos = [[product.id, product.name] for product in products]

    return jsonify(infos)

@bp.route("/addusergrade/", methods=["POST"])
@login_required
def add_user_grade():

    pid = request.form.get("pid","")
    grade = request.form.get("grade","")
    uid = FrontUser.query.filter(FrontUser.id == session['uid']).first().id
    if pid and uid and grade:
        grade = Grade(uid=uid, pid=pid, grade=grade)
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
    products = Product.query.all()[:5]

    infos = [[product.id, product.name] for product in products]

    return jsonify(infos)

#TODO 筛选已评价的产品不出现在评价弹窗内 !!!

bp.add_url_rule("/login/", view_func=LoginView.as_view("login"))
bp.add_url_rule("/register/", view_func=RegView.as_view("reg"))
bp.add_url_rule("/setting/", view_func=SettingView.as_view("setting"))
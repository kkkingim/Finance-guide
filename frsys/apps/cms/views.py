from flask import Blueprint, render_template, request, session, redirect, url_for, g, jsonify
from .decorators import login_required
from flask.views import MethodView
from .forms import cms_login_form, update_info_form, cms_user_add_form
from .models import CmsUser, db
from apps.front.models import FrontUser
from apps.models import Product, Grade
from apps.front.forms import RegForm
import config

from datetime import datetime, timedelta
import os
from threading import Thread
# from utils import rd

bp = Blueprint("cms", __name__, url_prefix="/cms")


# login View
class LoginView(MethodView):

    def __render(self, message=None):
        return render_template("cms/login.html", tip=message)

    def get(self):
        return self.__render()

    def post(self):
        form = cms_login_form(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data
            user = CmsUser.query.filter(CmsUser.username == username).first()
            if user and user.check_password(password):
                session.permanent = True
                session["cms_uid"] = user.id
                next = request.args.get("next", "")
                if next:
                    return redirect(next)
                else:
                    return redirect(url_for("cms.index"))
            return self.__render("账号密码错误")
        return self.__render(form.get_error())


# logout View
@bp.route('/logout/')
@login_required
def logout():
    del session["cms_uid"]
    return redirect(url_for('cms.login'))


# cms_index View
@bp.route('/')
@login_required
def index():
    run_time = datetime.now() - config.RUN_START_TIME

    run_time = "{} days {}:{:0>2}:{}".format(run_time.days, run_time.seconds // 3600, run_time.seconds % 3600 // 60,
                                             run_time.seconds % 60)

    context = {
        'comment': Grade.query.count(),
        'user_amount': FrontUser.query.count(),
        'data_amount': Product.query.count(),
        'run_time': run_time
    }
    return render_template("cms/index.html", **context)


'''
########################
Front User Manager Views
########################
'''


# user_mgr View
@bp.route('/usermgr/')
@login_required
def user_mgr():
    wd = request.args.get("wd", "")
    tmp_query = FrontUser.query
    if wd:
        t = '%{}%'.format(wd)
        tmp_query = tmp_query.filter(db.or_(FrontUser.username.like(t), FrontUser.email.like(t)))

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
        f_users = []
    else:
        f_users = tmp_query.order_by(FrontUser.username).offset((page - 1) * config.ROW_PER_PAGE)[
                  :config.ROW_PER_PAGE]

    return render_template("cms/user_mgr.html", users=f_users, rpp=config.ROW_PER_PAGE, current_page=page,
                           last_page=last_page, wd=wd)


# reset_password
@bp.route('/resetuserpwd/', methods=["POST"])
@login_required
def reset_password():
    uid = request.form.get("id", "")
    n_pwd = request.form.get("pwd", "")
    user = FrontUser.query.filter(FrontUser.id == uid).first()
    if user:
        user.password = n_pwd
        db.session.commit()
        return jsonify({"statue": True})
    else:
        return jsonify({"statue": False})


# update_info
@bp.route('/updateuserinfo/', methods=["POST"])
@login_required
def update_user_info():
    uid = request.form.get("id", "")
    user = FrontUser.query.filter(FrontUser.id == uid).first()
    if user:
        form = update_info_form(request.form)
        if form.validate():
            user.username = form.username.data
            user.email = form.email.data
            user.realname = form.realname.data
            db.session.commit()
            return jsonify({"statue": True})
        print(form.get_error())
    return jsonify({"statue": False})


# del_user
@bp.route('/deluser/', methods=["POST"])
@login_required
def del_user():
    uid = request.form.get("id", "")
    user = FrontUser.query.filter(FrontUser.id == uid).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"statue": True})
    else:
        return jsonify({"statue": False})


# add_user
@bp.route('/adduser/', methods=["POST"])
@login_required
def add_user():
    form = RegForm(request.form)
    if form.validate():
        user = FrontUser(username=form.username.data, password=form.password.data, email=form.email.data,
                         realname=form.realname.data)
        db.session.add(user)
        db.session.commit()
        return jsonify({"statue": True})
    return jsonify({"statue": False, "error": form.get_error()})


# del_users
@bp.route('/delusers/', methods=["POST"])
@login_required
def del_users():
    uids = request.form.get("uid_list", "")
    uids = uids.split(",")
    users = [FrontUser.query.filter(FrontUser.id == uid).first() for uid in uids]
    if users:
        for user in users:
            if user:
                db.session.delete(user)
        db.session.commit()
        return jsonify({"statue": True})
    else:
        return jsonify({"statue": False})


'''
######################
CMS User Manager Views
######################
'''


# cms_user_mgr View
@bp.route('/cmsusermgr/')
@login_required
def cms_user_mgr():
    wd = request.args.get("wd", "")
    tmp_query = CmsUser.query
    if wd:
        t = '%{}%'.format(wd)
        tmp_query = tmp_query.filter(CmsUser.username.like(t))

    amt = tmp_query.count()
    page = int(request.values.get("page", 1))
    if page < 1:
        page = 1
    elif page > amt // config.ROW_PER_PAGE:
        page = amt // config.ROW_PER_PAGE
        if amt % config.ROW_PER_PAGE != 0:
            page += 1

    last_page = amt // config.ROW_PER_PAGE
    if amt % config.ROW_PER_PAGE != 0:
        last_page += 1

    if page < 1:
        page = 1

    c_users = tmp_query.order_by(CmsUser.username).offset((page - 1) * config.ROW_PER_PAGE)[:config.ROW_PER_PAGE]

    return render_template("cms/cms_user_mgr.html", users=c_users, rpp=config.ROW_PER_PAGE, current_page=page,
                           last_page=last_page, wd=wd)


# del_cms_user
@bp.route('/delcmsuser/', methods=["POST"])
@login_required
def del_cms_user():
    uid = request.form.get("id", "")
    user = CmsUser.query.filter(CmsUser.id == uid).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        if uid == session["cms_uid"]:
            del session["cms_uid"]
        return jsonify({"statue": True})
    else:
        return jsonify({"statue": False})


# reset_cms_password
@bp.route('/resetcmsuserpwd/', methods=["POST"])
@login_required
def reset_cms_password():
    uid = request.form.get("id", "")
    n_pwd = request.form.get("pwd", "")
    user = CmsUser.query.filter(CmsUser.id == uid).first()
    if user:
        user.password = n_pwd
        db.session.commit()

        if uid == session["cms_uid"]:
            del session["cms_uid"]
            return jsonify({"statue": True, "reload": True})
        return jsonify({"statue": True, "reload": False})
    else:
        return jsonify({"statue": False})


# add_cms_user
@bp.route('/addcmsuser/', methods=["POST"])
@login_required
def add_cms_user():
    form = cms_user_add_form(request.form)
    if form.validate():
        user = CmsUser(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return jsonify({"statue": True})
    return jsonify({"statue": False, "error": form.get_error()})


# del_cms_users
@bp.route('/delcmsusers/', methods=["POST"])
@login_required
def del_cms_users():
    uids = request.form.get("uid_list", "")
    uids = uids.split(",")
    users = [CmsUser.query.filter(CmsUser.id == uid).first() for uid in uids]
    if users:
        for user in users:
            if user:
                db.session.delete(user)

        db.session.commit()
        if session['cms_uid'] in uids:
            del session['cms_uid']
        return jsonify({"statue": True})
    else:
        return jsonify({"statue": False})


'''
######################
    Data Info View
######################
'''


# products view
@bp.route('/products/')
@login_required
def products_mgr():
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
        products = tmp_query.order_by(Product.id).offset((page - 1) * config.ROW_PER_PAGE)[
                   :config.ROW_PER_PAGE]

    context = {
        'products': products,
        'rpp': config.ROW_PER_PAGE,
        'current_page': page,
        'last_page': last_page,
        "wd": wd
    }

    return render_template("cms/product_mgr.html", **context)


# add_product
@bp.route('/addproduct/', methods=["POST"])
@login_required
def add_product():
    id = request.form.get('id', "")
    name = request.form.get('name', "")
    amt = request.form.get('amt', "")
    price = request.form.get('price', "")
    last_price = request.form.get('last_price', "")
    pe = request.form.get('pe', "")
    t_inc = request.form.get('t_inc', "")

    if not Product.query.filter(Product.id == id).first():
        product = Product(id=id, name=name, amount=amt, price=price, last_price=last_price, PE_ratio=pe,
                          total_increase=t_inc)
        db.session.add(product)
        db.session.commit()
        return jsonify({"statue": True})
    return jsonify({"statue": False, "error": "股票代码已存在"})


# del_products
@bp.route('/delproducts/', methods=["POST"])
@login_required
def del_products():
    ids = request.form.get("id_list", "")
    ids = ids.split(",")
    products = [Product.query.filter(Product.id == id).first() for id in ids]
    if products:
        for product in products:
            if product:
                db.session.delete(product)
        db.session.commit()
        return jsonify({"statue": True})
    else:
        return jsonify({"statue": False})


# del_product
@bp.route('/delproduct/', methods=["POST"])
@login_required
def del_product():
    id = request.form.get("id", "")
    product = Product.query.filter(Product.id == id).first()
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"statue": True})
    else:
        return jsonify({"statue": False})


# update_info
@bp.route('/updateproductinfo/', methods=["POST"])
@login_required
def update_product_info():
    id = request.form.get("id", "")
    name = request.form.get("name", "")
    amt = request.form.get("amt", "")
    price = request.form.get("price", "")
    last_price = request.form.get("last_price", "")
    pe = request.form.get("pe", "")
    t_inc = request.form.get("t_inc", "")
    product = Product.query.filter(Product.id == id).first()
    if product:
        product.name = name if name != "" else product.name
        product.amount = amt if amt != "" else product.amount
        product.price = price if price != "" else product.price
        product.last_price = last_price if last_price != "" else product.last_price
        product.PE_ratio = pe if pe != "" else product.PE_ratio
        product.total_increase = t_inc if t_inc != "" else product.total_increase
        db.session.commit()
        return jsonify({"statue": True})
    return jsonify({"statue": False})


'''
######################
    User Grade View
######################
'''


@bp.route('/usergrade/')
@login_required
def user_grade_mgr():
    wd = request.args.get("wd", "")

    infos = []
    grades = Grade.query.filter(~Grade.uid.like("Vr-%")).all()
    for grade in grades:
        g = grade.grade
        p = Product.query.filter(Product.id == grade.pid).first()
        u = FrontUser.query.filter(FrontUser.id == grade.uid).first()
        if p and u:
            l = {
                "uid": u.id,
                "pid": str(p.id),
                "username": u.username,
                "productname": p.name,
                "grade": g
            }
            infos.append(l)

    if wd:
        tmp = []
        for info in infos:
            if wd in info['username'] or wd in info['pid'] or wd in info['productname']:
                tmp.append(info)

        infos = tmp

    amt = len(infos)
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

    if amt != 0:
        infos = infos[(page - 1) * config.ROW_PER_PAGE:(page - 1) * config.ROW_PER_PAGE + config.ROW_PER_PAGE]

    context = {
        'current_page': page,
        'last_page': last_page,
        'infos': infos,
        "wd": wd

    }

    return render_template("cms/user_grade_mgr.html", **context)


# add_grade
@bp.route('/addgrade/', methods=["POST"])
@login_required
def add_grade():
    uid = request.form.get('uid', "")
    pid = request.form.get('pid', "")
    grade = request.form.get('grade', "")

    user = FrontUser.query.filter(db.or_(FrontUser.id == uid, FrontUser.username == uid))
    product = Product.query.filter(db.or_(Product.id == pid, Product.name == pid))
    if user.count() == 1 and product.count() == 1:
        g = Grade(uid=user.first().id, pid=product.first().id, grade=grade)
        db.session.add(g)
        db.session.commit()
        return jsonify({"statue": True})
    return jsonify({"statue": False, "error": "输入条件不唯一,请精确输入"})


# del_grades
@bp.route('/delgrades/', methods=["POST"])
@login_required
def del_grades():
    ids = request.form.get("id_list", "")
    ids = ids.split(",")
    ids = [(ids[2 * i], ids[2 * i + 1]) for i in range(len(ids) // 2)]
    grades = [Grade.query.filter(Grade.uid == id[0], Grade.pid == id[1]).first() for id in ids]
    if grades:
        for grade in grades:
            if grade:
                db.session.delete(grade)
        db.session.commit()
        return jsonify({"statue": True})
    else:
        return jsonify({"statue": False})


# del_grade
@bp.route('/delgrade/', methods=["POST"])
@login_required
def del_grade():
    uid = request.form.get("uid", "")
    pid = request.form.get("pid", "")
    grade = Grade.query.filter(Grade.uid == uid, Grade.pid == pid).first()
    if grade:
        db.session.delete(grade)
        db.session.commit()
        return jsonify({"statue": True})
    else:
        return jsonify({"statue": False})


# update_info
@bp.route('/updategradeinfo/', methods=["POST"])
@login_required
def update_grade_info():
    uid = request.form.get("uid", "")
    pid = request.form.get("pid", "")
    new_grade = request.form.get("grade", "")
    grade = Grade.query.filter(Grade.uid == uid, Grade.pid == pid).first()
    if grade:
        grade.grade = new_grade if new_grade != "" else grade.grade
        db.session.commit()
        return jsonify({"statue": True})
    return jsonify({"statue": False})


'''
######################
Setting View (useless)
######################
'''


@bp.route('/cmssetting/')
@login_required
def cms_setting():
    context = {
        "sth": "v"

    }
    return render_template("cms/setting.html", **context)


@bp.route('/rgm/', methods=['POST'])
@login_required
def re_gen_models():


    action = request.form.get("action", "")
    if action:
        if action == "regen":
            if os.path.exists('ratings.json'):
                os.remove('ratings.json')
            if os.path.exists('grade_sim_form.json'):
                os.remove('grade_sim_form.json')

            rd.data_to_json()

            return jsonify({"statue": 'complete'})
    return jsonify({"statue": True})


'''
######################
Something cause Error
######################
'''

# # test
# @bp.route('/test/')
# def test():
#     users = [['ok']]
#     context = {
#         "users": users
#     }
#
#     # for i in range(100, 200):
#     #     username = "xxxxxx" + str(i)
#     #     password = "xxxxxxxxx" + str(i)
#     #     email = "xxx" + str(i) + "@xxx.xx"
#     #     realname = "xx" + str(i)
#     #     user = FrontUser(username = username, password=password, email=email, realname= realname)
#     #
#     #     db.session.add(user)
#     #
#     # db.session.commit()
#
#     return render_template("common/test.html", **context)


bp.add_url_rule("/login/", view_func=LoginView.as_view("login"))

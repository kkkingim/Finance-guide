# coding: utf-8
from flask import Blueprint, render_template, request, session, Response, redirect, url_for
from flask.views import MethodView
from apps.front.forms import RegForm, LoginForm
from apps.front.models import FrontUser as User, db
from .decorators import login_required

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

                return "注册成功<a href=''>返回<a>"
            else:
                return self.__render("用户名或邮箱已存在")
        errors = [e for e in form.errors.values()]
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
    state = "ok"
    login_flag = False

    if "uid" in session:
        state = session["uid"]
        login_flag = True

    context = {
        "state": state,
        'login_flag': login_flag
    }
    return render_template('front/index.html', **context)


@bp.route("/logout/")
@login_required
def logout():
    del session["uid"]
    return redirect(url_for("front.index"))


bp.add_url_rule("/login/", view_func=LoginView.as_view("login"))
bp.add_url_rule("/reg/", view_func=RegView.as_view("reg"))
bp.add_url_rule("/setting/", view_func=SettingView.as_view("setting"))

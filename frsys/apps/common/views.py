from flask import Blueprint, render_template, request
from apps.front.decorators import login_required
import config

bp = Blueprint("common", __name__)

@bp.route('/admin/')
def admin_index():
    return render_template("common/admin.html")


@bp.route("/list/")
@login_required
def show_list():

    from apps.models import Product

    page = int(request.values.get("page", 0))
    if page < 0:
        page = 0

    pds = Product.query.offset(page*config.ROW_PER_PAGE)[:config.ROW_PER_PAGE]
    amt = Product.query.count()

    print(request.url)


    return render_template("common/list.html", pds = pds, amt=amt)

@bp.route("/add/")
def add_sth():

    from apps.cms.models import CmsUser, db
    #
    # user = CmsUser(username="johnson", password="abkfiakq94151")
    # db.session.add(user)
    # db.session.commit()

    users = CmsUser.query.count()

    return str(users)
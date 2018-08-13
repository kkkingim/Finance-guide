from .views import bp, CmsUser
from flask import g, session


@bp.before_request
def before_request():
    if "cms_uid" in session:
        id = session["cms_uid"]
        user = CmsUser.query.filter(CmsUser.id == id).first()
        if user:
            g.cms_user = user
            print(g.cms_user)

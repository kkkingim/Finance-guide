#encoding: utf-8
from functools import wraps
from flask import session, redirect, url_for, request

def login_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if "cms_uid" in session:
            return func(*args,**kwargs)
        else:
            return redirect(url_for('cms.login', next = request.path))
    return inner
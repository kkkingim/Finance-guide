#encoding: utf-8
from functools import wraps
from flask import session, redirect, url_for, request

def login_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if "uid" in session:
            return func(*args,**kwargs)
        else:
            return redirect(url_for('front.login', next = request.path))
    return inner
# coding: utf-8
from flask import Flask
import config
from exts import db

from app.front import bp as front_bp
# from app.cms import bp as cms_bp
from app.common import bp as common_bp


application = Flask(__name__)
application.config.from_object(config)

db.init_app(application)

application.register_blueprint(front_bp)
# app.register_blueprint(cms_bp)
application.register_blueprint(common_bp)


if __name__ == "__main__":

    application.run()

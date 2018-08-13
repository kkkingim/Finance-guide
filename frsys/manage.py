#coding: utf-8

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from frsystem import app

from apps.front import models as front_models
from apps.cms import  models as cms_models
from  apps.common import models as common_models
from apps import models

db = models.db

manager = Manager(app)
Migrate(app, db)
manager.add_command("db", MigrateCommand)

@manager.option('-u','--username',dest='username')
@manager.option('-p','--password',dest='password')
def create_cms_user(username,password):
    user = cms_models.CmsUser(username=username,password=password)
    db.session.add(user)
    db.session.commit()
    print('cms用户添加成功！')


if __name__ == "__main__":
    manager.run()

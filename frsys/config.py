from datetime import timedelta, datetime

# sqlalchemy
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://ksuser:ksssuser@localhost:3306/fr_system"

# flask
SECRET_KEY = "MERRY_CHRISTMAS"

DEBUG = True
TEMPLATES_AUTO_RELOAD = True
# SERVER_NAME = "xxn.com:5000"

#session
PERMANENT_SESSION_LIFETIME = timedelta(hours=8)




# Info
RUN_START_TIME = datetime.now()
# RUN_START_TIME = datetime.now() - timedelta(hours=2, minutes=22)

ROW_PER_PAGE = 10

GEN_STATUE = 0
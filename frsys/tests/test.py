import random


for i in range(10):
    print ("".join([random.choice(list("qwertyuiopasdfghjklzxcvbnm1234567890!@#$%^&*+")) for a in range(16)]))

print (len("pbkdf2:sha256:50000$oVDL5VF1$4d2f04a11c756b3400990d3c680a0f9a3be1b3110c4e05914a8095705b52da06"))




#--------used ----

from enum import Enum


class roletype(Enum):
    SuperAdmin = 1
    Admin = 2
    User = 3

u_role = db.Column(db.Enum(roletype), nullable=False)




#-----------------
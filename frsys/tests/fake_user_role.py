fake_names = []
for i in range(10):
    name = fa.name().split(" ")[1].lower()
    while (name in fake_names):
        name = fa.name().split(" ")[1].lower()
    fake_names.append(name)

fake_passwords = []
for i in range(10):
    pwd = fa.word() + str(fa.random_int(min=1000))
    while (pwd in fake_passwords or len(pwd) <= 8):
        pwd = fa.word() + str(fa.random_int(min=1000))
    fake_passwords.append(pwd)

l = []

for i in range(10):
    unm = fake_names[i]
    upd = fake_passwords[i]
    if (i + 1) % 10 == 0:
        uid = 1000 + i // 10
        rt = roletype.SuperAdmin
    elif (i + 1) % 3 == 0:
        uid = 5000 + i // 3
        rt = roletype.Admin
    else:
        uid = 10000 + i
        rt = roletype.User

    user = User(u_id=uid, u_username=unm, u_password=upd)
    role = Role(u_id=uid, u_role=rt)

    l.append(user)
    l.append(role)

db.session.add_all(l)
db.session.commit()
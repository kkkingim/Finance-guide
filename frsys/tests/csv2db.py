import csv


def gp2():
    file = '/Users/vagitus/Desktop/ks/csv/gp2_p.csv'

    with open(file, "r") as f:
        dr = csv.DictReader(f)
        data = [i for i in dr]

    l = []

    for i in data:
        pid = i["#"]
        for j in i.items():
            if j[0] != "#" and j[1] != "":
                username = j[0]
                grade = j[1]

                l.append((pid, username, grade))

    return l

print()
#
# file = '/Users/vagitus/Desktop/ks/csv/gp2.csv'
#
# with open(file, "r") as f:
#     dr = csv.DictReader(f)
#     data = [i for i in dr]
#


def gp_p():
    with open("/Users/vagitus/Desktop/py/flask_project/frsys/tests/a.csv", "r") as f2:
        dr = csv.DictReader(f2)
        data = [i for i in dr.reader]

        l = []

        for i in data[1:]:
            l.append(i)

    return l

for i in gp_p():
    print(i)

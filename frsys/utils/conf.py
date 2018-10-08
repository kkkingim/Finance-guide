import pymysql

# 数据库表名
GRADE_LIST = ['grade', 'grade_1', 'grade_2']
PRODUCT_LIST = ['product', 'product_1', 'product_2']
PRODUCT_PROP_LIST = ['product_prop', 'product_prop_1', 'product_prop_2']

# 数据库连接
CONNECTION = pymysql.connect(
            host="www.kk721.cn",
            user="ksuser",
            password="ksssuser",
            db="fr_system",
            charset="utf8")
CUR = CONNECTION.cursor()

#数据库从查询语句
SQL_GRADE = 'SELECT pid, showid, grade FROM fr_system.{0} ,fr_system.front_user ' \
              'where fr_system.{0}.uid = fr_system.front_user.id'

SQL_PRODUCT = 'SELECT * FROM fr_system.{0[product]}'
SQL_PROP = 'SELECT * FROM fr_system.{0[prop]}'

SQL_ID2SHOWID = "SELECT id, showid FROM fr_system.front_user"

idlist = []
CUR.execute(SQL_ID2SHOWID)
rows = CUR.fetchall()
for row in rows:
    idlist.append(row)

# timelyRec 中取相似用户的的个数
USERNUM = 3

baseidr = "utils/"
# baseidr = ""


# if __name__ == '__main__':
#     print('conf.py')
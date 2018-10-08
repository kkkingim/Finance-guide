import time
import pickle
import numpy as np
from pandas import DataFrame, Series
from scipy.stats import pearsonr
from utils.conf import CUR, SQL_GRADE, GRADE_LIST, PRODUCT_LIST, PRODUCT_PROP_LIST, SQL_PROP, SQL_PRODUCT, USERNUM
from utils.conf import baseidr , idlist
import os


def get2id(id):
    for i in idlist:
        if id == i[0]:
            return i[1]
        if id == i[1]:
            return i[0]
    return None


# 将评数据转成pkl
def data_to_pkl(data, pkl_name):
    pkl_name = baseidr + "dailyRec_pkl/" + pkl_name
    if not pkl_name.endswith('.pkl'):
        pkl_name += '.pkl'
    output = open(pkl_name, 'wb')
    pickle.dump(data, output)
    output.close()
    print('Info: The ' + str(pkl_name) + ' in pkl is success ! ')


# 将pkl转回数据
def pkl_to_data(pkl_name):
    pkl_name = baseidr + "dailyRec_pkl/" + pkl_name
    if not pkl_name.endswith('.pkl'):
        pkl_name += '.pkl'
    if os.path.exists(pkl_name):
        pkl_file = open(pkl_name, 'rb')
        data = pickle.load(pkl_file)
        pkl_file.close()
        return data
    else:
        print("You should make dailyRec firstly!")
        return None


class Product:
    # 初始化
    def __init__(self, grade, product, prop):
        self.grade = grade
        self.product = product
        self.prop = prop
        self.gradeForm = None
        self.productForm = None
        self.productRank = None
        # 返回DataFrame
        self.get_gradeForm()
        # 返回DataFrame
        self.get_productForm()
        # 返回Series
        self.get_productRank()

    # 获取评分表
    def get_gradeForm(self):
        data = DataFrame(dtype=np.int8)
        data.name = self.grade + "_gradeForm"
        data.index.names = ['pid']
        data.columns.names = ['uid']
        self_SQL_GRADE = SQL_GRADE.format(self.grade)

        try:
            CUR.execute(self_SQL_GRADE)
            rows = CUR.fetchall()
            for row in rows:
                data.loc[row[0], row[1]] = row[2]
        except Exception as e:
            raise e
        finally:
            data = data.fillna(0)
            self.gradeForm = data
            print("Info: The {0[product]}'gradeForm is up to date.".format({'product': self.product}))

    # 获取产品表
    def get_productForm(self):
        products_list = []
        prop_list = []
        self_SQL_PRODUCT = SQL_PRODUCT.format({'product': self.product})
        self_SQL_PROP = SQL_PROP.format({'prop': self.prop})

        try:
            CUR.execute(self_SQL_PRODUCT)
            results_product = CUR.fetchall()
            for row in results_product:
                products_list.append(row)

            CUR.execute(self_SQL_PROP)
            results_prop = CUR.fetchall()
            for row in results_prop:
                prop_list.append(row[0])
        except Exception as e:
            raise e
        finally:
            # 将prop表的值做为product表的列名
            frame = DataFrame(products_list, columns=prop_list[:])
            frame.name = self.product + "_productForm"
            frame.index.names = ['product id']
            frame.columns.names = ['attribute']
            self.productForm = frame.fillna(0)
            print("Info: The {0[product]}'productForm is up to date.".format({'product': self.product}))

    # 将评分表中心化后排序
    def get_productRank(self, start=0, end=30):
        centered_rating = self.gradeForm.apply(lambda x: x - x.mean(), axis=1)
        centered_rating['sum_grade'] = centered_rating.apply(lambda x: x.sum(), axis=1)
        self.productRank = centered_rating['sum_grade'].sort_values(ascending=False)[start:end].index
        print("Info: The {0[product]}'productRank is up to date.".format({'product': self.product}))


class Pro_rec(Product):

    def __init__(self, grade, product, prop):
        Product.__init__(self, grade, product, prop)

    # 每日推荐,pkl ## 不用!!
    def make_dailyRec(self, k=15):
        dailyRec = {}
        for uid in self.gradeForm.columns:
            # # Test
            # if uid == 1040: break

            # 取出评分二维表中目标用户未评分的产品的index
            not_bought_index = self.gradeForm[uid].isin([0]).index
            new_list = {}
            for item in not_bought_index:
                grade = self.get_sim_in_item(ratings=self.gradeForm, target_user=uid, target_item=item)
                new_list[item] = grade
            rec_list = Series(new_list)
            rec_list = rec_list.sort_values(ascending=False)[: k]
            dailyRec[uid] = rec_list.index

        #  生成每个人用户后存入pkl
        pkl_name = self.product + '_dailyRec.pkl'
        data_to_pkl(dailyRec, pkl_name)
        print("Info: The {0[product]}'dailyRec is save in pkl.".format({'product': self.product}))

    # 从pkl取出每日推荐
    def get_dailyRec(self):
        try:
            pkl_name = self.product + '_dailyRec.pkl'
            data = pkl_to_data(pkl_name)
            return data
        except Exception as e:
            print("Please check your local pkl file  or remake it !")
            return None

    def get_user_dailyRec(self, uid):
        return self.get_dailyRec()[get2id(uid)]

    # 求某用户对某产品的预测评分（基于产品）
    def get_sim_in_item(self, ratings, target_user, target_item):

        # 取出评分二维表中目标用户已经评分的index
        no_0_index = ratings[~ratings[target_user].isin([0])].index
        csim_list = []
        # 求每一行与目标行的相似度, 如果目标行全为0，返回0
        if (ratings.loc[target_item, :] == 0).astype(int).sum() == ratings.columns.size:
            return float(0)

        for i in no_0_index:
            ss = pearsonr(ratings.loc[i, :], ratings.loc[target_item, :])
            csim_list.append(np.nan_to_num(ss[0]))
        new_ratings = DataFrame({'similarity': csim_list, 'rating': ratings[target_user]}, index=no_0_index)

        # 得出某产品相对其他产品的相似度和评分表
        new_ratings = new_ratings[new_ratings.similarity > 0].sort_values('similarity', ascending=False)

        if new_ratings['similarity'].sum() == 0:
            return float(0)

        new_ratings['multiple'] = new_ratings['rating'] * new_ratings['similarity']

        # 通过加权平均求出某用户对某产品的预测评分
        result = new_ratings['multiple'].sum() / new_ratings['similarity'].sum()
        return result

    # 及时推荐（基于内容）,每次取，k += 1
    def get_timelyRec(self, uid, k=1):
        uid = get2id(uid)
        ratings = self.gradeForm.T
        sim_user = {}
        sim_user['uid'] = ratings.index
        sim_user['user_sim'] = []

        # 求相似度最高的用户
        for i in ratings.index:
            ss = pearsonr(ratings.loc[i, :], ratings.loc[uid, :])
            sim_user['user_sim'].append(np.nan_to_num(ss[0]))
        sim_user_list = DataFrame(sim_user).sort_values(by="user_sim", ascending=False)
        sim_user_list = sim_user_list[sim_user_list['user_sim'] > 0]

        # 如果相似用户产品全部推荐完，转为热门推荐
        start = (k - 1) * USERNUM + 1
        end = k * USERNUM + 1

        if end > len(sim_user_list) - 1:
            print("The sim_user_list is used! ")
            rec = self.productRank
        else:
            # 取出n位相似用户所有评分的产品去尾降序排列(第一位是推荐用户本身，排除）
            users = list(sim_user_list[start: end]['uid'])
            rec = ratings.loc[[users[0], users[1], users[2]]].T
            rec['sum'] = rec.apply(lambda x: x.sum(), axis=1)
            rec = rec[rec['sum'] > 0].sort_values(by="sum", ascending=False)

        # 取出推荐用户所有未评分的产品
        uid_list = ratings.loc[uid][ratings.loc[uid] > 0]

        # 将推荐列表中推荐用户已评分产品去除
        rec_list = [i for i in rec.index if i not in set(uid_list.index)]
        return rec_list


# # How To Use

# if __name__ == "__main__":
#     start = time.clock()
#
#     end = time.clock()
#     print('\n' + '-' * 10 + 'Init time: %s Seconds' % (end - start) + '-' * 10)
#     print(pro_rec_2.productForm.head())
#     #=======================================================================================================================
#
#
#     start = time.clock()
#
#     a = pro_rec.get_timelyRec(1040, k=1)
#     print(a)
#     b = pro_rec_1.get_timelyRec(1040, k=1)
#     print(b)
#     c = pro_rec_2.get_timelyRec(1040,k=1)
#     print(c)
#
#     end = time.clock()
#     print('\n' + '-' * 10 + "Get timelyRec's time: %s Seconds" % (end - start) + '-' * 10)
#
#     #=======================================================================================================================
#
#     start = time.clock()
#
#     pro_rec.make_dailyRec(k=15)
#     pro_rec_1.make_dailyRec(k=15)
#     pro_rec_2.make_dailyRec(k=15)
#
#     end = time.clock()
#     print('\n' + '-' * 10 + "Making dailyRec's time: %s Seconds" % (end - start) + '-' * 10)
#
#     #=======================================================================================================================
#
#     start = time.clock()
#
#     a = pro_rec.get_dailyRec()
#     print(a)
#     b = pro_rec_1.get_dailyRec()
#     print(b)
#     c = pro_rec_2.get_dailyRec()
#     print(c)
#
#     end = time.clock()
#     print('\n' + '-' * 10 + "Get dailyRec's time: %s Seconds" % (end - start) + '-' * 10)
#
#
#     #=======================================================================================================================
#     #=======================================================================================================================


pro_rec = Pro_rec(GRADE_LIST[0], PRODUCT_LIST[0], PRODUCT_PROP_LIST[0])
pro_rec_1 = Pro_rec(GRADE_LIST[1], PRODUCT_LIST[1], PRODUCT_PROP_LIST[1])
pro_rec_2 = Pro_rec(GRADE_LIST[2], PRODUCT_LIST[2], PRODUCT_PROP_LIST[2])


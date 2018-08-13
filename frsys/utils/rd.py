#coding: utf-8
import pymysql

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from pandas import DataFrame, Series
from apps.models import db, Grade

# 数据库取数据,输入参数为(产品ID, 用户ID, grade, 数据库表名), 输出产品-用户 评分表
def get_mysql_grade():
    data = DataFrame()
    try:
        for grade in Grade.query.all():
            data.loc[grade.uid, grade.pid] = grade.grade
    except Exception as e:
        raise e
    finally:
        data.index.names = ['uid']
        data.columns.names = ['pid']
        return data.fillna(0)

ratings = get_mysql_grade()
centered_rating = ratings.apply(lambda x : x - x.mean(), axis=1)



# 求某用户对某产品的预测评分（基于物品）
def get_sim_in_item(ratings, centered_rating, target_user, target_item):
    # 取出评分二维表中目标用户已经评分的index
    no_0_index = ratings[~ratings[int(target_user)].isin([0])].index
    csim_list = []
    for i in no_0_index:
        #print(i)
        csim_list.append(cosine_similarity(centered_rating.loc[i, :].values.reshape(1, -1),
                                           centered_rating.loc[target_item, :].values.reshape(1, -1)).item())
    new_ratings = pd.DataFrame({'similarity': csim_list, 'rating': ratings[target_user]}, index=no_0_index)

    #print(new_ratings)

    # 得出某产品相对其他产品的相似度和评分表
    top = new_ratings[new_ratings.similarity > 0].sort_values('similarity', ascending=False)

    #print('---' + str(target_item) + '---')
    #print(top)

    top['multiple'] = top['rating'] * top['similarity']

    # 通过加权平均求出某用户对某产品的预测评分
    result = top['multiple'].sum() / top['similarity'].sum()

    #print(result)
    return result

# 基于产品的协调过滤推荐
def get_item_in_item(ratings, centered_rating, target_user, k):
    # 取出评分二维表中目标用户未评分的产品的index
    not_bought_index = ratings[target_user].isin([0]).index
    new_list = {}
    for item in not_bought_index:
        grade = get_sim_in_item(ratings=ratings, centered_rating=centered_rating, target_user=target_user,
                                target_item=item)
        new_list[item] = grade
    recommend_list = Series(new_list)
    recommend_list.index.name = 'item_ID'
    recommend_list.name = 'Recomend_grade'
    recommend_list = recommend_list.sort_values(ascending=False)[: k]
    return recommend_list


print (get_sim_in_item(ratings=ratings, centered_rating=centered_rating, target_user=10001,target_item=5662))



print (get_item_in_item(ratings=ratings, centered_rating=centered_rating, target_user=10001, k=10))
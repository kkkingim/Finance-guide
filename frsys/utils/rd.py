import pymysql
import numpy as np
from pandas import DataFrame
from scipy.stats import pearsonr
import json
import time
import config



from apps.models import Grade

# 准备工作: 取数据,算相似度, 把二维表转成json文件存储
def data_to_json():
    config.GEN_STATUE = 1

    # 输入参数为(产品ID, 用户ID, grade, 数据库表名), 输出产品-用户 评分表
    def get_mysql_grade():
        uid2id = {}
        nnum = 1000
        data = DataFrame(dtype=np.int8)
        grades = Grade.query.all()
        try:
            for grade in grades:
                if grade.uid not in uid2id:
                    nnum += 1
                    if 'Vr-' in grade.uid:
                        uid2id[grade.uid] = str(nnum)
                    else:
                        uid2id[grade.uid] = 'Vr-' + str(nnum)
                uid = uid2id[grade.uid]

                data.loc[grade.pid, uid] = grade.grade
        except Exception as e:
            raise e
        finally:
            data.index.names = ['pid']
            data.columns.names = ['uid']
            data = data.fillna(0)
            return data

    start = time.clock()
    # 获取产品-用户 评分表
    ratings = get_mysql_grade()
    end = time.clock()
    print('Request Data time: %s Seconds' % (end - start))


    # 将评分二维表转成json,并存入本地
    with open( 'ratings.json', 'w') as f:
        a_json = ratings.to_json(orient='split')
        json.dump(a_json, f)
    print('The grade in json is success ! ')

    # 根据产品-用户 评分表,算出各个产品(用户)之间的相似度,返回相似度二维表
    def get_sim_form(ratings):
        sim_form = DataFrame(index=ratings.index, columns=ratings.index)
        index_length = len(ratings.index)
        print(index_length)
        for i in range(index_length):
            print(i)
            # print('(' + str(i) + '):  ', end=' ')
            for j in range(i + 1):
                # print(j,end=' ')
                if i == j :
                    sim = float(1)
                else:
                    sim = pearsonr(ratings.iloc[i, :], ratings.iloc[j, :])
                sim_form.iloc[i, j] = sim
        sim_form = sim_form.fillna(0)

        return sim_form

    start = time.clock()
    sim_form = get_sim_form(ratings)
    end = time.clock()
    print('Creating the sim Data time: %s Seconds' % (end - start))


    # 将相似度二维表转成json,并存入本地
    with open('grade_sim_form.json', 'w') as f:
        a_json = sim_form.to_json(orient='split')
        json.dump(a_json, f)
    print('The sim_form in json is success ! ')

    config.GEN_STATUE = 0

#############################################################################



# All_start =time.clock()
#
# data_to_json()
#
# # 将json转回二维表
# # with open('grade_sim_form.json', 'r') as f:
# # with open('grade.json', 'r') as f:
# #     a_json = json.load(fp=f)
#
# # a_dict = json.loads(a_json)
# # ratings = DataFrame(a_dict['data'], index=a_dict['index'], columns=a_dict['columns'])
#
# # ratings.iloc[0,:]
#
# All_end =time.clock()
# print('All  time: %s Seconds'%(All_end-All_start))
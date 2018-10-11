# -*- coding:utf-8 -*-
"""
Created on Mon Sep 7 16:01 2018
@author: BC_Zhang
"""
import pymongo
import pandas as pd
import numpy as np
from snownlp import SnowNLP


#初始化
client = pymongo.MongoClient(host='localhost',port=27017)
db = client.doubanfic
collection = db.doubanfic1

#调用SnowNLP对数据进行分析
def get_sentiment_cn(text):
	s = SnowNLP(text)
	return s.sentiments



def main():
	data = collection.find()#{'star':1}
	data_pack = []
	for record in data:
		comment = record['comment']
		sentiments = get_sentiment_cn(comment)
		data_temp = []
		year = record['time'][0]
		month = record['time'][1]
		day = record['time'][2]
		star = record['star']
		useful = record['useful']
		user_name = record['user_name']
		data_temp.append(user_name)
		data_temp.append(year)
		data_temp.append(month)
		data_temp.append(day)
		data_temp.append(star)
		data_temp.append(sentiments)
		data_temp.append(useful)
		data_temp.append(comment)
		data_pack.append(data_temp)
	np_data = np.array(data_pack)
	pd_data = pd.DataFrame(np_data, columns=['user_name', 'year','month', 'day','star', 'sentiments','useful', 'comment'])
	# print(pd_data)
	pd_data.to_excel('excel_output.xls',na_rep=True)

if __name__ == '__main__':
    main()
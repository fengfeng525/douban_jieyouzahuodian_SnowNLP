# -*- coding:utf-8 -*-
"""
Created on Mon Sep 3 21:22 2018
@author: BC_Zhang
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import sys
from requests.exceptions import RequestException
import math
from Config import *
import pymongo
import random
# from fake_useragent import UserAgent


# ua = UserAgent()
# header = {'User-Agent':ua.random}

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


# PROXY_POOL_URL = 'http://localhost:5000/get'
#
# def get_proxy():
#     try:
#         response = requests.get(PROXY_POOL_URL)
#         if response.status_code == 200:
#             return response.text
#     except ConnectionError:
#         return None


def get_page(url_base):
	print('正在读取页面……')
	ips = [	'http://39.137.69.10:8080',
		 'http://47.105.164.63:80',
		 'http://118.190.95.43:9001',
		 'http://120.76.55.150:80',
		 'http://115.223.222.206:9000',
		 'http://221.2.174.28:8060',
		 'http://118.190.95.35:9001',
		 'http://110.40.13.5:80',
		 'http://122.252.182.80:53281',
		 'http://61.135.217.7:80']


	proxy_ip = {'http':ips[random.randint(0, 9) ]}
	try:
		# print(header)
		response = requests.get(url_base,proxies = proxy_ip)#headers =header
		if response.status_code == 200:
			return response.text
		return None
	except RequestException:
		return None

def get_page_num(html):
	soup = BeautifulSoup(html, "html.parser")
	page_num = soup.find(id='total-comments').get_text().replace("全部共 ","").replace(" 条","")
	print(page_num)
	return page_num

def get_user_loc(html):
	soup = BeautifulSoup(html, "html.parser")
	user_loc = soup.find(class_='user-info').find('a').get_text()
	# print(user_loc)
	return user_loc

def parse_one_page(html1):
	soup = BeautifulSoup(html1, "html.parser")
	for item in soup.find_all(class_="comment-item"):
		comment_info = {
			'user_name': None,
			'user_url': None,
			# 'user_loc': None,
			'star': None,
			'time': None,
			'useful': None,
			'comment': None
		}
		try:
			comment_info['user_name'] = item.find(class_ ='avatar').find('a').get('title')
		except:
			pass
		try:
			comment_info['user_url'] = item.find(class_ ='avatar').find('a').get('href')
		except:
			pass
		# try:
		# 	html2 = get_page(comment_info['user_url'])
		# 	comment_info['user_loc'] = get_user_loc(html2)
		# except:
		# 	pass
		try:
			tmp = item.find(class_="comment-info").find('span').get('title')
			if tmp == '力荐':
				comment_info['star'] = 5
			elif tmp == '推荐':
				comment_info['star'] = 4
			elif tmp == '还行':
				comment_info['star'] = 3
			elif tmp == '较差':
				comment_info['star'] = 2
			elif tmp == '很差':
				comment_info['star'] = 1
		except:
			pass
		try:
			if comment_info['star']==None:
				comment_info['time'] = item.find(class_="comment-info").find_all('span')[0].get_text().split('-')
			else:
				comment_info['time'] = item.find(class_="comment-info").find_all('span')[1].get_text().split('-')
		except:
			pass
		try:
			comment_info['useful'] = int(item.find(class_="vote-count").get_text())
		except:
			pass
		try:
			comment_info['comment'] = item.find(class_="short").get_text()
		except:
			pass
		# print(comment_info)
		save_to_mongo(comment_info)

def save_to_mongo(result):
	# db[MONGO_TABLE].insert(result)
	try:
		if db[MONGO_TABLE].insert(result):
			print('存储到MongoDB成功',result)
	except Exception:
		print('存储到MongoDB失败', result)

def main():
	url_base = 'https://book.douban.com/subject/25862578/comments/hot?'
	html = get_page(url_base)
	page_num = int(get_page_num(html))
	print(math.ceil(page_num / 20))
	for i in range(1,math.ceil(page_num/20)):
		url_tmp = url_base + "p=%s"%i
		html1 = get_page(url_tmp)
		time.sleep(4)
		try:
			parse_one_page(html1)
			print(i, '页正常')
		except:
			print(i,'页出错')

if __name__ == '__main__':
	main()
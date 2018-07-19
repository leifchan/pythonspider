# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 14:55:30 2018

@author: DELL
"""

#Redis地址
REDIS_HOST = '127.0.0.1'
#Redis端口
REDIS_PORT = '6379'
#redis密码
REDIS_PASSWORD = None

REDIS_KEY = 'weixin'
#代理池地址
PROXY_POOL_URL = 'http://127.0.0.1:5000/random'
#响应码
VALID_STATUS = [200]

MAX_FAILED_TIME = 20

TIMEOUT = 20

#MySQL用户名、密码等
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PORT = 3306
MYSQL_PASSWORD = None
MYSQL_DATABASE = 'weixin'



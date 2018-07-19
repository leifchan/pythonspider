# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 18:27:40 2018

@author: DELL
"""

import pymysql
from weix.config import *

class MySQL():
    def __init__(self,host=MYSQL_HOST,username=MYSQL_USER,password=MYSQL_PASSWORD,
                 port=MYSQL_PORT,database=MYSQL_DATABASE):
        '''
        MySQL初始化
        param host：
        param username：
        param port：
        param password:
        param database:
        '''
        try:
            self.db = pymysql.connect(host,username,password,database,charset='utf8',
                                      port=port)
            self.cursor = self.db.cursor()
        except pymysql.MySQLError as e:
            print(e.args)
    
    def insert(self,table,data):
        '''
        插入数据
        '''
        keys = ','.join(data.keys())
        values = ','.join(['%s']*len(data))
        sql_query = 'insert into %s (%s) values (%s)' %(table,keys,values)
        try:
            self.cursor.execute(sql_query,tuple(data.values()))
            self.db.commit()
        except pymysql.MySQLError as e:
            print(e.args)
            self.db.rollback()
        
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 14:05:03 2018

@author: DELL
"""

#TIMEOUT = 10
from requests import Request
from weix.config import TIMEOUT


class WeixinRequest(Request):
    def __init__(self,url,callback,method='GET',headers=None,
                 need_proxy=False,fail_time=0,timeout=TIMEOUT):
        Request.__init__(self,method,url,headers)
        self.callback = callback
        self.need_proxy = need_proxy
        self.fail_time = fail_time
        self.timeout = timeout
        
        
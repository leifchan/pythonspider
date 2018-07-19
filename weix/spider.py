# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 15:23:59 2018

@author: DELL
"""

from weix.config import *
from requests import Session
from weix.db import RedisQueue
from weix.request import WeixinRequest
from urllib.parse import urlencode
from requests import ConnectionError,ReadTimeout
import requests
from pyquery import PyQuery as pq
from weix.mysql import MySQL


class Spider():
    base_url = 'http://weixin.sogou.com/weixin'
    keyword = '区块链'
    headers = {
            'Accept': 'text/html,application/xhtml+xml,applicati'+
            'on/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'ABTEST=0|1531911557|v1; IPLOC=CN3502; SUID=465D2978721A910A000000005B4F1D85; SUID=465D29781E20910A000000005B4F1D87; weixinIndexVisited=1; SUV=002F259F78295D465B4F1D8979B02791; ppinf=5|1531911582|1533121182|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToyNzolRTglQjYlQjQlRTglQjYlQjQlRTklQTIlQTB8Y3J0OjEwOjE1MzE5MTE1ODJ8cmVmbmljazoyNzolRTglQjYlQjQlRTglQjYlQjQlRTklQTIlQTB8dXNlcmlkOjQ0Om85dDJsdUZSaEdDOUxpY3ZMT0FaMVdpektKWFFAd2VpeGluLnNvaHUuY29tfA; pprdig=qMRbPOJ-5DrmFSfPMu071D0-PqmALVCVDhRC7a9byaQ3GCISFiB8z0455yRj6PUDCFdAYf-_Xm7SB_0IdDDl_Lup4mdA7geguowhk8mJuu7E2eZ5iCJlZlV9bkFYtj1P9AlixXMu7vJ54bbvCURCkTqJ_Lh6HPtYX8FfdCmZ_XY; sgid=20-36086407-AVtPHZ7BYBIaJevIoBbR3JQ; SUIR=D9C3B6E79E9AEFDC69059DDC9FDFB561; SNUID=C3D8ADFD8581F5C132D23B7C8598D918; ld=8lllllllll2bF8cplllllVH55AUlllllWjONSkllllGlllll9klll5@@@@@@@@@@; LSTMV=480%2C153; LCLKINT=1788; ppmdig=1531982355000000f568350e0482be773bf1a8e38fdca406; JSESSIONID=aaaHU7xOhzCpH-CDVaHsw; sct=9',
            'Host': 'weixin.sogou.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
            }
    session = Session()
    queue = RedisQueue()
    mysql = MySQL()
    
    def get_proxy(self):
        '''
        从代理池获取代理
        return：
        '''
        try:
            response = requests.get(PROXY_POOL_URL)
            if response.status_code == 200:
                print('Get Proxy',response.text)
                return response.text
            return None
        except requests.exceptions.ConnectionError:
            return None
    
    def start(self):
        '''
        初始化工作
        '''
        #全局更新Headers
        self.session.headers.update(self.headers)
        start_url = self.base_url +'?'+ urlencode({'type':2,'query':self.keyword,
                                               'ie':'utf8'})
        weixin_request = WeixinRequest(url=start_url,callback=self.parse_index,
                                       need_proxy =True)
        #调度第一个请求
        self.queue.add(weixin_request)
    
    def request(self,weixin_request):
        '''
        执行请求
        param weixin_request：请求
        return：响应
        '''
        prepare_request = self.session.prepare_request(weixin_request)
        try:
            if weixin_request.need_proxy:
                proxy = self.get_proxy()
                if proxy:
                    proxies = {
                            'http':'http://' + proxy,
                            'https':'https//' + proxy,
                            }
                    return self.session.send(prepare_request,timeout=weixin_request.timeout,
                                             allow_redirects=False,proxies=proxies)
            return self.session.send(prepare_request,timeout=weixin_request.timeout,
                                         allow_redirects=False)
        except (ConnectionError,ReadTimeout) as e:
            print(e.args)
            return False
    
    def parse_index(self,response):
        '''
        解析索引页
        param response：响应
        return：新的响应
        '''
        doc = pq(response.text)
        items = doc('.new-list li .txt-box h3 a').items()
        for item in items:
            url = item.attr('href')
            weixin_request = WeixinRequest(url=url,callback=self.parse_detail)
            yield weixin_request
        next_url = doc('#sogou_next').attr('href')
        if next_url:
            url = self.base_url + str(next_url)
            weixin_request = WeixinRequest(url=url,callback=self.parse_index,need_proxy=True)
            yield weixin_request
    
    def parse_detail(self,response):
        '''
        解析详情页
        param response：响应
        return：微信公众号文章
        '''
        doc = pq(response.text)
        data = {
                'title':doc('.rich_media_title').text().strip(),
                'content':doc('.rich_media_content').text().strip(),
                'date':doc('#publish_time').text(),
                'nickname':doc('#js_profile_qrcode > div > strong').text(),                            
                'wechat':doc('#js_profile_qrcode > div > p:nth-child(1) > span').text()
                }
        yield data
    
    def schedule(self):
        '''
        调度请求
        '''
        while not self.queue.empty():
            weixin_request = self.queue.pop()
            callback = weixin_request.callback
            print('schedule',weixin_request.url)
            response = self.request(weixin_request)
            if response and response.status_code in VALID_STATUS:
                results = list(callback(response))
                if results:
                    for result in results:
                        print('New Result',type(result))
                        if isinstance(result,WeixinRequest):
                            self.queue.add(result)
                        if isinstance(result,dict):
                            self.mysql.insert('articles',result)
                else:
                    self.error(weixin_request)
            else:
                self.error(weixin_request)
    
    def error(self,weixin_request):
        '''
        错误处理
        param weixin_request：请求
        return：
        '''
        weixin_request.fail_time +=1
        print('Request Failed',weixin_request.fail_time,'Times',weixin_request.url)
        if weixin_request.fail_time < MAX_FAILED_TIME:
            self.queue.add(weixin_request)
    
    def run(self):
        '''
        入口
        '''
        self.start()
        self.schedule()
        
if __name__ == '__main__':
    spider = Spider()
    spider.run()
    
    

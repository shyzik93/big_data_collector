#!/usr/bin/env python3

"""
Author: Polyakov Konstantin
Date: 2018-12-19
Place: Yeysk, Russia
"""

import requests
import lxml.html as html
import os
import datetime

'''
+ autogetting the next proxy
+ autoupdate list of proxies
'''

class _ProxiesDB():
    
    def __init__(self, c, cu, site, path_data):
        self.c = c
        self.cu = cu
        self.site = site

        self.proxies = []
        self.cur_proxy_index = 0
        
        self.path_log = os.path.join(path_data, 'proxies_log'+datetime.datetime.today().strftime('-%Y-%m-%d_%T').replace(':', '-')+'.txt')
        
        self.s = requests.Session()
        
        self.log('------------------- Start\n', 'w')

    def log(self, text, mode='a'):
        with open(self.path_log, mode) as f: f.write(text)

    def insert(self, ip, port):
        ip = ip.strip()
        port = port.strip()
    	
        sql = "SELECT `proxy_ip`, `proxy_port` FROM `proxy` WHERE `proxy_ip`=? AND `proxy_port`=?"
        res = self.cu.execute(sql, (ip, port)).fetchall()
        
        if not res:

            sql = "INSERT INTO `proxy` (`proxy_ip`, `proxy_port`) VALUES (?, ?)"
            self.cu.execute(sql, (ip, port))

    def commit(self):
        self.c.commit()

    def load(self):
    	
        self.log('------------------- Start loading proxies\n')

        # 1

        r = self.s.get('https://free-proxy-list.net')
        page = html.document_fromstring(r.content)
        rows = page.cssselect('#proxylisttable tr')

        for row in rows:
            children = row.getchildren()
            if children[0].tag == 'th': continue
        
            ip = children[0].text_content()
            port = children[1].text_content()
            has_https = children[6].text_content()

            if has_https == 'yes' and (port == '8080' or port == '80'): self.insert(ip, port)

        self.commit()

        # 2

        r = self.s.get('https://hidemyna.me/ru/proxy-list/?ports=80,8080&type=s')
        page = html.document_fromstring(r.content)
        rows = page.cssselect('.proxy__t tr')

        for row in rows:
            children = row.getchildren()
            if children[0].tag == 'th': continue
        
            ip = children[0].text_content()
            port = children[1].text_content()

            self.insert(ip, port)

        self.commit()

        # 3

        r = self.s.get('https://www.us-proxy.org/')
        page = html.document_fromstring(r.content)
        rows = page.cssselect('#proxylisttable tr')

        for row in rows:
            children = row.getchildren()
            if children[0].tag == 'th': continue
        
            ip = children[0].text_content()
            port = children[1].text_content()
            has_https = children[6].text_content()

            if has_https == 'yes' and (port == '8080' or port == '80'): self.insert(ip, port)

        self.commit()
        
        # 4

        r = self.s.get('https://www.proxynova.com/proxy-server-list/')
        page = html.document_fromstring(r.content)
        rows = page.cssselect('#tbl_proxy_list tr')

        for row in rows:
            children = row.getchildren()
            if children[0].tag == 'th': continue
            
            if len(children) < 2: continue

            ip = children[0].getchildren()[0].get('title').strip()
            port = children[1].text_content().strip()
            speed = int(children[3].getchildren()[0].get('data-value'))
            
            if speed > 50 and (port == '8080' or port == '80'): self.insert(ip, port)

        self.commit()

        # 5

        r = self.s.get('https://www.sslproxies.org/')
        page = html.document_fromstring(r.content)
        rows = page.cssselect('#proxylisttable tr')

        for row in rows:
            children = row.getchildren()
            if children[0].tag == 'th': continue
        
            ip = children[0].text_content()
            port = children[1].text_content()
            has_https = children[6].text_content()

            if has_https == 'yes' and (port == '8080' or port == '80'): self.insert(ip, port)

        self.commit()

        # more proxies)
        #self.proxies += self.proxies
        #self.proxies += self.proxies    

    def update_list(self, count=10):

        self.log('------------------- Start updating list\n')

        self.proxies = []
        self.cur_proxy_index = 0
        
        date = datetime.date.today() - datetime.timedelta(hours=4)
        date = date.strftime('%Y-%m-%d %T')
        
        sql = "SELECT `proxy_ip`, `proxy_port` FROM `proxy` WHERE (`site_"+self.site+"` is NULL OR `site_"+self.site+"` < ?) LIMIT ?"
        res = self.cu.execute(sql, (date,count)).fetchall()
        for proxy in res: self.proxies.append('https://'+proxy['proxy_ip']+':'+str(proxy['proxy_port']))
        
    def block(self):
        if not self.proxies: return

        _proxy = self.proxies[self.cur_proxy_index].split('//')[1]
        ip, port = _proxy.split(':')

        date = datetime.datetime.today().strftime('%Y-%m-%d %T')

        sql = "UPDATE `proxy` SET `site_"+self.site+"`=? WHERE `proxy_ip`=? AND `proxy_port`=?"
        self.cu.execute(sql, (date, ip, port))
        self.c.commit()

class _Proxies(_ProxiesDB):

    def __init__(self, c, cu, site, path_data, is_auto_update=True):
        _ProxiesDB.__init__(self, c, cu, site, path_data)

        self.is_auto_update = is_auto_update

    def __len__(self):
        return len(self.proxies)
        
    def __add__(self, index):
        return self.get_next_proxy(index)

    def __radd__(self, index):
        return self.get_next_proxy(index)

    def get_next_proxy(self, index=1):

        self.cur_proxy_index += index

        if self.cur_proxy_index >= len(self.proxies):
            if self.is_auto_update: self.update_list()
            self.cur_proxy_index = 0

        proxy = self.proxies[self.cur_proxy_index]

        return proxy

    def get_next_proxy2(self, is_cur_blocked=False):
    	
        if is_cur_blocked:
            self.cur_proxy_index -= 1
            del self.proxies[self.cur_proxy_index]

        if self.cur_proxy_index >= len(self.proxies):
            self.cur_proxy_index = 0

        if not self.proxies: self.update_list()

        proxy = self.proxies[self.cur_proxy_index]

        self.cur_proxy_index += 1
        
        return proxy


class Proxies(_Proxies):
	
    def __init__(self, c, cu, site, path_data, is_auto_update=True):
        _Proxies.__init__(self, c, cu, site, path_data, is_auto_update)
        
        self.update_list()

        self.log('\n  Proxy:'.join(self.proxies)+'\n')
        self.log_new(self+0, 'a')
        
    def log_new(self, proxy, mode):
        date = datetime.datetime.today().strftime('%m-%d-%Y %T  ')
        with open(self.path_log, mode) as f: f.write(date+proxy.split('//')[1]+'\n')

    def log_status(self, mode, status, url):
        date = datetime.datetime.today().strftime('%m-%d-%Y %T      ')
        with open(self.path_log, mode) as f: f.write(date + status+' '+url+'\n')


    def get_next_proxy(self, index):
        if index > 0: self.log_new(self.proxies[self.cur_proxy_index], 'a')
        return _Proxies.get_next_proxy(self, index)

    def open_url(self, url, is_blocked_func = lambda r: False, headers={}):
        success = 0
        is_need_new_proxy = 0
        proxy = self + 0
        r = None
        while success == 0:
            r = None

            try:
                r = self.s.get(url, proxies={'https':proxy}, headers=headers)
                success = 1 # for 404 error
            except Exception as e:
                is_need_new_proxy = 1
                self.log_status('a', 'unaccess', url)
                self.block()

            if r is not None:#isinstance(r, requests.Response):
                if not is_blocked_func(r):
                    success = 1
                    self.log_status('a', 'success', url)
                else:
                    self.log_status('a', 'blocked', url)
                    is_need_new_proxy = 1
                    success = 0
                    self.block()

            if is_need_new_proxy:
                proxy = self + 1
                is_need_new_proxy = 0
                self.log_new(proxy, 'a')
                
        return r

    def open_url2(self, url, is_blocked_func = lambda r: False, headers={}):
        success = 0
        proxy = self + 0
        r = None
        is_blocked = 0
        while success == 0:
            r = None

            try:
                r = requests.get(url, proxies={'https':proxy}, headers=headers)
                is_blocked = 0 
            except Exception as e:
                self.log_status('a', 'unaccess', url)
                is_blocked = 1

            if r:
                if not is_blocked_func(r):
                    success = 1
                    self.log_status('a', 'success', url)
                else:
                    self.log_status('a', 'blocked', url)
                    is_blocked = 1

            proxy = self.get_next_proxy2(is_blocked)
            self.log_new(proxy, 'a')

        return r

if __name__ == '__main__':

    import config_site as cs
    
    c, cu = cs.get_db()
    
    proxies = _ProxiesDB(c, cu, 'avito')
    proxies.load()

    print('End')
    exit()

    '''proxies = Proxies()
    proxies.update_list()
    print(len(proxies))
    print(proxies+1, proxies.cur_proxy_index)
    print(proxies+100, proxies.cur_proxy_index)
    print(proxies+100, proxies.cur_proxy_index)
    print(proxies+150, proxies.cur_proxy_index)
    print(proxies+150, proxies.cur_proxy_index)
    print(proxies+450, proxies.cur_proxy_index)
    print(proxies+350, proxies.cur_proxy_index)
    print(proxies+150, proxies.cur_proxy_index)'''
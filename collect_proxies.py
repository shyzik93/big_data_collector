import requests
import lxml.html as html
import os

path_data = os.path.join(os.getcwd(), "data")

if not os.path.exists(path_data): os.makedirs(path_data)

'''
+ autogetting the next proxy
+ autoupdate list of proxies
'''

class Proxies():

    def __init__(self, is_auto_update=True):
        self.proxies = []
        self.cur_proxy_index = 0
        self.is_auto_update = is_auto_update
        
    def __len__(self):
        return len(self.proxies)
        
    def __add__(self, index):
        return self.get_next_proxy(index)

    def __radd__(self, index):
        return self.get_next_proxy(index)

    def update_list(self):

        r = requests.get('https://free-proxy-list.net')

        page = html.document_fromstring(r.content)
        rows = page.cssselect('#proxylisttable tr')

        self.proxies = []
        self.cur_proxy_index = 0
    
        for row in rows:
            children = row.getchildren()
            if children[0].tag == 'th': continue
        
            ip = children[0].text_content()
            has_https = children[6].text_content()
        
            if has_https == 'yes': self.proxies.append(ip)
            
        # more proxies)
        self.proxies += self.proxies
        self.proxies += self.proxies
        
    def get_next_proxy(self, index=1):
        if self.cur_proxy_index >= len(self.proxies):
            if self.is_auto_update: self.update_list()
            self.cur_proxy_index = 0
        

        proxy = self.proxies[self.cur_proxy_index]
    	
        self.cur_proxy_index += index
        
        return proxy

if __name__ == '__main__':

    proxies = Proxies()
    proxies.update_list()
    print(len(proxies))
    print(proxies+1, proxies.cur_proxy_index)
    print(proxies+100, proxies.cur_proxy_index)
    print(proxies+100, proxies.cur_proxy_index)
    print(proxies+150, proxies.cur_proxy_index)
    print(proxies+150, proxies.cur_proxy_index)
    print(proxies+450, proxies.cur_proxy_index)
    print(proxies+350, proxies.cur_proxy_index)
    print(proxies+150, proxies.cur_proxy_index)
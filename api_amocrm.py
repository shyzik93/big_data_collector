import requests
import json
import configparser
import os

class Base():

    def __init__(self, subdomain, login, client_hash):
        self.subdomain = subdomain
        self.login = login
        self.client_hash = client_hash

        self.domain = 'https://'+subdomain+'.amocrm.ru/'
        self.url = self.domain+'api/v2/'

        self.s = requests.Session()

        self.headers = {
            'User-Agent': 'amoCRM-API-client/1.0',
            'Content-Type': 'application/json',
        }

    def auth(self):
        url = self.domain + 'private/api/auth.php?type=json'
        data = {'USER_LOGIN':self.login, 'USER_HASH': self.client_hash}
        res = self.s.post(url, data=json.dumps(data), headers=self.headers)

        if res.status_code in [200, 204]:
            res_json = res.json()['response']
            if  res_json['auth']:
                print('authed')
            else:
                print('not authed')
        elif res.status_code == 401:
            res_json = res.json()['response']
            print('auth failed:', res_json['error_code'], res_json['error'])
        else:
            print('server error. Status code:', res.status_code, res.content)

    def request(self, name, data):
        data = json.dumps(data)

        res = self.s.post(self.url+name, data=data, headers=self.headers)
        if res.status_code == 200:
            print(res.json)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    #config.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'parser_config.ini'))
    config.read('../parser_config.ini')
    #print(dict(config['DEFAULT']))
    config = config['amocrm']

    #print(dict(config))

    amo = Base(config['subdomain'], config['login'], config['client_hash'])
    amo.auth()

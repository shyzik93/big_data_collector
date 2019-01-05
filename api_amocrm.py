import requests
import json
import config_parser
import os

class Base():

    def __init__(self, subdomain, login, client_hash):
        self.subdomain = subdomain
        self.login = login
        self.client_hash = client_hash

        self.domain = 'http://'+subdomain+'amocrm.ru/'
        self.url = self.domain+'api/v2/'

        self.s = requests.Session()

        self.headers = {
            'user-agent': 'amoCRM-API-client/1.0',
            'Content-Type': 'application/json',
        }

    def auth(self):
        url = self.domain + 'private/api/auth.php?type=json'
        data = {'USER_LOGN':self.login, 'USER_HASH': self.client_hash}
        res = self.s.post(url)

        if res.status_code in [200, 204]:
            res_json = res.json['response']
            if  res_json['auth']:
                print('authed')
            else:
                print('not authed')
        else:
            print('server error. Status code:', res.status_code)

    def request(self, name, data):
        data = json.dump(data)

        res = self.s.post(self.url+name, data=data, headers=self.headers)
        if res.status_code == 200:
            print(res.json)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config = config.read(os.path.join(os.path.dirname(__file__), 'parser_config.ini'))
    config = config['amocrm']

    amo = Base(config['subdomain'], config['login'], config['client_hash'])
    amo.auth()

#!/usr/bin/env python3

"""
Author: Polyakov Konstantin
Date: 2018-12-22
Place: Yeysk, Russia
"""

import re
import sqlite3
import lxml.html as html
import requests
import time
import os

import config_site_avito as cs

def get_obj_links_from_page(page):
    page = html.document_fromstring(page)
    links = page.cssselet('')
    
    #https://www.avito.ru/user/e1b47b49f2ed83208fd34f902ad9cfb5/profile/items?shortcut=active&offset=0&limit=16
    #https://www.avito.ru/user/e1b47b49f2ed83208fd34f902ad9cfb5/profile/items?shortcut=closed&offset=0&limit=16

if __name__ == '__main__':

    curIndex = cs.CurIndex(os.path.join(cs.path_data, 'cur_user_id.txt'))
    cur_user_id = curIndex.get()

    c, cu = cs.get_db()

    sql = "SELECT * FROM `user` WHERE `user_id` > ?"
    res = cu.execute(sql, (cur_user_id,)).fetchall()
    
    for user in res:

        if not user['user_url']: continue

        if user['user_url'].startswith('/user/'):
            #url = user['user_url'].split('?')[0]

            url = user['user_url'] + '/items?shortcut=closed&offset=0&limit=16'
            r = requests.get(cs.domain_url + url)
            json = r.json()

            if 'disclaimer' in json: print(json['disclaimer'])

            if not ('status' in json and json['status'] == 'ok'):
                print(json)
                continue
                
            if not ('result' in json):
                print(json)
                continue

            result = json['result']

            if not ('list' in result):
                print(json)
                continue
                
            objects = result['list']
            obj_links = []
            
            for obj in objects:
                
                fields = {}
                
                if not ('category' in obj and 'url' in obj and 'time' in obj and 'price' in obj):
                    print(obj)
                    continue
                
                category = obj['category']
                if not ('name' in category):
                    print(obj)
                    continue

                cat = category['name']
                if cat == 'Квартиры': fields['realty_category'] = 'flat'
                elif cat == 'Комнаты': fields['realty_category'] = 'room'
                elif cat == 'Дома, дачи, коттеджи': fields['realty_category'] = 'house'
                elif cat == 'Земельные участки': fields['realty_category'] = 'land'
                elif cat == 'Гаражи и машиноместа': fields['realty_category'] = 'garage'
                elif cat == 'Коммерческая недвижимость': fields['realty_category'] = 'business'
                elif cat == 'Недвижимость за рубежом': fields['realty_category'] = 'abroad'
                else: continue # it is not realty.
 
                #fields['realty_url'] = obj['url']
                #fields['realty_date_publication'] = cs.transform_date(obj['time'].split())
                ##fields['realty_price'] = obj['price'].replace(' ', '').replace('руб.', '')
                #fields['realty_ext_id'] = obj['id']
                
                if not obj['url'].startswith('/eysk/'): continue
                
                obj_links.append(obj['url'])
            cs.save_objects(obj_links, cu, c)

        else:
            print(user['user_url'])

        #r = requests.get(cs.domain_url + user['user_url'])
        #if r.status_code == 404: continue
        
        #obj_links = get_obj_links_from_page(r.content)
        #for obj_link in obj_links:
        #    print(obj_link)



        curIndex.save(user['user_id'])

        time.sleep(7)

    curIndex.save(1)
    
    
    
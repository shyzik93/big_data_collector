import re
import sqlite3
import lxml.html as html
import requests
import time
import os

import collect_proxies

""" 
Р�СЃС‚РѕСЂРёСЏ СЃС‚Р°С‚СЃСѓСЃР° (СЂР°Р·РјРµС‰РµРЅРѕ, Р·Р°РєСЂС‹С‚Рѕ, 
РїРµСЂРµСЂР°Р·РјРµС‰РµРЅРѕ) """

path_pages = os.path.join(os.getcwd(), "pages")
path_data = os.path.join(os.getcwd(), "data")

if not os.path.exists(path_pages): os.makedirs(path_pages)
if not os.path.exists(path_data): os.makedirs(path_data)

proxies = collect_proxies.Proxies()

def get_categories(page):
    page = html.document_fromstring(page)
    links = page.cssselect(".rubricator-submenu-18HMk a")
    return [link.get("href") for link in links]

def get_objects(page):
    page = html.document_fromstring(page)
    objects = page.cssselect('.item_table-header a[itemprop="url"]')
    return [o.get("href") for o in objects]

def save_objects(object_urls, cu, c):
    ins_sql = "INSERT INTO `realty` (`realty_url`, `realty_ext_id`) VALUES "
    _ins_values = []
    ins_values = []

    upd_sql = "UPDATE `realty` SET `realty_url`=? WHERE `realty_ext_id`=?"
    upd_values = []

    for url in object_urls:

        is_absent = 0

        obj_id = int(url.split('_')[-1])

        sel_sql = "SELECT `realty_id` FROM `realty` WHERE `realty_ext_id`=?"
        res = cu.execute(sel_sql, (obj_id,)).fetchall()

        if len(res) == 0: is_absent = 1
        
        if is_absent: # for insert
            _ins_values.append("(?, ?)")
            ins_values.append(url)
            ins_values.append(obj_id)
        else: # for update
            upd_values.append((url, obj_id))

    # insert

    if ins_values:
        cu.execute(ins_sql + ",".join(_ins_values), ins_values)
        c.commit()

    # update

    if upd_values:
        for v in upd_values:
            cu.execute(upd_sql, v)
        c.commit()

def get_count_pages(page):
    page = html.document_fromstring(page)
    link = page.cssselect(".pagination-pages a.pagination-page")

    if not link: return 1 # only one page, because the paginator is absent

    url = link[-1].get('href')
    q = url.split('?')[-1]
    for p in q.split('&'):
        if p.startswith('p='): return int(p.split('=')[-1])

def get_objects2(link, cu, c, max_page=None):
    print('   ', link)
    r = requests.get(link)#, proxies={'https':proxies+1})
    objects = get_objects(r.content)
    save_objects(objects, cu, c)

    if max_page is None: max_page = get_count_pages(r.content)
    return max_page, len(objects)

if __name__ == '__main__':

    c = sqlite3.connect(os.path.join(path_data, 'data_avito.db'))
    c.row_factory = sqlite3.Row
    cu = c.cursor()
    cu.executescript('''
      CREATE TABLE IF NOT EXISTS realty (
        realty_id INTEGER PRIMARY KEY,
        realty_price INTEGER,
        realty_m2_building INTEGER, --  / 10 (common square)
        realty_m2_kitchen INTEGER,  -- / 10
        realty_m2_living INTEGER,  -- / 10
        realty_m2_landing INTEGER,  -- / 10
        realty_type_building TEXT,
        realty_address TEXT,
        realty_description TEXT,
        realty_floor_total INTEGER,
        realty_deal_type_id INTEGER,
        realty_price_arenda_type TEXT,
        realty_floor INTEGER,
        realty_count_rooms INTEGER,
        realty_date DATETIME DEFAULT TIMESTAMP,
        realty_url TEXT,
        realty_ext_id INTEGER UNIQUE);
      CREATE TABLE IF NOT EXISTS status (
        status_id INTEGER PRIMARY KEY,
        status_name TEXT);
      CREATE TABLE IF NOT EXISTS realty_status (
        realty_status_id INTEGER PRIMARY KEY,
        real_id INTEGER,
        status_id INTEGER,
        realty_status_date DATETIME DEFAULT TIMESTAMP);
      CREATE TABLE IF NOT EXISTS realty_prices (
        realty_prices_id INTEGER PRIMARY KEY,
        realty_id INTEGER,
        realty_price INTEGER,
        realty_price_date DATETIME DEFAULT TIMESTAMP);''')

    domain_url = "https://avito.ru"

    r = requests.get(domain_url+"/eysk/nedvizhimost/")#, proxies={'https':proxies+1})
    time.sleep(15)
    print(r.status_code)
    cat_links = get_categories(r.content)

    for i, cat_link in enumerate(cat_links):
        print(cat_link)

        #cat_path = os.path.join(path_pages, "pages/"+cat_link.split('?')[0].replace('/', '_')+'.html')
        #with open(cat_path, 'wb') as f:
        #    f.write(r.content)

        # get objects

        max_page, count_objects = get_objects2(domain_url+cat_link, cu, c)
        print('    pages:', max_page)

        for cur_page in range(1, max_page+1):
            max_page, count_objects = get_objects2(domain_url+cat_link+'&p='+str(cur_page), cu, c, max_page)
            time.sleep(7)
            print('    objects on page '+str(cur_page)+':', count_objects)

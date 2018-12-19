import re
import sqlite3
import lxml.html as html
import requests
import time

""" 
Р�СЃС‚РѕСЂРёСЏ СЃС‚Р°С‚СЃСѓСЃР° (СЂР°Р·РјРµС‰РµРЅРѕ, Р·Р°РєСЂС‹С‚Рѕ, 
РїРµСЂРµСЂР°Р·РјРµС‰РµРЅРѕ) """

def get_categories(page):
    page = html.document_fromstring(page)
    links = page.cssselect(".rubricator-submenu-18HMk a")
    return [link.get("href") for link in links]

def get_objects(page):
    page = html.document_fromstring(page)
    objects = page.cssselect('.item_table-header a[itemprop="url"]')
    return [o.get("href") for o in objects]

def save_objects(object_urls, cu):
    ins_sql += "INSERT INTO `realty` (`realty_url`, `realty_ext_id`) VALUES "
    _ins_values = []
    ins_values = []

    for url in object_urls:
        is_absent = 0

        realty_id = int(url.split('_')[-1])

        sel_sql = "SELECT `realty_id` FROM `realty` WHERE `realty_id`=?"
        r = cu.execute(sel_sql, realty_id)
        
        if is_absent:
            _ins_values.add("(?, ?)")
            ins_values.add(obj_url)
            ins_values.add(obj_id)

            cu.execute(ins_sql + ",".join(_ins_values), ins_values)

if __name__ == '__main__':
    # РёРЅРёС†РёР°Р»РёР·Р°С†РёСЏ Р‘Р”
    c = sqlite3.connect('data_avito.db')
    c.row_factory = sqlite3.Row
    cu = c.cursor()
    cu.executescript('''
      CREATE TABLE IF NOT EXISTS realty (
        realty_id INTEGER PRIMARY KEY,
        realty_price INTEGER,
        realty_m2_building INTEGER,
        realty_m2_landing INTEGER,
        realty_count_rooms INTEGER,
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
        realty_price_date INTEGER);''')
    
    domain_url = "https://avito.ru"

    r = requests.get(domain_url+"/eysk/nedvizhimost/")
    cat_links = get_categories(r.content)
    
    for i, cat_link in enumerate(cat_links):
        r = requests.get(domain_url+cat_link)
        
        cat_path = "pages/"+cat_link.split('?')[0].replace('/', '_')+'.html'
        with open(cat_path, 'wb') as f:
            f.write(r.content)

        # get objects

        objects = get_objects(r.content)
        #save_objects(objects, cu)

        print(objects, len(objects))
        exit()

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
    print(links)

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
    
    r = requests.get("https://avito.ru/eysk/nedvizhimost/")
    print(r)

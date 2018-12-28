#!/usr/bin/env python3

"""
Author: Polyakov Konstantin
Date: 2018-12-19
Place: Yeysk, Russia
"""

import re
import sqlite3
import lxml.html as html
import requests
import time
import os

import config_site_avito as cs

def get_categories(page):
    page = html.document_fromstring(page)
    #links = page.cssselect(".rubricator-submenu-18HMk a")
    #return [link.get("href") for link in links]
    return ['https://krasnodar.cian.ru/kupit-kvartiru-krasnodarskiy-kray-eysk/']

if __name__ == '__main__':

    c, cu = cs.get_db()
    proxies = collect_proxies.Proxies(c, cu)
    
    r = proxies.open_url(cs.domain_url, cs.is_blocked)
    print(r.status_code)
    cat_links = get_categories(r.content)

    for i, cat_link in enumerate(cat_links):
        print(cat_link)
        
        r = cs.proxies.open_url(cat_link, cs.is_blocked)
        
        'href="https://krasnodar.cian.ru/sale/flat/198690529/"'
        
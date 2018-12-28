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
import argparse

import config_site_avito as cs
import parser_tools as pt

def get_categories(page):
    page = html.document_fromstring(page)
    links = page.cssselect(".rubricator-submenu-18HMk a")
    return [link.get("href") for link in links]

def get_objects(page):
    page = html.document_fromstring(page)
    objects = page.cssselect('.item_table-header a[itemprop="url"]')
    return [o.get("href") for o in objects]

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
    r = proxies.open_url(link, cs.is_blocked)
    #r = requests.get(link)#, proxies={'https':cs.proxies+1})
    objects = get_objects(r.content)
    cs.save_objects(objects, cu, c)

    if max_page is None: max_page = get_count_pages(r.content)
    return max_page, len(objects)

if __name__ == '__main__':

    cli_parser = argparse.ArgumentParser(description='Script for getting analitic info about real estates. Author: Polyakov Konstantin')
    cli_parser.add_argument('--settlement', default='eysk')

    cli_args = cli_parser.parse_args()

    c, cu = cs.get_db()
    proxies = pt.Proxies(c, cu, 'avito', cs.path_data)

    r = proxies.open_url(cs.domain_url+"/"+cli_args.settlement+"/nedvizhimost/", cs.is_blocked)
    print(r.status_code)
    cat_links = get_categories(r.content)

    for i, cat_link in enumerate(cat_links):
        print(cat_link)

        # get objects

        max_page, count_objects = get_objects2(cs.domain_url+cat_link, cu, c)
        print('    pages:', max_page)

        for cur_page in range(1, max_page+1):
            max_page, count_objects = get_objects2(cs.domain_url+cat_link+'&p='+str(cur_page), cu, c, max_page)
            print('    objects on page '+str(cur_page)+':', count_objects)

    exit(1)
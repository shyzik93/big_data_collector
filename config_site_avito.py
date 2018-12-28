#!/usr/bin/env python3

"""
Author: Polyakov Konstantin
Date: 2018-12-22
Place: Yeysk, Russia
"""

from config_site import *
import os
import datetime
import sqlite3

domain_url = "https://avito.ru"
site_id = 1

def is_blocked(r):
    return r.url.endswith('/blocked') or r.status_code == 403
    
#TODO переписать на регулярных выражениях    
# 4 декабря 18:00 | 4 декабря 2015 | вчера 15:00 | сегодя 15:00
def transform_date(date_publication): 
    #print(date_publication)
    time_publication = date_publication.pop()
    if ':' in time_publication:
        year = datetime.date.today().strftime('%Y')
        time_publication = time_publication + ":00"
    else:
        year = time_publication
        time_publication = '00:00:00'

    if date_publication[0] == 'сегодня':
        date_publication = datetime.date.today().strftime('%Y-%m-%d')#datetime.date.today().strftime('%Y-%m-%d')
    elif date_publication[0] == 'вчера':
        date_publication = (datetime.date.today()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')#datetime.strftime('%m/%d/%Y %I:%M%p')
    else:
        day_publication = date_publication[0].rjust(2, '0')
        month_publication = date_publication[1]
        if month_publication.startswith('янв'): month_publication = '01'
        elif month_publication.startswith('фев'): month_publication = '02'
        elif month_publication.startswith('март'): month_publication = '03'
        elif month_publication.startswith('апрел'): month_publication = '04'
        elif month_publication.startswith('ма'): month_publication = '05'
        elif month_publication.startswith('июн'): month_publication = '06'
        elif month_publication.startswith('июл'): month_publication = '07'
        elif month_publication.startswith('авг'): month_publication = '08'
        elif month_publication.startswith('сент'): month_publication = '09'
        elif month_publication.startswith('окт'): month_publication = '10'
        elif month_publication.startswith('нояб'): month_publication = '11'
        elif month_publication.startswith('декаб'): month_publication = '12'

        date_publication = year+'-'+month_publication+'-'+day_publication
                
    return date_publication +" "+ time_publication

def transform_price(p):
    price = []
    _price = list(str(p))
    _price.reverse()
    for i, s in enumerate(_price):
        price.append(s)
        if (i+1) % 3 == 0: price.append(' ')
    price.reverse()
    return ''.join(price)

def save_objects(object_urls, cu, c):
    ins_sql = "INSERT INTO `realty` (`realty_url`, `realty_ext_id`, `site`) VALUES "
    _ins_values = []
    ins_values = []

    upd_sql = "UPDATE `realty` SET `realty_url`=? WHERE `realty_ext_id`=? AND `realty_is_redirect`=NULL AND `site`=?"
    upd_values = []

    for url in object_urls:

        is_absent = 0

        obj_id = int(url.split('_')[-1])

        sel_sql = "SELECT `realty_id` FROM `realty` WHERE `realty_ext_id`=? AND `site`=?"
        res = cu.execute(sel_sql, (obj_id,site_id)).fetchall()

        if len(res) == 0: is_absent = 1
        
        if is_absent: # for insert
            _ins_values.append("(?, ?, ?)")
            ins_values.append(url)
            ins_values.append(obj_id)
            ins_values.append(site_id)
        else: # for update
            upd_values.append((url, obj_id, site_id))

    # insert

    if ins_values:
        cu.execute(ins_sql + ",".join(_ins_values), ins_values)
        c.commit()

    # update

    if upd_values:
        for v in upd_values:
            cu.execute(upd_sql, v)
        c.commit()
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

"""
Добавляем нули к днюб даты
"""

if __name__ == '__main__':

    c = sqlite3.connect(os.path.join(cs.path_data, 'data_avito.db'))
    c.row_factory = sqlite3.Row
    cu = c.cursor()

    c2 = sqlite3.connect(os.path.join(cs.path_data, 'data_avito.db'))
    c2.row_factory = sqlite3.Row
    cu2 = c2.cursor()
    
    sql = "SELECT `realty_date_publication`, `realty_id` FROM `realty`"
    res = cu.execute(sql).fetchall()
    
    for row in res:
        
        if not row['realty_date_publication']: continue
        
        rdate, rtime = row['realty_date_publication'].split()
        rdate = rdate.split('-')
        if len(rdate[-1]) == 1:
            rdate[-1] = '0' + rdate[-1]
            rdate = '-'.join(rdate)
            
            #print(row['realty_date_publication'], ' -> ', rdate+' '+rtime)
            #continue
            
            sql = "UPDATE `realty` SET `realty_date_publication`=? WHERE `realty_id`=?"
            res2 = cu2.execute(sql, (rdate+' '+rtime, row['realty_id']))
            
            c2.commit()
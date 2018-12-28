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

if __name__ == '__main__':

    path_cur_user_id = os.path.join(cs.path_data, 'cur_user_id.txt')
    cur_user_id = cs.get_cur_index(path_cur_user_id)

    c = sqlite3.connect(os.path.join(cs.path_data, 'data_avito.db'))
    c.row_factory = sqlite3.Row
    cu = c.cursor()

    c2 = sqlite3.connect(os.path.join(cs.path_data, 'data_avito.db'))
    c2.row_factory = sqlite3.Row
    cu2 = c2.cursor()
    
    sql = "SELECT * FROM `user`"
    res = cu.execute(sql).fetchall()
    
    _user_ids = []
    
    for user in res:

        if not user['user_url']: continue

        if user['user_url'].startswith('/user/'):
            new_url = user['user_url'].split('?')
            if len(new_url) == 1: continue # уже обновли ранее
            new_url = new_url[0]
            
            if int(user['user_id']) in [int(i) for i in _user_ids]: continue

            sql = "SELECT * FROM `user` WHERE `user_url` LIKE ?"
            res2 = cu2.execute(sql, (new_url+'%',)).fetchall()
            user_ids = []
            for user2 in res2:
                user_ids.append(user2['user_id'])
                print(user2['user_name'], user2['user_url'])

            if res2:
                sql = "UPDATE `realty` SET `realty_user_id`=? WHERE `realty_user_id` IN ("+(','.join(['?' for i in user_ids]))+")"
                res2 = cu2.execute(sql, tuple([user['user_id']]+user_ids))
                c2.commit()
                print(user2['user_id'], user2['user_name'], user2['user_url'])

                sql = "UPDATE `user` SET `user_is_deleted`=1 WHERE `user_id` IN ("+(','.join(['?' for i in user_ids]))+")"
                res2 = cu2.execute(sql, tuple(user_ids))
                c2.commit()

                _user_ids += user_ids

         
            sql = "UPDATE `user` SET `user_url`=?, `user_is_deleted`=0 WHERE `user_id` = ?"
            res2 = cu2.execute(sql, (new_url,user['user_id']))
            c2.commit()

        else:
            pass
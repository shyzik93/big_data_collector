#!/usr/bin/env python3

"""
Author: Polyakov Konstantin
Date: 2018-12-22
Place: Yeysk, Russia
"""

# SQLIte3 API
# https://habr.com/post/321510/


import os
import sqlite3

import collect_proxies
from collect_proxies import Proxies
from cur_index import CurIndex

#path_data = os.path.join(os.getcwd(), "data")
#if not os.path.exists(path_pages): os.makedirs(path_pages)
path_data = "/root/parsers/data"
if not os.path.exists(path_data): os.makedirs(path_data)
path_templates = "/root/parsers/templates"
if not os.path.exists(path_templates): os.makedirs(path_templates)

def get_db():
    c = sqlite3.connect(os.path.join(path_data, 'data_avito.db'))
    c.row_factory = sqlite3.Row
    cu = c.cursor()
    
    cu.executescript('''
      CREATE TABLE IF NOT EXISTS realty (
        realty_id INTEGER PRIMARY KEY,
        realty_price INTEGER,
        realty_category TEXT,
        realty_m2_building INTEGER, --  / 10 (common square)
        realty_m2_kitchen INTEGER,  -- / 10
        realty_m2_living INTEGER,  -- / 10
        realty_m2_landing INTEGER,  -- / 10
        realty_s_to_town INTEGER, -- / 10
        realty_type_building TEXT,
        realty_type_object TEXT,
        realty_address TEXT,
        realty_description TEXT,
        realty_floor_total INTEGER,
        realty_deal_type_id INTEGER,
        realty_price_arenda_type TEXT,
        realty_floor INTEGER,
        realty_count_rooms INTEGER,
        realty_is_multi_rooms INTEGER,
        realty_wall_material INTEGER,
        realty_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        realty_user_id INTEGER,
        realty_lat TEXT,
        realty_lon TEXT,
        realty_date_publication DATETIME,

        realty_address_box TEXT,
        realty_builder_type_action TEXT,
        realty_builder TEXT,
        realty_name_of_building TEXT,
        realty_decoration TEXT,
        realty_date_deadline TEXT,

        realty_is_redirect INTEGER, -- redirect if page is deleted
        realty_url TEXT,
        site INTEGER, -- 1 - avito.ru, 2 - cian.ru
        realty_ext_id INTEGER UNIQUE);

      CREATE TABLE IF NOT EXISTS user_type (
        user_type_id INTEGER PRIMARY KEY,
        user_type_name TEXT);
      CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER PRIMARY KEY,
        user_name TEXT,
        user_type_id INTEGER,
        user_url TEXT,
        site INTEGER,
        user_is_deleted INTEGER);

      CREATE TABLE IF NOT EXISTS warning (
        warning_id INTEGER PRIMARY KEY,
        warning_name TEXT -- #TODO change in real db integer -> text!
      );
      CREATE TABLE IF NOT EXISTS realty_warning (
        realty_warning_id INTEGER PRIMARY KEY,
        warning_id INTEGER,
        realty_id INTEGER,
        realty_warning_date DATETIME DEFAULT CURRENT_TIMESTAMP);

      CREATE TABLE IF NOT EXISTS status (
        status_id INTEGER PRIMARY KEY,
        status_name TEXT);
      CREATE TABLE IF NOT EXISTS realty_status (
        realty_status_id INTEGER PRIMARY KEY,
        real_id INTEGER,
        status_id INTEGER,
        realty_status_date DATETIME DEFAULT CURRENT_TIMESTAMP);

      CREATE TABLE IF NOT EXISTS history_publ_date (
        history_publ_date_id INTEGER PRIMARY KEY,
        history_realty_id INTEGER,
        history_publ_date DATETIME,
        history_date DATETIME DEFAULT CURRENT_TIMESTAMP
      );
      CREATE TABLE IF NOT EXISTS history_price (
        history_price_id INTEGER PRIMARY KEY,
        history_realty_id INTEGER,
        history_price INTEGER,
        history_date DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS user_contact (
        user_contact_id INTEGER PRIMARY KEY,
        user_contact_user_id INTEGER,
        user_contact_type TEXT,
        user_contact_data TEXT
      );

      CREATE TABLE IF NOT EXISTS proxy (
        proxy_id INTEGER PRIMARY KEY,
        proxy_ip TEXT,
        proxy_port INTEGER,
        site_avito DATETIME,
        site_cian DATETIME,
        date_added DATETIME DEFAULT CURRENT_TIMESTAMP
      );
      ''')
    
    return c, cu

class DBHistory():

    def __init__(self, c, cu):
        self.cu = cu
        self.c = c

    def save(self, realty_id, table_name, value_name, new_value):
        sql = "SELECT * FROM `"+table_name+"` WHERE `history_realty_id`=? ORDER BY `history_date` DESC LIMIT 1"
        res2 = self.cu.execute(sql, (realty_id,)).fetchall()
        if res2: res2 = res2[0]
        if not res2 or res2[value_name] != new_value:
            sql = "INSERT INTO `"+table_name+"` (`history_realty_id`, `"+value_name+"`) VALUES (?, ?); "
            self.cu.execute(sql, (realty_id, new_value))

    def insert_and_commit(self):
        self.c.commit()

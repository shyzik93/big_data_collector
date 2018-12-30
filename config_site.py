#!/usr/bin/env python3

"""
Author: Polyakov Konstantin
Date: 2018-12-22
Place: Yeysk, Russia
"""

# SQLIte3 API
# https://habr.com/post/321510/


import os
#import sqlite3
import pymysql
import configparser

import parser_tools as pt

'''
Traceback (most recent call last):
  File "collect_obj_data_avito.py", line 290, in <module>
    history.insert_and_commit()
  File "/root/parsers/config_site.py", line 139, in insert_and_commit
    def insert_and_commit(self):
sqlite3.OperationalError: database is locked
'''

#path_data = os.path.join(os.getcwd(), "data")
#if not os.path.exists(path_pages): os.makedirs(path_pages)

path_main = os.path.dirname(__file__)

path_data = os.path.join(path_main, "data")
if not os.path.exists(path_data): os.makedirs(path_data)
path_templates = os.path.join(path_main, "templates")
if not os.path.exists(path_templates): os.makedirs(path_templates)

path_db = os.path.join(path_data, 'data_avito.db')

def get_db():
    #c = sqlite3.connect(path_db)
    #c.row_factory = sqlite3.Row
    #cu = c.cursor()

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(path_main), 'parser_config.ini'))
    
    c = pymysql.connect(
        db=config['db_name'],
        user=config['db_user'],
        passwd=config['db_password'],
        host=config['db_host'])
    cu = c.cursor()

    
    """cu.executescript('''
      CREATE TABLE IF NOT EXISTS realty (
        realty_id INTEGER PRIMARY KEY,
        realty_price INTEGER,
        realty_category VARCHAR(10),
        realty_m2_building INTEGER, --  / 10 (common square)
        realty_m2_kitchen INTEGER,  -- / 10
        realty_m2_living INTEGER,  -- / 10
        realty_m2_landing INTEGER,  -- / 10
        realty_s_to_town INTEGER, -- / 10
        realty_type_building VARCHAR(255),
        realty_type_object VARCHAR(255),
        realty_address VARCHAR(255),
        realty_description TEXT,
        realty_floor_total INTEGER,
        realty_deal_type_id INTEGER,
        realty_price_arenda_type VARCHAR(10),
        realty_floor INTEGER,
        realty_count_rooms INTEGER,
        realty_is_multi_rooms INTEGER,
        realty_wall_material INTEGER,
        realty_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        realty_user_id INTEGER,
        realty_lat VARCHAR(20),
        realty_lon VARCHAR(20),
        realty_date_publication DATETIME,

        realty_address_box VARCHAR(255),
        realty_builder_type_action VARCHAR(255),
        realty_builder VARCHAR(255),
        realty_name_of_building VARCHAR(255),
        realty_decoration VARCHAR(255),
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
        user_contact_type VARCHAR(20),
        user_contact_data VARCHAR(255)
      );

      CREATE TABLE IF NOT EXISTS proxy (
        proxy_id INTEGER PRIMARY KEY,
        proxy_ip VARCHAR(255),
        proxy_port INTEGER,
        site_avito DATETIME,
        site_cian DATETIME,
        date_added DATETIME DEFAULT CURRENT_TIMESTAMP
      );
      ''')"""
    
    return c, cu
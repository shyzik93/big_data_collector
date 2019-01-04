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
import datetime
import argparse

import config_site_avito as cs
import parser_tools as pt

cli_parser = argparse.ArgumentParser(description='')
cli_parser.add_argument('--only-empty', default=None)

cli_args = cli_parser.parse_args()

#TODO collect info about publicator (fio, name of organization)

def func_compare_publ_date(old, new):
    return old.split()[0] == new.split()[0]

if __name__ == '__main__':
    curIndex = pt.CurIndex(os.path.join(cs.path_data, 'cur_obj_id.txt'))
    cur_obj_id = curIndex.get()

    c, cu = cs.get_db()
    c2, cu2 = cs.get_db()
    proxies = pt.Proxies(c, cu, 'avito', cs.path_data)
    history = pt.DBHistory(c2, cu2)

    #sql = "SELECT `realty_price`, `realty_id`, `realty_url`, `realty_ext_id` FROM `realty` WHERE `realty_id`>=? AND `realty_is_redirect` IS NULL AND `site`=? "
    sql = "SELECT `realty_price`, `realty_id`, `realty_url`, `realty_ext_id` FROM `realty` WHERE `realty_id`>=? AND `site`=? "
    if cli_args.only_empty: sql += " AND `realty_price` is NULL "
    res = cu.execute(sql, (cur_obj_id, cs.site_id)).fetchall()
    for obj in res:
        print(obj['realty_id'])
        print(obj['realty_url'], end='  ')
        #TODO if status_code is 404, the object is unpablished. Add the sirow into `realty_status` table
        # and we need to got into the publicator's pager and try to see the object in 'finished' list of objects

        # -------- getting page

        r = proxies.open_url(cs.domain_url + obj['realty_url'], cs.is_blocked)

        print(r.status_code)

        url = r.url.split('avito.ru')[1]
        if r.status_code == 404 or url != obj['realty_url']: # the advertisementy is deleted on the avito.ru
            sql = "UPDATE `realty` SET `realty_is_redirect`=1 WHERE `realty_id`=?"
            cu2.execute(sql, (obj['realty_id'],))
            c2.commit()
            curIndex.save(obj['realty_id'])
            continue


        # -------- processing page

        
        page = html.document_fromstring(r.content)

        fields = {
            #'realty_category': '',
            #'realty_price': '',
            #'realty_price_arenda_type': '',
            #'realty_m2_building': '',
            #'realty_m2_kitchen': '',
            #'realty_m2_landing': '',
            #'realty_m2_living': '',
            #'realty_m2_landing': '',
            #'realty_s_to_town': '',
            #'realty_count_rooms': '',
            #'realty_type_building': '',
            #'realty_type_object': '',
            #'realty_wall_material': '',
            #'realty_floor_total': '',
            #'realty_floor': '',
            #'realty_address': '',
            #'realty_description': '',
            #'realty_deal_type_id':'',
            #'realty_date_publication':None,
            'realty_is_redirect':None,
        }

        # category
        
        cat = obj['realty_url'].split('/')[2] # zero is empty, first is town
        if cat == 'kvartiry': fields['realty_category'] = 'flat'
        elif cat == 'komnaty': fields['realty_category'] = 'room'
        elif cat == 'doma_dachi_kottedzhi': fields['realty_category'] = 'house'
        elif cat == 'zemelnye_uchastki': fields['realty_category'] = 'land'
        elif cat == 'garazhi_i_mashinomesta': fields['realty_category'] = 'garage'
        elif cat == 'kommercheskaya_nedvizhimost': fields['realty_category'] = 'business'
        elif cat == 'nedvizhimost_za_rubezhom': fields['realty_category'] = 'abroad'

        # price

        price = page.cssselect('.item-view-header span[itemprop=price]')
        if price:
            price = price[0]
            price = int(price.get('content'))
            fields['realty_price'] = price

        # type of deal

        price = page.cssselect('.item-view-header span.price-value-string')
        if price:
            price = price[0]
            arenda = price.text_content().split()[-1];
            if arenda == 'год': fields['realty_price_arenda_type'] = 'year'
            elif arenda == 'месяц': fields['realty_price_arenda_type'] ='month'
            elif arenda == 'сутки': fields['realty_price_arenda_type'] ='day'

            
        # publication date

        date_publication = page.cssselect('.item-view-header .title-info-metadata-item')
        if date_publication:
            date_publication = date_publication[0]
            date_publication = date_publication.text_content().split(',')[1]
            date_publication = date_publication.strip().split()[1:]

            fields['realty_date_publication'] = cs.transform_date(date_publication)

        # other

        items = page.cssselect('.item-view-block .item-params-list-item')

        for item in items:

            name, value = item.text_content().strip().split(':', 1)
            name = name.strip()
            value = value.strip()
            
            print('    ', name, ':' ,value)

            if name == 'Общая площадь' or name == 'Площадь дома':
                fields['realty_m2_building'] = int(float(value.split()[0])*10)
            elif name == 'Площадь кухни':
                fields['realty_m2_kitchen'] = int(float(value.split()[0])*10)
            elif name == 'Площадь участка':
                fields['realty_m2_landing'] = int(float(value.split()[0])*10)
            elif name == 'Жилая площадь':
                fields['realty_m2_living'] = int(float(value.split()[0])*10)
            elif name == 'Площадь':
                fields['realty_m2_landing'] = int(float(value.split()[0])*10)
            elif name == 'Расстояние до города':
                fields['realty_s_to_town'] = int(float(value.split()[0])*10)
            elif name == 'Количество комнат':
                if value == 'студии':
                    fields['realty_count_rooms'] = 0 #TODO add new field
                elif value == 'многокомнатные':
                    fields['realty_is_multi_rooms'] = 1
                else:
                    fields['realty_count_rooms'] = int(value.split('-')[0])
            elif name == 'Тип дома':
                fields['realty_type_building'] = value
            elif name == 'Вид объекта':
                fields['realty_type_object'] = value
            elif name == 'Материал стен':
                fields['realty_wall_material'] = value
            elif name == 'Этажей в доме':
                fields['realty_floor_total'] = int(value.replace('>', '').strip())
            elif name == 'Этаж':
                fields['realty_floor'] = int(value)

            elif name == 'Корпус, строение':
                fields['realty_address_box'] = value
            elif name == 'Тип участия':
                fields['realty_builder_type_action'] = value
            elif name == 'Официальный застройщик':
                fields['realty_builder'] = value
            elif name == 'Название объекта недвижимости':
                fields['realty_name_of_building'] = value
            elif name == 'Отделка':
                fields['realty_decoration'] = value
            elif name == 'Срок сдачи':
                fields['realty_date_deadline'] = value

         # address

        address = page.cssselect('.item-view-map .item-map-location')
        if address:
            address = address[0]
            address.remove(address.cssselect('.item-map-control')[0])
            _address = []
            for child in address.getchildren():
                _address.append(child.text_content().strip())
            fields['realty_address'] = '  | '.join(_address[1:])
        
        # description

        descr = page.cssselect('.item-view-block .item-description-text')
        if descr:
            descr = descr[0]
            fields['realty_description'] = descr.text_content().strip()

        # type of deal

        deal = page.cssselect('.item-navigation .breadcrumbs ')
        if deal:
            deal = deal[0]
            deal = deal.text_content()
            if 'Куплю' in deal or 'Купить' in deal:     fields['realty_deal_type_id'] = 1#'buy'
            elif 'Продам' in deal or 'Продать' in deal: fields['realty_deal_type_id'] = 2#'sell'
            elif 'Сдам' in deal or 'Сдать' in deal:     fields['realty_deal_type_id'] = 3#'give_rent'
            elif 'Сниму' in deal or 'Снять' in deal:    fields['realty_deal_type_id'] = 4#'get_rent'

        # publicator

        seller_block = page.cssselect('.seller-info-col')
        if not seller_block: seller_block = page.cssselect('.seller-info-prop')
        if seller_block:
            seller_block = seller_block[0]
            
            seller_name = seller_block.getchildren()[0].getchildren()[0]
            if seller_name.getchildren(): seller_name = seller_name.getchildren()[0].text_content().strip()
            else: seller_name = seller_name.text_content().strip()

            seller_url = seller_block.getchildren()[0].getchildren()[0]
            if seller_url.getchildren(): seller_url  = seller_url.getchildren()[0].get('href').strip()
            else: seller_url  = ''
            if seller_url.startswith('/user/'): seller_url = seller_url.split('?')[0]

            seller_type = seller_block.getchildren()[1].text_content()
            
            print('    SName:', seller_name, seller_url)
            print('    SType:', seller_type)
            
            # saving type of publicator
            
            sql = "SELECT * FROM `user_type` WHERE `user_type_name`=?"
            res2 = cu2.execute(sql, (seller_type,)).fetchall()
            if len(res2) == 0:
                sql = "INSERT INTO `user_type` (`user_type_name`) VALUES (?)"
                res2 = cu2.execute(sql, (seller_type,))
                c2.commit()

            # saving publicator
          
            sql = "SELECT * FROM `user` WHERE `user_name`=? AND `user_url`=? AND `site`=1"
            res2 = cu2.execute(sql, (seller_name,seller_url)).fetchall()
            if len(res2) == 0:
                sql = "INSERT INTO `user` (`user_name`, `user_url`, `user_type_id`, `site`) SELECT ?, ?, `user_type`.`user_type_id`, ? FROM `user_type` WHERE `user_type`.`user_type_name`=? "
                res2 = cu2.execute(sql, (seller_name,seller_url,cs.site_id,seller_type))
                c2.commit()

            # get id of publicator

            sql = "SELECT * FROM `user` WHERE `user_name`=? AND `user_url`=? AND `site`=?"
            res2 = cu2.execute(sql, (seller_name,seller_url,cs.site_id)).fetchall()
            if res2:
                fields['realty_user_id'] = res2[0]['user_id']
                
        # Warning message. 

        warning = page.cssselect('.item-view-warning-content')
        if warning:
            warning = warning[0]
            warning = warning.text_content().strip()
            print('    Warning:', warning)

            # save warning message
            
            sql = "SELECT * FROM `warning` WHERE `warning_name`=?"
            res2 = cu2.execute(sql, (warning,)).fetchall()
            if len(res2) == 0:
                sql = "INSERT INTO `warning` (`warning_name`) VALUES (?) "
                res2 = cu2.execute(sql, (warning,))
                c2.commit()
                
            # saving warning for realty
            
            sql = "SELECT * FROM `realty_warning`, `warning` WHERE `realty_warning`.`warning_id`=`warning`.`warning_id` AND `warning`.`warning_name`=? AND `realty_warning`.`realty_id`=? ORDER BY `realty_warning`.`realty_warning_date` DESC LIMIT 1"
            res2 = cu2.execute(sql, (warning,obj['realty_id'])).fetchall()
            if len(res) == 0:
                sql = "INSERT INTO `realty_warning` (`warning_id`, `realty_id`) SELECT `warning`.`warning_id`, ? FROM `warning` WHERE `warning`.`warning_name`=? "
                res2 = cu2.execute(sql, (obj['realty_id'],warning))
                c2.commit()

        # Map

        objmap = page.cssselect('.item-map-wrapper')
        if objmap:
            objmap = objmap[0]
            fields['realty_lat'] = objmap.get('data-map-lat')
            fields['realty_lon'] = objmap.get('data-map-lon')

        # check if all new data is empty

        count_empty = 0
        for k, v in fields.items():
            if not v: count_empty += 1

        # history of different properties

        if 'realty_date_publication' in fields: history.save(obj['realty_id'], "history_publ_date", 'history_publ_date', fields['realty_date_publication'], func_compare_publ_date)
        if 'realty_price' in fields: history.save(obj['realty_id'], "history_price", 'history_price', fields['realty_price'])
        history.insert_and_commit()

        # updating...
        
        keys = []
        values = []
        
        for key, value in fields.items():
            keys.append('`'+key+'`=?')
            values.append(value)

        values.append(obj['realty_id'])
        
        #if count_empty < len(fields)-2: # если была переадресация, то поля не должны затираться

        sql = "UPDATE `realty` SET " + ','.join(keys) + 'WHERE `realty_id`=?'
        cu2.execute(sql, tuple(values))
        c2.commit()

        curIndex.save(obj['realty_id'])

        #print(fields)

        #time.sleep(5)

    #curIndex.save(1)
    exit(1)

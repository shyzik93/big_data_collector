import re
import sqlite3
import lxml.html as html
import requests
import time
import os
import datetime

import collect_proxies

path_data = os.path.join(os.getcwd(), "data")

if not os.path.exists(path_data): os.makedirs(path_data)

proxies = collect_proxies.Proxies()

#TODO collect info about publicator (fio, name of organization)

if __name__ == '__main__':
    cur_obj_id = 1
    path_cur_obj_id = os.path.join(path_data, 'cur_obj_id.txt')
    if os.path.exists(path_cur_obj_id):
        with open(path_cur_obj_id) as f:
            _cur_obj_id = f.read().strip()
            # if file is empty
            if _cur_obj_id: cur_obj_id = int(_cur_obj_id)

    c = sqlite3.connect(os.path.join(path_data, 'data_avito.db'))
    c.row_factory = sqlite3.Row
    cu = c.cursor()

    domain_url = "https://avito.ru"

    sql = "SELECT `realty_price`, `realty_id`, `realty_url`, `realty_ext_id` FROM `realty` WHERE `realty_id`>=?"
    r = cu.execute(sql, (cur_obj_id, )).fetchall()
    for obj in r:
        print(domain_url + obj['realty_url'])
        #TODO if status_code is 404, the object is unpablished. Add the sirow into `realty_status` table
        # and we need to got into the publicator's pager and try to see the object in 'finished' list of objects
        r = requests.get(domain_url + obj['realty_url'])
        print('    Status code:', r.status_code)
        if r.status_code == 404: contnue
        page = html.document_fromstring(r.content)

        fields = {
            'realty_category': '',
            'realty_price': '',
            'realty_price_arenda_type': '',
            'realty_m2_building': '',
            'realty_m2_kitchen': '',
            'realty_m2_landing': '',
            'realty_m2_living': '',
            'realty_m2_landing': '',
            'realty_s_to_town': '',
            'realty_count_rooms': '',
            'realty_type_building': '',
            'realty_type_object': '',
            'realty_wall_material': '',
            'realty_floor_total': '',
            'realty_floor': '',
            'realty_address': '',
            'realty_description': '',
            'realty_deal_type_id':'',
        }

        # category
        
        cat = obj['realty_url'].split('/')[2] # zero is empty, first is town
        if cat == 'kvartiry': fields['realty_category'] = 'flat'
        elif cat == 'komnaty': fields['realty_category'] = 'flat'
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
            
            # log of price history
            
            if price != fields['realty_price']:
                #TODO logging of price
                pass

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

            time_publication = date_publication.pop() + ":00"

            if date_publication[0] == 'сегодня':
                date_publication = datetime.date.today().strftime('%Y-%m-%d')#datetime.strftime('%m/%d/%Y %I:%M%p')
            elif date_publication[0] == 'вчера':
                date_publication = datetime.date.today().strftime('%Y-%m-%d')#datetime.date.today().strftime('%Y-%m-%d')
            else:
                day_publication = date_publication[0]
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

                date_publication = datetime.date.today().strftime('%Y')+'-'+month_publication+'-'+day_publication
                
            fields['realty_date_publication'] = date_publication +" "+ time_publication

        # Warning message. 

        warning = page.cssselect('.item-view-warning-content')
        if warning:
            warning = warning[0]
            print('    Warning:', warning.text_content().strip())

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
                    fields['realty_count_rooms'] = 0
                else:
                    fields['realty_count_rooms'] = int(value.split('-')[0])
            elif name == 'Тип дома':
                fields['realty_type_building'] = value
            elif name == 'Вид объекта':
                fields['realty_type_object'] = value
            elif name == 'Материал стен':
                fields['realty_wall_material'] = value
            elif name == 'Этажей в доме':
                fields['realty_floor_total'] = int(value)
            elif name == 'Этаж':
                fields['realty_floor'] = int(value)

         # address

        address = page.cssselect('.item-view-map .item-map-location')
        if address:
            address = address[0]
            address.remove(address.cssselect('.item-map-control')[0])
            _address = []
            for child in address.getchildren():
                _address.append(child.text_content().strip())
            fields['realty_address'] = ', '.join(_address[1:])
        
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
            if 'Куплю' in deal: fields['realty_deal_type_id'] = 1#'buy'
            elif 'Продам' in deal: fields['realty_deal_type_id'] = 2#'sell'
            elif 'Сдам' in deal: fields['realty_deal_type_id'] = 3#'give_rent'
            elif 'Сниму' in deal: fields['realty_deal_type_id'] = 4#'get_rent'

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

            seller_type = seller_block.getchildren()[1].text_content()
            
            print('    SName:', seller_name, seller_url)
            print('    SType:', seller_type)

            # saving type of publicator
            
            sql = "SELECT * FROM `user_type` WHERE `user_type_name`=?"
            res = cu.execute(sql, (seller_type,)).fetchall()
            if len(res) == 0:
                sql = "INSERT INTO `user_type` (`user_type_name`) VALUES (?)"
                res = cu.execute(sql, (seller_type,))
                c.commit()

            # saving publicator
          
            sql = "SELECT * FROM `user` WHERE `user_name`=? AND `user_url`=?"
            res = cu.execute(sql, (seller_name,seller_url)).fetchall()
            if len(res) == 0:
                sql = "INSERT INTO `user` (`user_name`, `user_url`, `user_type_id`) SELECT ?, ?, `user_type`.`user_type_id` FROM `user_type` WHERE `user_type`.`user_type_name`=? "
                res = cu.execute(sql, (seller_name,seller_url,seller_type))
                c.commit()

            # get id of publicator

            sql = "SELECT * FROM `user` WHERE `user_name`=? AND `user_url`=?"
            res = cu.execute(sql, (seller_name,seller_url)).fetchall()
            print(res)
            if res:
                fields['realty_user_id'] = res[0]['user_id']
        
        # check if all new data is empty

        count_empty = 0
        for k, v in fields.items():
            if not v: count_empty += 1

        # updating...
        
        keys = []
        values = []
        
        for key, value in fields.items():
            keys.append('`'+key+'`=?')
            values.append(value)

        values.append(obj['realty_id'])

        if count_empty < len(fields)-2: # если была переадресация, то поля не должны затираться

            sql = "UPDATE `realty` SET " + ','.join(keys) + 'WHERE `realty_id`=?'
            res = cu.execute(sql, tuple(values))
            c.commit()

        with open(path_cur_obj_id, 'w') as f: f.write(str(obj['realty_id']))

        #print(fields)

        time.sleep(5)

    with open(path_cur_obj_id, 'w') as f: f.write('1')
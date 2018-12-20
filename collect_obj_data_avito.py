import re
import sqlite3
import lxml.html as html
import requests
import time
import os

import collect_proxies

path_data = os.path.join(os.getcwd(), "data")

if not os.path.exists(path_data): os.makedirs(path_data)

proxies = collect_proxies.Proxies()

#TODO collect info about publicator (fio, name of organization)
#TODO collect info about type (category) of realrty (by link)
#TODO 

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

        fields = {}

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

        #TODO this date into YYYY-MM-DD HH:MM:SS

        date_publication = page.cssselect('.item-view-header .title-info-metadata-item')
        if date_publication:
            date_publication = date_publication[0]
            date_publication = date_publication.text_content().split(',')[1]
            date_publication = date_publication.strip().split()[1:]

            time_publication = date_publication.pop()

            if date_publication[0] == 'сегодня':
                pass
            elif date_publication[0] == 'вчера':
                pass
            else:
                day_publication = date_publication[0]
                month_publication = date_publication[1]
            
        # other

        items = page.cssselect('.item-view-block .item-params-list-item')

        for item in items:

            name, value = item.text_content().strip().split(':', 1)
            name = name.strip()
            value = value.strip()
            
            print('    ', name, ':' ,value)

            if name == 'Общая площадь':
                fields['realty_m2_building'] = int(float(value.split()[0])*10)
            elif name == 'Площадь кухни':
                fields['realty_m2_kitchen'] = int(float(value.split()[0])*10)
            elif name == 'Жилая площадь':
                fields['realty_m2_living'] = int(float(value.split()[0])*10)
            elif name == 'Количество комнат':
                if value == 'студии':
                    fields['realty_count_rooms'] = 0
                else:
                    fields['realty_count_rooms'] = int(value.split('-')[0])
            elif name == 'Тип дома':
                fields['realty_type_building'] = value
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
        
        # updating...
        
        keys = []
        values = []
        
        for key, value in fields.items():
            keys.append('`'+key+'`=?')
            values.append(value)

        values.append(obj['realty_id'])

        sql = "UPDATE `realty` SET " + ','.join(keys) + 'WHERE `realty_id`=?'
        res = cu.execute(sql, tuple(values))
        c.commit()

        with open(path_cur_obj_id, 'w') as f: f.write(str(obj['realty_id']))

        #print(fields)

        time.sleep(6)

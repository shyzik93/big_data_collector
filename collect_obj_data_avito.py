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


if __name__ == '__main__':
    c = sqlite3.connect(os.path.join(path_data, 'data_avito.db'))
    c.row_factory = sqlite3.Row
    cu = c.cursor()

    domain_url = "https://avito.ru"
    
    start_obj_id = 1

    sql = "SELECT `realty_price`, `realty_id`, `realty_url`, `realty_ext_id` FROM `realty` WHERE `realty_id`>=?"
    r = cu.execute(sql, (start_obj_id, )).fetchall()
    for obj in r:
        print(domain_url + obj['realty_url'])
        r = requests.get(domain_url + obj['realty_url'])
        page = html.document_fromstring(r.content)

        fields = {}

        # price

        price = page.cssselect('.item-view-header span[itemprop=price]')[0]
        fields['realty_price'] = int(price.get('content'))

        # publication date

        date_publication = page.cssselect('.item-view-header .title-info-metadata-item')[0]
        date_publication = date_publication.text_content().split(',')[1]
        print(date_publication)
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
            
            print(name, value)
            if name == 'Общая площадь':
                fields['realty_m2_building'] = int(float(value.split()[0])*10)
            elif name == 'Площадь кухни':
                fields['realty_m2_kitchen'] = int(float(value.split()[0])*10)
            elif name == 'Количество комнат':
                fields['realty_count_rooms'] = int(value.split('-')[0])
            elif name == 'Тип дома':
                fields['realty_type_building'] = value
            elif name == 'Этажей в доме':
                fields['realty_floor_total'] = int(value)
            elif name == 'Этаж':
                fields['realty_floor'] = int(value)

         # address

        address = page.cssselect('.item-view-map .item-map-location')[0]
        address.remove(address.cssselect('.item-map-control')[0])
        _address = []
        for child in address.getchildren():
            _address.append(child.text_content().strip())
        fields['realty_address'] = ', '.join(_address[1:])
        

        print(fields)

        exit()

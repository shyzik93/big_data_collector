import re
import sqlite3
import lxml.html as html
import requests
import time
import os

path_data = os.path.join(os.getcwd(), "data")

if not os.path.exists(path_data): os.makedirs(path_data)


if __name__ == '__main__':
    c = sqlite3.connect(os.path.join(path_data, 'data_avito.db'))
    c.row_factory = sqlite3.Row
    cu = c.cursor()

    domain_url = "https://avito.ru"
    
    m2 = 50
    count_rooms = 2
    category_obj = 'flat'
    deal_type = 'sell'
    user_type = 'Частное лицо'

    e = 8
    max_m2 = m2 + e
    min_m2 = m2 - e
    
    deal_types = {
        'buy': 1, 'sell': 2, 'give_rent':3, 'get_rent': 4
    }

    _square="`realty_m2_building` < ? AND `realty_m2_building` > ? "
    _rooms=" `realty_count_rooms` = ? "
    _cat = " `realty_category` = ? "
    _deal_type = " `realty_deal_type_id` = ? "

    _user_type = """ `realty`.`realty_user_id` = `user`.`user_id` AND 
                     `user`.`user_type_id` = `user_type`.`user_type_id` AND 
                     `user_type`.`user_type_name`=? """

    select = "SELECT * FROM `realty`, `user`, `user_type` WHERE "#`realty_price_arenda_type` is NULL AND "

    sql = select + _square +" AND "+ _rooms +" AND "+ _cat +" AND "+ _deal_type +" AND "+ _user_type
    sql += " ORDER BY `realty_price`"
    res = cu.execute(sql, (max_m2*10, min_m2*10, count_rooms, category_obj, deal_types[deal_type], user_type))
    
    average_price = 0;
    total_price = 0;
    count_objects = 0
    
    with open(os.path.join(path_data, 'A_for_obj.html'), 'w') as f:

        f.write('''<style>
        td {padding:2px 5px;}
        .block_target {padding-left: 20px;}
        </style>''')

        f.write("Анализ для следующей недвижимости:")
        f.write("<div class='block_target'>\n")
        f.write("Категория: "+str(category_obj)+"<br>\n")
        f.write("Суммарная площадь: "+str(m2)+" м2<br>\n")
        f.write("Кол-во комнат: "+str(count_rooms)+"<br>\n")
        f.write("</div>\n<br><br>\n")
        
        f.write("<table>")

        f.write("<th>Стоимость</th>\n")
        f.write("<th>Площадь</th>\n")
        f.write("<th>Комнат</th>\n")
        f.write("<th>Ссылка</th>\n")
        f.write("<th>Разместил</th>\n")

        for row in res:
            f.write("<tr>")

            f.write("<td>"+str(row['realty_price'])+" руб.</td>\n")
            f.write("<td>"+str(row['realty_m2_building']/10)+" м2 </td>\n")
            f.write("<td>"+str(row['realty_count_rooms'])+"</td\n>")

            f.write("<td><a target='_blank' href='"+domain_url+row['realty_url']+"'>")
            f.write("Посмотреть на Avito")
            f.write("</a></td>\n")

            if row['user_url']:
                f.write("<td><a target='_blank' href='"+domain_url+row['user_url']+"'>")
                f.write(row['user_name'])
                f.write("</a> ("+row['user_type_name']+")</td>\n")
            else:
                f.write("<td>")
                f.write(row['user_name'])
                f.write(" ("+row['user_type_name']+")</td>\n")

            f.write("</tr>")

            total_price += row['realty_price']
            
            count_objects += 1

        f.write("</table>")
        f.write("<br><br>")
        
        average_price = total_price / count_objects

        f.write("Всего объектов: "+str(count_objects)+"<br>")
        f.write("Средняя цена: "+str(average_price)+"<br>")
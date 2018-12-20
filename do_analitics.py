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

    e = 10
    max_m2 = m2 + e
    min_m2 = m2 - e

    square="`realty_m2_building` < ? AND `realty_m2_building` > ? "
    rooms=" `realty_count_rooms` = ? "

    select = "SELECT * FROM `realty` WHERE `realty_price_arenda_type` is NULL "

    sql = select +" AND "+ square +" AND "+ rooms
    res = cu.execute(sql, (max_m2*10, min_m2*10, count_rooms))
    
    average_price = 0;
    total_price = 0;
    count_objects = 0
    
    with open(os.path.join(path_data, 'A_for_obj.html'), 'w') as f:

        f.write("Анализ для следующей недвижимости:")
        f.write("<div>\n")
        f.write("Площадь здания: "+str(m2)+"м2<br>\n")
        f.write("Кол-во комнат: "+str(count_rooms)+"м2<br>\n")
        f.write("</div>\n<br><br>\n")

        for row in res:
            f.write("<a target='_blank' href='"+domain_url+row['realty_url']+"'>")
            f.write(str(row['realty_price'])+" руб. ")
            f.write(str(row['realty_m2_building']/10)+"м2 ")
            f.write(str(row['realty_count_rooms'])+"-комнатная")
            f.write("</a><br>\n")

            total_price += row['realty_price']
            
            count_objects += 1

        f.write("<br><br>")
        
        average_price = total_price / count_objects

        f.write("Всего объектов: "+str(count_objects)+"<br>")
        f.write("Средняя цена: "+str(average_price)+"<br>")
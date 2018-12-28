sqlite3 data/data_avito.db '.dump' > data/dump.sql

#select="SELECT \"<a target='_blank' href='https://avito.ru\" || \`realty_url\` || \"'>\" || \`realty_price\` || \" руб. \" || \`realty_count_rooms\` || \"</a><br>\" FROM \`realty\` WHERE \`realty_price_arenda_type\` is NULL AND "

#sqlite3 data/data_avito.db "${select} \`realty_price\`<=1500000" > data/A1.html
#sqlite3 data/data_avito.db "${select} \`realty_price\`>1500000 AND \`realty_price\`<=2000000" > data/A2.html
#sqlite3 data/data_avito.db "${select} \`realty_price\`>3000000 AND \`realty_price\`<=5000000" > data/A3.html
#sqlite3 data/data_avito.db "${select} \`realty_price\`>5000000" > data/A4.html

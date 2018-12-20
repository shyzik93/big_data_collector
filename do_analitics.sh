# for delete

e=10
max_m2=$(($1+$e))
min_m2=$(($1-$e))

square="\`realty_m2_building\` < ${max_m2}*10 AND \`realty_m2_building\` > ${min_m2}*10 "

select="SELECT \"<a target='_blank' href='https://avito.ru\" || \`realty_url\` || \"'>\" || \`realty_price\` || \" руб. \" || \`realty_count_rooms\` || \"</a><br>\" FROM \`realty\` WHERE \`realty_price_arenda_type\` is NULL AND "

echo "${select} ${square}"

sqlite3 data/data_avito.db "${select} ${square}" > data/A_for_obj.html
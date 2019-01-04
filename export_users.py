import config_site_avito as cs
import csv
import os

if __name__ == "__main__":

    output_path = os.path.join(cs.path_data, 'for_amo_crm.csv')
    cur_date = 'date'

    c, cu = cs.get_db()

    f = open(output_path, 'w')
    csvw = csv.writer(f)

    sql = "SELECT * FROM user, user_contact WHERE user.user_id=user_contact.user_contact_user_id"
    rows = c.execute(sql).fetchall()
    for row in rows:
        csvw.writerow([
            row['user_name'],
            row['user_contact_data'],
            'Polyakov Konstantin',
            cur_date,
            row['user_name'],
        ])

    f.close()

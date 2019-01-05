import config_site_avito as cs
import csv
import os
import datetime

if __name__ == "__main__":

    output_path = os.path.join(cs.path_data, 'for_amo_crm.csv')
    cur_date = 'date'

    c, cu = cs.get_db()

    f = open(output_path, 'w')
    csvw = csv.writer(f)

    csvw.writerow([
        'full name (contact)',
        'position (contact)',
        'responsible',
        'who create contact',
        'mobile phone',
        'when create contact',
        'url of the profile',
    ])

    when_create_contact = datetime.date.today().strftime('%d.%m.%Y')

    sql = "SELECT * FROM user, user_contact, user_type  WHERE user.user_id=user_contact.user_contact_user_id AND user.user_type_id=user_type.user_type_id LIMIT 10"
    rows = c.execute(sql).fetchall()
    for row in rows:

        user_position = ''
        responsible = ''
        who_create_contact = 'Polyakov Konstantin'

        csvw.writerow([
            row['user_name'],
            user_position,
            responsible,
            who_create_contact,
            row['user_contact_data'],
            when_create_contact,
            row['user_url'],
        ])

    f.close()

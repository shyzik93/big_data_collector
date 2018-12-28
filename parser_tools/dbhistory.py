"""
Author: Polyakov Konstantin
Date: 2018-12-26
Place: Yeysk, Russia
"""

class DBHistory():

    def __init__(self, c, cu):
        self.cu = cu
        self.c = c

    def save(self, realty_id, table_name, value_name, new_value):
        sql = "SELECT * FROM `"+table_name+"` WHERE `history_realty_id`=? ORDER BY `history_date` DESC LIMIT 1"
        res2 = self.cu.execute(sql, (realty_id,)).fetchall()
        if res2: res2 = res2[0]
        if not res2 or res2[value_name] != new_value:
            sql = "INSERT INTO `"+table_name+"` (`history_realty_id`, `"+value_name+"`) VALUES (?, ?); "
            self.cu.execute(sql, (realty_id, new_value))

    def insert_and_commit(self):
        self.c.commit()

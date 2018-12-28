#!/usr/bin/env python3

"""
Author: Polyakov Konstantin
Date: 2018-12-23
Place: Yeysk, Russia
"""

import os

class CurIndex():
	
    def __init__(self, path_cur_index):
        self.path_cur_id = path_cur_index

    def get(self):
        cur_obj_id = 1
        if os.path.exists(self.path_cur_id):
            with open(self.path_cur_id) as f:
                _cur_obj_id = f.read().strip()
                # if file is empty
                if _cur_obj_id: cur_obj_id = int(_cur_obj_id)
        return cur_obj_id

    def save(self, index):
        with open(self.path_cur_id, 'w') as f: f.write(str(index))
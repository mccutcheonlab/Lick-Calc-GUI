# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 13:43:06 2019

@author: jmc010
"""

import csv

filename='C:\\Github\\Lick-Calc-GUI\\output\\ch1.txt'

with open(filename, newline='') as myFile:
    reader = csv.DictReader(myFile)
    cols = reader.fieldnames
    loaded_vars = {}
    for col in cols:
        loaded_vars[col] = []
        myFile.seek(0)
        for idx, row in enumerate(reader):
            if idx < 5:
                pass
            else:
                try:
                    loaded_vars[col].append(float(row[col]))
                except:
                    pass 

import datetime
import numpy as np

headerrows=5
f = open(filename, 'r')
lines = f.readlines()[headerrows:]
f.close()

lines_dt = [datetime.datetime.strptime(line, '%H:%M:%S.%f\n') for line in lines]


delta = [d-lines_dt[idx-1] for idx, d in enumerate(lines_dt[1:])]
delta_array = np.array([d.total_seconds() for d in delta])

dayadvance = np.where(delta_array < 0)[0][0]

#lines_dt = [d + datetime.timedelta(days=1) for d in lines_dt]


lines_dt2 = lines_dt[:dayadvance] + [d + datetime.timedelta(days=1) for d in lines_dt[dayadvance:]]

t0=lines_dt2[0]

lines_dt3 = [(d - t0).total_seconds() for d in lines_dt2]

data = lickCalc(lines_dt3)

#delta.min()


#
#dt_obj = datetime.datetime.strptime(time_str, '%H:%M:%S.%f\n')
#dt_obj2 = datetime.datetime.strptime(time_str_end, '%H:%M:%S.%f\n')
#
#print(lines_dt[0])
#print(lines_dt[0] + datetime.timedelta(days=1))

#print(dt_obj2-dt_obj)




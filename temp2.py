# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 11:47:43 2018

@author: James Rig
"""




def checknsessions(filename):
    f = open(filename, 'r')
    f.seek(0)
    filerows = f.readlines()[8:]
    datarows = [isnumeric(x) for x in filerows]
    matches = [i for i,x in enumerate(datarows) if x == 0.3]
    return matches

def isnumeric(s):
    try:
        x = float(s)
        return x
    except ValueError:
        return float('nan')

filename = 'C:\\Users\\James Rig\\Downloads\\!2018-07-25_09h32m.Subject QPP2.01'

matches = checknsessions(filename)
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 16:32:58 2018

@author: jaimeHP
"""
import csv


fff = 'hey ho'
ttt = str(203)
bbb = 543

d = [('Filename', fff),('Total licks', ttt),
     ('Burst number', bbb)]


with open('C:\\Users\\jaimeHP\\Dropbox\\Python\\cas9\\cas9_medfiles\\testfile.csv', 'w', newline='') as file:
    csv_out = csv.writer(file)
    csv_out.writerow(['Parameter', 'Value'])
    for row in d:
        csv_out.writerow(row)

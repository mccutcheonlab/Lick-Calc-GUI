# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 16:32:58 2018

@author: jaimeHP
"""
import collections
import numpy as np
import string

import os

files = os.listdir('C:\\Users\\jaimeHP\\Dropbox\\Python\\cas9\\cas9_medfiles\\')

n = [x[0] for x in enumerate(files) if x[1] == '!2016-08-31_09h16m.Subject 4']

print(n)
print(n[0])
print(files[n[0]+1])

#str = "<>I'm Tom."
#temp = str.split("I",1)
#temp[0]=temp[0].replace("<>","")
#str = "I".join(temp)
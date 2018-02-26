# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 16:32:58 2018

@author: jaimeHP
"""
import collections
import numpy as np
import string

d = {'a':[1,2,3], 'c':[6,7,8]}

options = [x+': '+str(len(d[x])) for x in d]

print(options)
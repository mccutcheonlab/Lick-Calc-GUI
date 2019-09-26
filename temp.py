# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 13:43:06 2019

@author: jmc010
"""
import string
import numpy as np
import matplotlib.pyplot as plt

import scipy.stats as stats
import weibull
    


def medfilereader_licks(filename,
                  sessionToExtract = 1,
                  verbose = False,
                  remove_var_header = True):
    
    f = open(filename, 'r')
    f.seek(0)
    filerows = f.readlines()[8:]
    datarows = [isnumeric(x) for x in filerows]
    matches = [i for i,x in enumerate(datarows) if x == 0.3]
    if sessionToExtract > len(matches):
        print('Session ' + str(sessionToExtract) + ' does not exist.')
    if verbose == True:
        print('There are ' + str(len(matches)) + ' sessions in ' + filename)
        print('Analyzing session ' + str(sessionToExtract))
    
    varstart = matches[sessionToExtract - 1]    
    medvars = {}
   
    k = int(varstart + 27)
    for i in range(26):
        medvarsN = int(datarows[varstart + i + 1])
        if medvarsN > 1:
            medvars[string.ascii_uppercase[i]] = datarows[k:k + int(medvarsN)]
        k = k + medvarsN
    
    if remove_var_header == True:
        for val in medvars.values():
            val.pop(0)

    return medvars

def isnumeric(s):
    try:
        x = float(s)
        return x
    except ValueError:
        return float('nan')

"""
This function will calculate data for bursts from a train of licks. The threshold
for bursts and clusters can be set. It returns all data as a dictionary.
"""
def lickCalc(licks, offset = [], burstThreshold = 0.25, runThreshold = 10,
             ignorelongilis=True, minburstlength=1,
             binsize=60, histDensity = False):
    # makes dictionary of data relating to licks and bursts
    if type(licks) != np.ndarray or type(offset) != np.ndarray:
        try:
            licks = np.array(licks)
            offset = np.array(offset)
        except:
            print('Licks and offsets need to be arrays and unable to easily convert.')
            return

    lickData = {}
    
    if len(offset) > 0:
        lickData['licklength'] = offset - licks
        lickData['longlicks'] = [x for x in lickData['licklength'] if x > 0.3]
    else:
        lickData['licklength'] = []
        lickData['longlicks'] = []

    lickData['licks'] = np.concatenate([[0], licks])
    lickData['ilis'] = np.diff(lickData['licks'])
    if ignorelongilis:
        lickData['ilis'] = [x for x in lickData['ilis'] if x < burstThreshold]

    lickData['freq'] = 1/np.mean([x for x in lickData['ilis'] if x < burstThreshold])
    lickData['total'] = len(licks)
    
    # Calculates start, end, number of licks and time for each BURST 
    lickData['bStart'] = [val for i, val in enumerate(lickData['licks']) if (val - lickData['licks'][i-1] > burstThreshold)]  
    lickData['bInd'] = [i for i, val in enumerate(lickData['licks']) if (val - lickData['licks'][i-1] > burstThreshold)]
    lickData['bEnd'] = [lickData['licks'][i-1] for i in lickData['bInd'][1:]]
    lickData['bEnd'].append(lickData['licks'][-1])

    lickData['bLicks'] = np.diff(lickData['bInd'] + [len(lickData['licks'])])
    
    # calculates which bursts are above the minimum threshold
    inds = [i for i, val in enumerate(lickData['bLicks']) if val>minburstlength-1]
    
    lickData['bLicks'] = removeshortbursts(lickData['bLicks'], inds)
    lickData['bStart'] = removeshortbursts(lickData['bStart'], inds)
    lickData['bEnd'] = removeshortbursts(lickData['bEnd'], inds)
      
    lickData['bTime'] = np.subtract(lickData['bEnd'], lickData['bStart'])
    lickData['bNum'] = len(lickData['bStart'])
    if lickData['bNum'] > 0:
        lickData['bMean'] = np.nanmean(lickData['bLicks'])
        lickData['bMean-first3'] = np.nanmean(lickData['bLicks'][:3])
    else:
        lickData['bMean'] = 0
        lickData['bMean-first3'] = 0
    
    lickData['bILIs'] = [x for x in lickData['ilis'] if x > burstThreshold]

    # Calculates start, end, number of licks and time for each RUN
    lickData['rStart'] = [val for i, val in enumerate(lickData['licks']) if (val - lickData['licks'][i-1] > runThreshold)]  
    lickData['rInd'] = [i for i, val in enumerate(lickData['licks']) if (val - lickData['licks'][i-1] > runThreshold)]
    lickData['rEnd'] = [lickData['licks'][i-1] for i in lickData['rInd'][1:]]
    lickData['rEnd'].append(lickData['licks'][-1])

    lickData['rLicks'] = np.diff(lickData['rInd'] + [len(lickData['licks'])])    
    lickData['rTime'] = np.subtract(lickData['rEnd'], lickData['rStart'])
    lickData['rNum'] = len(lickData['rStart'])

    lickData['rILIs'] = [x for x in lickData['ilis'] if x > runThreshold]
    try:
        lickData['hist'] = np.histogram(lickData['licks'][1:], 
                                    range=(0, 3600), bins=int((3600/binsize)),
                                          density=histDensity)[0]
    except TypeError:
        print('Problem making histograms of lick data')
        
    return lickData

def removeshortbursts(data, inds):
    data = [data[i] for i in inds]
    return data

def burstprobFig(ax, data):
    
    figlabel = '{:d} total bursts\n{:.2f} licks/burst'.format(
            data['bNum'], data['bMean'])
    
    x, y = calculate_burst_prob(data['bLicks'])
    ax.scatter(x,y,color='none', edgecolors='grey')

    ax.set_xlabel('Burst size (n)')
    ax.set_ylabel('Probability of burst>n')
    ax.text(0.9, 0.8, figlabel, ha='right', va='center', transform = ax.transAxes)
    
    return x, y

def calculate_burst_prob(bursts):
    bins = np.arange(min(bursts), max(bursts))
    hist=np.histogram(bursts, bins=bins, density=True)
    cumsum=np.cumsum(hist[0])

    x = hist[1][1:]
    y = [1-val for val in cumsum]
    
    return x, y

def wb2LL(p, x): #log-likelihood
    return sum(np.log(stats.weibull_min.pdf(x, p[1], 0., p[0])))

def weib(x,n,a):
    return (a / n) * (x / n)**(a - 1) * np.exp(-(x / n)**a)



currdir = 'C:\\Github\\Lick-Calc-GUI\\data\\'
filename = currdir+'!2017-07-28_08h14m.Subject pcf1.02'

#!2017-07-28_10h00m.Subject pcf1.12
#!2017-07-28_10h14m.Subject pcf1.09
#!2017-07-28_09h29m.Subject pcf1.03

arrays = medfilereader_licks(filename)

try:
    lickdata = lickCalc(arrays['B'], minburstlength=3)
except KeyError:
    lickdata = lickCalc(arrays['E'], minburstlength=3)
    
bursts = lickdata['bLicks']
x, bursts_cumsum = calculate_burst_prob(bursts)


import scipy.optimize as opt

def weib_davis(x, alpha, beta): 
    return (np.exp(-(alpha*x)**beta))

def fit_weibull(lickdata):
    xdata, ydata = calculate_burst_prob(lickdata['bLicks'])
    x0=np.array([0.1, 1])
    fit=opt.curve_fit(weib_davis, xdata, ydata, x0)
    alpha=fit[0][0]
    beta=fit[0][1]
    slope, intercept, r_value, p_value, std_err = stats.linregress(ydata, weib_davis(xdata, alpha, beta))
    r_squared=r_value**2


result = (stats.exponweib.fit(bursts, floc=0, f0=1))
result2 = (stats.exponweib.fit(bursts_cumsum, floc=0, f0=1))


f, ax = plt.subplots(figsize=(6,4), ncols=2)
burstprobFig(ax[0], lickdata)
ax[0].plot(x, weib(x,result[3], result[1]), c='g')
ax[0].plot(x, weib(x,result2[3], result2[1]), c='r')

burstprobFig(ax[1], lickdata)
ax[1].plot(x, weib_davis(x,result[3], result[1]), c='g')
ax[1].plot(x, weib_davis(x,result2[3], result2[1]), c='r')

alpha=0.1
beta=0.90






#
#LL = wb2LL(np.asarray(result), [x, y])

analysis = weibull.Analysis(bursts_cumsum, unit='hour')
analysis.fit(method='mle')

print(analysis.beta, analysis.eta)

ax[1].plot(x, weib_davis(x,alpha, beta), c='b')
#ax[1].plot(x, weib_davis(x,analysis.eta, analysis.beta), c='orange')


# trying to optimize myself

xdata=x
ydata=np.array(bursts_cumsum)

x0=np.array([0.1, 1])

#sigma=np.array([1.0, 1.0, 1.0, 1.0])



result3=opt.curve_fit(weib_davis, xdata, ydata, x0)

print(result3[0])

ax[1].plot(x, weib_davis(x,result3[0][0], result3[0][1]), c='orange')

fitted = weib_davis(x,result3[0][0], result3[0][1])


slope, intercept, r_value, p_value, std_err = stats.linregress(ydata, fitted)

print(r_value**2)


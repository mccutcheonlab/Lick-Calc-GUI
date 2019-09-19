# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 14:33:59 2019

@author: admin
"""

def get_location():
    loc = filedialog.askdirectory(initialdir=currdir, title='Select a save folder.')
    return loc

def sessionlicksFig(ax, licks):
    ax.hist(licks, range(0,3600,60), color='grey', alpha=0.4)
    yraster = [ax.get_ylim()[1]] * len(licks)
    ax.scatter(licks, yraster, s=50, facecolors='none', edgecolors='grey')

    ax.set_xticks(np.multiply([0, 10, 20, 30, 40, 50, 60],60))
    ax.set_xticklabels(['0', '10', '20', '30', '40', '50', '60'])
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Licks per min')

def alert(msg):
    print(msg)
    messagebox.showinfo('Error', msg)

def checknsessions(filename):
    f = open(filename, 'r')
    f.seek(0)
    filerows = f.readlines()[8:]
    datarows = [isnumeric(x) for x in filerows]
    matches = [i for i,x in enumerate(datarows) if x == 0.3]
    return matches

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

def licklengthFig(ax, data, contents = '', color='grey'):          
    if len(data['longlicks']) > 0:
        longlicklabel = str(len(data['longlicks'])) + ' long licks,\n' +'max = ' + '%.2f' % max(data['longlicks']) + ' s.'        
    else:
        longlicklabel = 'No long licks.'
    
    figlabel = str(len(data['licklength'])) + ' total licks.\n' + longlicklabel

    ax.hist(data['licklength'], np.arange(0, 0.3, 0.01), color=color)
    ax.text(0.9, 0.9, figlabel, ha='right', va='top', transform = ax.transAxes)
    ax.set_xlabel('Lick length (s)')
    ax.set_ylabel('Frequency')
    ax.set_title(contents)
    
def iliFig(ax, data, contents = '', color='grey'):
    ax.hist(data['ilis'], np.arange(0, 0.5, 0.02), color=color)
    figlabel = '%.2f Hz' % data['freq']
    ax.text(0.9, 0.9, figlabel, ha='right', va='top', transform = ax.transAxes)
    
    ax.set_xlabel('Interlick interval (s)')
    ax.set_ylabel('Frequency')
    ax.set_title(contents)
    
def burstlengthFig(ax, data, contents='', color3rdbar=False):
    
    figlabel = '{:d} total bursts\n{:.2f} licks/burst'.format(
            data['bNum'], data['bMean'])
                                                
    n, bins, patches = ax.hist(data['bLicks'], range(0, 20), normed=1)
    ax.set_xticks(range(1,20))
    ax.set_xlabel('Licks per burst')
    ax.set_ylabel('Frequency')
    ax.set_xticks([1,2,3,4,5,10,15])
    ax.text(0.9, 0.8, figlabel, ha='right', va='center', transform = ax.transAxes)
    
def burstprobFig(ax, data):
    
    figlabel = '{:d} total bursts\n{:.2f} licks/burst'.format(
            data['bNum'], data['bMean'])
    
    x, y = calculate_burst_prob(data['bLicks'])
    ax.scatter(x,y,color='none', edgecolors='grey')

    ax.set_xlabel('Burst size (n)')
    ax.set_ylabel('Probability of burst>n')
    ax.text(0.9, 0.8, figlabel, ha='right', va='center', transform = ax.transAxes)

def calculate_burst_prob(bursts):
    bins = np.arange(min(bursts), max(bursts))
    hist=np.histogram(bursts, bins=bins, density=True)
    cumsum=np.cumsum(hist[0])

    x = hist[1][1:]
    y = [1-val for val in cumsum]
    
    return x, y
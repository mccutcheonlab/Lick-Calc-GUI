"""
Created by J McCutcheon
22 Feb 2018
To analyze data from Med PC files and calculate/output lick parameters.
"""

# Import statements
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os
import string
import numpy as np
import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

#mpl.rcParams['figure.subplot.wspace'] = 0.3
#mpl.rcParams['figure.subplot.left'] = 0.1
#mpl.rcParams['figure.subplot.bottom'] = 0.25


# Main class for GUI
class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)               
        self.master = master
        self.init_window()
        
    def init_window(self):
        self.master.title('MedfileReader')
        self.pack(fill=BOTH, expand=1)
        
        openfileButton = Button(self, text='Load Med PC File', command=self.loadmedfile)
        openfileButton.grid(row=0, column=0)
        
        analyzeButton = Button(self, text='Analyze Data', command=self.analyze)
        analyzeButton.grid(row=1)
        
        self.IBthreshold = StringVar(self.master)
        thresholdField = Entry(self, textvariable=self.IBthreshold)
        thresholdField.insert(END,'0.5')
        thresholdField.grid(row=3, column=3)
        
        self.IRthreshold = StringVar(self.master)
        runthresholdField = Entry(self, textvariable=self.IRthreshold)
        runthresholdField.insert(END,'10')
        runthresholdField.grid(row=4, column=3)
         
        Label(self, text='onset').grid(row=3)
        Label(self, text='offset').grid(row=4)
        
        self.f_init = plt.figure(figsize=(1,5))
        canvas = FigureCanvasTkAgg(self.f_init, self)
        canvas.show()
        canvas.get_tk_widget().grid(row=5, column=0, columnspan=5, sticky='ew', padx=10)

        Label(self, text='LickCalc-1.0 by J McCutcheon').grid(row=7)
        
        
        
        #Lines for testing
        self.loadmedfile()

    def loadmedfile(self):
#        self.filename = filedialog.askopenfilename(initialdir=currdir, title='Select a Med PC file.')
        # Line for testing
        self.filename = 'C:\\Users\\jaimeHP\\Dropbox\\Python\\cas9\\cas9_medfiles\\!2016-07-19_09h16m.Subject 4'
        self.filename = 'C:\\Users\\jaimeHP\\Dropbox\\Python\\cas9\\cas9_medfiles\\!2017-06-12_10h53m.Subject thpe1.4'
        try:
            self.meddata = medfilereader(self.filename)
        except:
            alert("Error", "Problem reading file and extracting data. File may not be properly formatted - see Help for advice.")
            return
        
        self.medvars = [x for x in self.meddata if len(x)>1]
              
        try:
            self.setOptionMenu()
            self.showfilename()
        except TypeError:
            alert("No valid variables to analyze (e.g. arrays with more than one value")

    def showfilename(self):
        text = Label(self, text=self.filename)
        text.grid(row=0, column=2)

    def setOptionMenu(self):
        varlens = [len(x) for x in self.medvars]
        OPTIONS = [x+': '+str(y) for (x, y) in zip(list(string.ascii_uppercase), varlens)]

        self.onset = StringVar(self.master)
        onsetBtn = OptionMenu(self, self.onset, *OPTIONS).grid(row=3, column=1)
    
        self.offset = StringVar(self.master)
        offsetBtn = OptionMenu(self, self.offset, *OPTIONS).grid(row=4, column=1)
    
    def analyze(self):
        print('Analyzing...')
        
        # Check inputs
        try:
            burstTH = float(self.IBthreshold.get())
        except ValueError:
            alert('Interburst threshold value needs to be numeric')
            return
        
        try:
            runTH = float(self.IRthreshold.get())
        except ValueError:
            alert('Interrun threshold value needs to be numeric')
            return        
               
        if hasattr(self, 'filename'):            
            try:
                self.onsetArray = self.medvars[ord(self.onset.get()[0])-65]
                try:
                    self.offsetArray = self.medvars[ord(self.offset.get()[0])-65]
                    self.lickdata = lickCalc(self.onsetArray, offset=self.offsetArray, burstThreshold = burstTH, runThreshold = runTH)
                except:
                    self.lickdata = lickCalc(self.onsetArray, burstThreshold = burstTH, runThreshold = runTH)

            except:
                print("Error:", sys.exc_info()[0])               
                raise
        
        else:
            print('Select a file first')
            messagebox.showinfo("Error", "Select a valid file first.")
        
        self.makegraphs()
                        
    def makegraphs(self):
        
        self.f = plt.figure(figsize=(1,5))

        # Licks over session     
#        f1, ax = plt.subplots(figsize=(1,2.5))
        grid = plt.GridSpec(2, 3, wspace=0.5, hspace=0.5)
        self.ax1 = self.f.add_subplot(grid[0,:])
        self.ax2 = self.f.add_subplot(grid[1,0])
        self.ax3 = self.f.add_subplot(grid[1,1])
        self.ax4 = self.f.add_subplot(grid[1,2])
        
        sessionlicksFig(self.ax1, self.onsetArray)
        
        canvas = FigureCanvasTkAgg(self.f, self)
        canvas.show()
        canvas.get_tk_widget().grid(row=5, column=0, columnspan=5, sticky='ew', padx=10)
       
#        # Burst parameter figures
#        f2, (ax1, ax2, ax3) = plt.subplots(1,3,figsize=(1,2.5))
#        
#        iliFig(ax1, self.lickdata)    
#        burstlengthFig(ax2, self.lickdata)        
#        licklengthFig(ax3, self.lickdata)
#        
#        canvas = FigureCanvasTkAgg(f2, self)
#        canvas.show()
#        canvas.get_tk_widget().grid(row=6, column=0, columnspan=5, sticky='ew', padx=10)
#       
def sessionlicksFig(ax, licks):
    ax.hist(licks, range(0,3600,60), color='grey', alpha=0.4)
#    lim = max(np.histogram(licks, range(0,3600,60))[0])
    yraster = [ax.get_ylim()[1]] * len(licks)
#    yraster = [lim*1.05] * len(licks)
    ax.scatter(licks, yraster, s=50, facecolors='none', edgecolors='grey')

    ax.set_xticks(np.multiply([0, 10, 20, 30, 40, 50, 60],60))
    ax.set_xticklabels(['0', '10', '20', '30', '40', '50', '60'])
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Licks per min')

def alert(msg):
    print(msg)
    messagebox.showinfo('Error', msg)

def medfilereader(filename, varsToExtract = 'all',
                  sessionToExtract = 1,
                  verbose = False,
                  remove_var_header = False):
    if varsToExtract == 'all':
        numVarsToExtract = np.arange(0,26)
    else:
        numVarsToExtract = [ord(x)-97 for x in varsToExtract]
    
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
    medvars = [[] for n in range(26)]
    
    k = int(varstart + 27)
    for i in range(26):
        medvarsN = int(datarows[varstart + i + 1])
        
        medvars[i] = datarows[k:k + int(medvarsN)]
        k = k + medvarsN
        
    if remove_var_header == True:
        varsToReturn = [medvars[i][1:] for i in numVarsToExtract]
    else:
        varsToReturn = [medvars[i] for i in numVarsToExtract]

    if np.shape(varsToReturn)[0] == 1:
        varsToReturn = varsToReturn[0]
    return varsToReturn

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
    lickData['freq'] = 1/np.mean([x for x in lickData['ilis'] if x < burstThreshold])
    lickData['total'] = len(licks)
    
    # Calculates start, end, number of licks and time for each BURST 
    lickData['bStart'] = [val for i, val in enumerate(lickData['licks']) if (val - lickData['licks'][i-1] > burstThreshold)]  
    lickData['bInd'] = [i for i, val in enumerate(lickData['licks']) if (val - lickData['licks'][i-1] > burstThreshold)]
    lickData['bEnd'] = [lickData['licks'][i-1] for i in lickData['bInd'][1:]]
    lickData['bEnd'].append(lickData['licks'][-1])

    lickData['bLicks'] = np.diff(lickData['bInd'] + [len(lickData['licks'])])    
    lickData['bTime'] = np.subtract(lickData['bEnd'], lickData['bStart'])
    lickData['bNum'] = len(lickData['bStart'])
    if lickData['bNum'] > 0:
        lickData['bMean'] = np.nanmean(lickData['bLicks'])
    else:
        lickData['bMean'] = 0
    
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
    
    figlabel = (str(data['bNum']) + ' total bursts\n' +
                str('%.2f' % data['bMean']) + ' licks/burst.')
                                                
    n, bins, patches = ax.hist(data['bLicks'], range(0, 20), normed=1)
    ax.set_xticks(range(1,20))
    ax.set_xlabel('Licks per burst')
    ax.set_ylabel('Frequency')
    ax.set_xticks([1,2,3,4,5,10,15])
#        ax.text(0.9, 0.9, figlabel1, ha='right', va='center', transform = ax.transAxes)
    ax.text(0.9, 0.8, figlabel, ha='right', va='center', transform = ax.transAxes)
    
    if color3rdbar == True:
        patches[3].set_fc('r')
    
def ibiFig(ax, data, contents = ''):
    ax.hist(data['bILIs'], range(0, 20), normed=1)
    ax.set_xlabel('Interburst intervals')
    ax.set_ylabel('Frequency')

root = Tk()

root.geometry('780x600')
currdir = os.getcwd()
currdir = 'C:\\Users\\jaimeHP\\Dropbox\\Python\\cas9\\cas9_medfiles\\'

app = Window(root)
root.lift()
root.mainloop()





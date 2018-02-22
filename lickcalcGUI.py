"""
Created by J McCutcheon
22 Feb 2018
To analyze data from Med PC files and calculate/output lick parameters.
"""

import JM_general_functions as jmf
import JM_custom_figs as jmfig

# Import statements
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os
import string
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
#import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

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
        
        #Lines for testing
        self.loadmedfile()

    def loadmedfile(self):
#        self.filename = filedialog.askopenfilename(initialdir=currdir, title='Select a Med PC file.')
        # Line for testing
        self.filename = 'C:\\Users\\jaimeHP\\Dropbox\\Python\\cas9\\cas9_medfiles\\!2016-07-19_09h16m.Subject 4'
       
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
                self.lickdata = jmf.lickCalc(self.onsetArray, burstThreshold = burstTH, runThreshold = runTH)

            except:
                print("Error:", sys.exc_info()[0])               
                raise
        
        else:
            print('Select a file first')
            messagebox.showinfo("Error", "Select a valid file first.")
        
        self.makegraphs()
                        
    def makegraphs(self):

        f, (ax1, ax2, ax3) = plt.subplots(1,3)
        
        jmfig.iliFig(ax1, self.lickdata)
        
        jmfig.burstlengthFig(ax2, self.lickdata)
        
        jmfig.ibiFig(ax3, self.lickdata)
        
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().grid(row=5, column=0, columnspan=5)

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

root = Tk()

root.geometry('800x800')
currdir = os.getcwd()
currdir = 'C:\\Users\\jaimeHP\\Dropbox\\Python\\cas9\\cas9_medfiles\\'

app = Window(root)
root.lift()
root.mainloop()





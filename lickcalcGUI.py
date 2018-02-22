
# coding: utf-8

# In[1]:

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
#import tkinter as tk

# import JM_general_functions as jmf
# import JM_custom_figs as jmfig

import os
import string

import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec


# In[2]:

class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)               
        self.master = master
        self.init_window()
        
    def init_window(self):
        self.master.title('MedfileReader')
        self.pack(fill=BOTH, expand=1)
        
#         self.filename='None'
#         filelabel = Label(self, text=self.filename)
#         filelabel.pack(side=TOP)
        
        openfileButton = Button(self, text='Load Med PC File', command=self.loadmedfile)
        openfileButton.grid(row=0)
        
        analyzeButton = Button(self, text='Analyze Data', command=self.analyze)
        analyzeButton.grid(row=1)
        
#         Label(self, text='Bottle 1').grid(row=2, column=1)
#         Label(self, text='Bottle 2').grid(row=2, column=4)
 
        Label(self, text='onset').grid(row=3)
        Label(self, text='offset').grid(row=4)
       


# In[3]:

def loadmedfile(self):
    self.filename = filedialog.askopenfilename(initialdir=currdir, title='Select a Med PC file.')
    self.showfilename()
    
    try:
        self.meddata = medfilereader(self.filename)
    except:
        print('Problem reading file and extracting data. File may not be properly formatted - see Help for advice.')
        messagebox.showinfo("Error", "Problem reading file and extracting data. File may not be properly formatted - see Help for advice.")
        return
    
    self.medvars = [x for x in self.meddata if len(x)>1]
          
    try:
        self.setOptionMenu()
    except TypeError:
        print('No valid variables to analyze (e.g. arrays with more than one value)')
        messagebox.showinfo("Error", "No valid variables to analyze (e.g. arrays with more than one value")
    


# In[4]:

def showfilename(self):
    text = Label(self, text=self.filename)
    text.grid(row=0, column=2)
    


# In[5]:

def setOptionMenu(self):
    varlens = [len(x) for x in self.medvars]
    OPTIONS = [x+' - '+str(y) for (x, y) in zip(list(string.ascii_lowercase), varlens)]
   
    self.b1onset = StringVar(self.master)
    b1onsetBtn = OptionMenu(self, self.b1onset, *OPTIONS).grid(row=3, column=1)

    self.b1offset = StringVar(self.master)
    b1offsetBtn = OptionMenu(self, self.b1offset, *OPTIONS).grid(row=4, column=1)

    self.b2onset = StringVar(self.master)
    b2onsetBtn = OptionMenu(self, self.b2onset, *OPTIONS).grid(row=3, column=4)

    self.b2offset = StringVar(self.master)
    b2offsetBtn = OptionMenu(self, self.b2offset, *OPTIONS).grid(row=4, column=4)


# In[6]:

def analyze(self):
    print('Analyzing...')
    
    if hasattr(self, 'filename'):
        try:
            print(ord(self.b1onset.get()[0])-97)
            print(self.b2onset.get())
#                self.lickdata = jmf.lickCalc(self.meddata)
#                self.makegraphs()
        except:
            print("Error:", sys.exc_info()[0])
            raise 
    else:
        print('Select a file first')
        
def makegraphs(self):

    gs1 = gridspec.GridSpec(2, 2)
    gs1.update(left=0.10, right= 0.9, wspace=0.5, hspace = 0.7)

    f = Figure(figsize=(5,5), dpi=100)
    ax = f.subplot(gs1[1, 1])

#        jmfig.licklengthFig(ax, self.lickdata)
    
    canvas = FigureCanvasTkAgg(f, self)
    canvas.show()
    canvas.get_tk_widget().grid(row=3, column=1)

    toolbar = NavigationToolbar2TkAgg(canvas, self)
    toolbar.update()
    canvas._tkcanvas.grid(row=4, column=1)


# In[7]:

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


# In[8]:

def isnumeric(s):
    try:
        x = float(s)
        return x
    except ValueError:
        return float('nan')


# In[9]:

root = Tk()

root.geometry('800x800')
currdir = os.getcwd()
currdir = 'C:\\Users\\jaimeHP\\Dropbox\\Python\\cas9\\cas9_medfiles\\'


# In[10]:

app = Window(root)
root.mainloop()


# In[ ]:




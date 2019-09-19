# -*- coding: utf-8 -*-
"""
Created by J McCutcheon
22 Feb 2018
To analyze data from Med PC files or text/csv files and calculate/output lick parameters.
"""

# Import statements
from tkinter import *
from tkinter import ttk
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
from matplotlib.backends.backend_pdf import PdfPages
import ntpath#
import csv
import collections
import xlsxwriter as xl

import lickcalc_fx

# Main class for GUI
class Window(Frame):

    def __init__(self, master=None):
        f1 = ttk.Style()
        f1.configure('.', background='powder blue', padding=5)
        f1.configure('TButton', width=15, sticky=(E,W))
        f1.configure('TMenubutton', background='light cyan', padding=0)
        f1.configure('header.TLabel', font='Helvetica 12')
        f2 = ttk.Style()
        f2.configure('inner.TFrame', background='light cyan')
        
        ttk.Frame.__init__(self, master, style='TFrame', padding=(10, 10, 15, 15))               
        self.master = master
        
        self.init_window()

    def init_window(self):
        self.master.title('MedfileReader')
        self.pack(fill=BOTH, expand=1)
        
        #Frame for graphs
        self.f2 = ttk.Frame(self, style='inner.TFrame', borderwidth=5,
                            relief="sunken", width=200, height=300)

        #Set up standalone labels
        self.fileparamslbl = ttk.Label(self, text='File Parameters', style='header.TLabel')
        self.calcparamslbl = ttk.Label(self, text='Calculator Parameters', style='header.TLabel')
        self.graphparamslbl = ttk.Label(self, text='Graph Parameters', style='header.TLabel')
        
        self.onsetlbl = ttk.Label(self, text='Onset')
        self.offsetlbl = ttk.Label(self, text='Offset')
        self.IBthresholdlbl = ttk.Label(self, text='Interburst threshold')
        self.IRthresholdlbl = ttk.Label(self, text='Interrun threshold')
        
        self.nolongILIslbl = ttk.Label(self, text='Ignore Long ILIs')
        self.minburstlengthlbl = ttk.Label(self, text='Minimum burst')
        self.plotburstproblbl = ttk.Label(self, text='Plot burst prob.')
        
        self.outputlbl = ttk.Label(self, text='Output Parameters', style='header.TLabel')
        self.suffixlbl = ttk.Label(self, text='File suffix')
        self.aboutlbl = ttk.Label(self, text='LickCalc-1.2 by J McCutcheon')
  
        #Set up Entry variables
        self.shortfilename = StringVar(self.master)
        self.shortfilename.set('No file loaded')
        self.filenamelbl = ttk.Label(self, textvariable=self.shortfilename)
        
        self.IBthreshold = StringVar(self.master)
        self.IRthreshold = StringVar(self.master)
        self.minburst = StringVar(self.master)

        self.IBthresholdField = ttk.Entry(self, textvariable=self.IBthreshold)
        self.IBthresholdField.insert(END,'0.5')
        
        self.IRthresholdField = ttk.Entry(self, textvariable=self.IRthreshold)
        self.IRthresholdField.insert(END,'10')
        
        self.minburstField = ttk.Entry(self, textvariable=self.minburst)
        self.minburstField.insert(END, '1')
        
        self.suffix = StringVar(self.master)
        self.suffixField = ttk.Entry(self, textvariable=self.suffix)
        self.suffixField.insert(END,'')
        
        # Set up Dropdown buttons
        self.OPTIONS = ['None']
        self.onset = StringVar(self.master)
        self.onsetButton = ttk.OptionMenu(self, self.onset, *self.OPTIONS)    
        self.offset = StringVar(self.master)
        self.offsetButton = ttk.OptionMenu(self, self.offset, *self.OPTIONS)

        #Set up Boolean variables
        self.nolongILIs = BooleanVar(self.master)
        self.nolongILIs.set(False)
        self.nolongILIsButton = ttk.Checkbutton(self, variable=self.nolongILIs, onvalue=True)
        
        self.plotburstprob = BooleanVar(self.master)
        self.plotburstprob.set(False)
        self.plotburstprobButton = ttk.Checkbutton(self, variable=self.plotburstprob, onvalue=True)
        
        # Set up Buttons
        self.loadmedButton = ttk.Button(self, text='Load Med File', command=self.openmedfile)
        self.loadcsvButton = ttk.Button(self, text='Load CSV/txt File', command=self.opencsvfile)
        self.analyzeButton = ttk.Button(self, text='Analyze Data', command=self.analyze)
        self.prevButton = ttk.Button(self, text='Previous', command=lambda: self.load_adj_files(delta=-1))
        self.nextButton = ttk.Button(self, text='Next', command=lambda: self.load_adj_files(delta=1))
        
        self.defaultfolderButton = ttk.Button(self, text='Default Folder', command=self.setsavefolder)
        self.pdfButton = ttk.Button(self, text='PDF', command=self.makePDF)
        self.excelButton = ttk.Button(self, text='Excel', command=self.makeExcel)
        self.textsummaryButton = ttk.Button(self, text='Text Summary', command=self.maketextsummary)
        
        #Place items in grid
        self.fileparamslbl.grid(column=0, row=0, columnspan=2)
        self.calcparamslbl.grid(column=2, row=0, columnspan=2)
        self.graphparamslbl.grid(column=4, row=0, columnspan=2)
        
        self.loadmedButton.grid(column=0, row=1, sticky=(W,E))
        self.loadcsvButton.grid(column=1, row=1, sticky=(W,E))
        self.filenamelbl.grid(column=0, row=2, columnspan=2, sticky=(W,E))
        self.prevButton.grid(column=0, row=3)
        self.nextButton.grid(column=1, row=3)

        self.onsetlbl.grid(column=2, row=1, sticky=E)
        self.offsetlbl.grid(column=2, row=2, sticky=E)
        self.IBthresholdlbl.grid(column=2, row=3, sticky=E)
        self.IRthresholdlbl.grid(column=2, row=4, sticky=E)
        
        self.onsetButton.grid(column=3, row=1, sticky=(W,E), pady=5)
        self.offsetButton.grid(column=3, row=2, sticky=(W,E), pady=5)
        self.IBthresholdField.grid(column=3, row=3, sticky=(W,E))
        self.IRthresholdField.grid(column=3, row=4, sticky=(W,E))
        
        self.nolongILIslbl.grid(column=4, row=1)
        self.nolongILIsButton.grid(column=5, row=1)
        
        self.minburstlengthlbl.grid(column=4, row=2)
        self.minburstField.grid(column=5, row=2)
        
        self.plotburstproblbl.grid(column=4, row=3)
        self.plotburstprobButton.grid(column=5, row=3)
        
        self.outputlbl.grid(column=0, row=6, sticky=(W,E), pady=5)
        self.suffixlbl.grid(column=1, row=6, sticky=(E), pady=5)
        self.suffixField.grid(column=2, row=6, sticky=(W,E), pady=5)
        
        self.defaultfolderButton.grid(column=3, row=6, sticky=(W,E), pady=5)
        self.pdfButton.grid(column=4, row=6, sticky=(W,E), pady=5)
        self.excelButton.grid(column=5, row=6, sticky=(W,E), pady=5)
        self.textsummaryButton.grid(column=6, row=6, sticky=(W,E), pady=5)
        
        self.aboutlbl.grid(column=0, row=7, columnspan=7, sticky=W)
        
        self.analyzeButton.grid(column=6, row=1, rowspan=4, sticky=(N, S, E, W))

        self.f2.grid(column=0, row=5, columnspan=7, sticky=(N,S,E,W))
                    
    def openmedfile(self):
        self.filename = filedialog.askopenfilename(initialdir=currdir, title='Select a Med PC file.')
        self.list_of_files = []
        self.loadmedfile()
        
    def loadmedfile(self):        
        try:
            if len(checknsessions(self.filename)) > 1:
                alert('More than one session in file. Analysing session 1.')
            else:                    
                self.loaded_vars = medfilereader_licks(self.filename)
        except:
            alert("Problem reading file and extracting data. File may not be properly formatted - see Help for advice.")
            return
         
        try:
            self.updateOptionMenu()
        except TypeError:
            alert("No valid variables to analyze (e.g. arrays with more than one value")
        
        self.currentfiletype = 'med'
        self.shortfilename.set(ntpath.basename(self.filename))
        
    def opencsvfile(self):
        self.filename = filedialog.askopenfilename(initialdir=currdir, title='Select a CSV file.')
        self.list_of_files = []
        self.loadcsvfile()
        
    def loadcsvfile(self):               
        try:            
            with open(self.filename, newline='') as myFile:
                reader = csv.DictReader(myFile)
                cols = reader.fieldnames
                self.loaded_vars = {}
                for col in cols:
                    self.loaded_vars[col] = []
                    myFile.seek(0)
                    for row in reader:
                        try:
                            self.loaded_vars[col].append(float(row[col]))
                        except:
                            pass 
        except:
            alert('Cannot load data from selected file. Is it a CSV?')
            return
                        
        try:
            self.updateOptionMenu()
        except TypeError:
            alert("No valid variables to analyze (e.g. arrays with more than one value")
        
        self.currentfiletype = 'csv'
        self.shortfilename.set(ntpath.basename(self.filename))
        
    def updateOptionMenu(self):
        options = [x+': '+str(len(self.loaded_vars[x])) for x in self.loaded_vars]
        self.onsetButton = ttk.OptionMenu(self, self.onset, *options).grid(column=3, row=1, sticky=(W,E))
        self.offsetButton = ttk.OptionMenu(self, self.offset, *options).grid(column=3, row=2, sticky=(W,E))

    def load_adj_files(self,delta=1): #delta+1 = next, -1=prev        
        try:
            if not self.list_of_files:
                self.currpath = ntpath.dirname(self.filename)
                self.list_of_files = os.listdir(self.currpath)
            index = [x[0] for x in enumerate(self.list_of_files) if x[1] == self.shortfilename.get()]
            newindex = index[0] + delta
            self.filename = os.path.join(self.currpath, self.list_of_files[newindex])
            
            if self.currentfiletype == 'med':
                self.loadmedfile()
            if self.currentfiletype == 'csv':
                self.loadcsvfile()
        except:
            alert('Problem loading next file. It might be at the end of the folder or in the wrong format.')
    
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
                self.onsetArray = self.loaded_vars[self.onset.get().split(':')[0]]
                try:
                    self.offsetArray = self.loaded_vars[self.offset.get().split(':')[0]]
                    self.lickdata = lickCalc(self.onsetArray, offset=self.offsetArray, burstThreshold = burstTH, runThreshold = runTH,
                                             ignorelongilis=self.nolongILIs.get(),
                                             minburstlength=int(self.minburst.get()))
                except:
                    self.lickdata = lickCalc(self.onsetArray, burstThreshold = burstTH, runThreshold = runTH,
                                             ignorelongilis=self.nolongILIs.get(),
                                             minburstlength=int(self.minburst.get()))

            except:
                alert('Have you picked an onset array yet?')
                print("Error:", sys.exc_info()[0])               
                raise
        
        else:
            print('Select a file first')
            messagebox.showinfo("Error", "Select a valid file first.")
               
        self.makegraphs()
                        
    def makegraphs(self):
        
        f = plt.figure(figsize=(8.27, 5))
        plt.suptitle(self.shortfilename.get())
        grid = plt.GridSpec(2, 3, wspace=0.5, hspace=0.5)
        ax1 = f.add_subplot(grid[0,:])
        ax2 = f.add_subplot(grid[1,0])
        ax3 = f.add_subplot(grid[1,1])
        ax4 = f.add_subplot(grid[1,2])

        # Licks over session 
        sessionlicksFig(ax1, self.onsetArray)
        
        # Lick parameter figures
        iliFig(ax2, self.lickdata)
        
        if self.plotburstprob.get() == False:
            burstlengthFig(ax3, self.lickdata)
        else:
            burstprobFig(ax3, self.lickdata)
            
        licklengthFig(ax4, self.lickdata)
        
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().grid(row=5, column=0, columnspan=7, sticky=(N,S,E,W))
      
        return f
    
    def setsavefolder(self):
        self.savefolder = get_location()
    
    def makePDF(self):
        if not hasattr(self, 'savefolder'):
            self.setsavefolder()
            
        savefile = self.savefolder + '//' + self.shortfilename.get() + self.suffix.get() + '.pdf'
        try:
            pdfFig = self.makegraphs()
            pdf_pages = PdfPages(savefile)
            pdf_pages.savefig(pdfFig)
            pdf_pages.close()
        except:
            print("Error:", sys.exc_info()[0])
            alert('Problem making PDF! Is data loaded and analyzed?')
    
    def makeExcel(self):
        if not hasattr(self, 'savefolder'):
            self.setsavefolder()
            
        savefile = self.savefolder + '//' + self.shortfilename.get() + self.suffix.get() + '.xlsx'
        
#        try:
        self.makesummarydictionary()
        
        wb = xl.Workbook(savefile)
        # worksheet with summary data
        sh = wb.add_worksheet('Summary')
        
        bold = wb.add_format({'bold': True})
        
        sh.set_column(0, 1, 20)
        sh.write('A1', 'Parameter', bold)
        sh.write('B1', 'Value', bold)
        for idx, vals in enumerate(self.d):
            sh.write(idx+1, 0, vals[0])
            sh.write(idx+1, 1, vals[1])
        
        # worksheet with lick timestamps
        sh = wb.add_worksheet('Licks')
        for idx, val in enumerate(self.onsetArray):
            sh.write(idx, 0, val)
        
        sh = wb.add_worksheet('ILIs')
        for idx, val in enumerate(self.lickdata['ilis']):
            sh.write(idx, 0, val)

        sh = wb.add_worksheet('Bursts')
        for idx, val in enumerate(self.lickdata['bLicks']):
            sh.write(idx, 0, val)
            
        wb.close()
#        except:
#            alert('Working on making an Excel file')
        
    def maketextsummary(self):
        if not hasattr(self, 'savefolder'):
            self.setsavefolder()
            
        savefile = self.savefolder + '//' + self.shortfilename.get() + self.suffix.get() + '-text_summary.csv'
        try:
            self.makesummarydictionary()
            
            with open(savefile, 'w', newline='') as file:
                csv_out = csv.writer(file)
                csv_out.writerow(['Parameter', 'Value'])
                for row in self.d:
                    csv_out.writerow(row)
        except:
            alert('Problem making text summary!')
            print("Error:", sys.exc_info()[0])
            
    def licksperburstsummary(self):
        self.folder = get_location()
        savefile = self.folder + '//' + self.shortfilename.get() + '-licks-per-burst.csv'
        try:
            d = self.data['bLicks']
        except:
            alert('Problem making text summary!')
            print("Error:", sys.exc_info()[0])
        
    def makesummarydictionary(self):
        self.d = [('Filename',self.shortfilename.get()),
                 ('Total licks',self.lickdata['total']),
                 ('Frequency',self.lickdata['freq']),
                 ('Number of bursts',self.lickdata['bNum']),
                 ('Licks per burst',self.lickdata['bMean']),
                 ('Licks per burst (first 3)',self.lickdata['bMean-first3']),
                 ('Number of long licks',len(self.lickdata['longlicks']))]

root = Tk()

currdir = os.getcwd()
currdir = 'C:\\Github\\Lick-Calc-GUI\\output\\'

app = Window(root)
root.lift()
root.mainloop()

# Files for for testing
#        self.filename = 'C:\\Users\\jaimeHP\\Dropbox\\Python\\cas9\\cas9_medfiles\\!2016-07-19_09h16m.Subject 4'
#        self.filename = 'C:\\Users\\jaimeHP\\Dropbox\\Python\\cas9\\cas9_medfiles\\!2017-06-12_10h53m.Subject thpe1.4'




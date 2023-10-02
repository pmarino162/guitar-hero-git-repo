# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 14:22:50 2023

@author: pmari
"""
#Import modules
from getTrajDf_module import getTrajDf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Get trajDf for dataset
dataset = 'CRS02b_1998_set1'
trajDf = getTrajDf(dataset)

#Setup save dir
#saveDir = Path('C:/Users/pmari/OneDrive - University of Pittsburgh/Documents/RNEL/Analysis/plots')
#filePath = saveDir / waveforms / dataset 

#Get numCh and numCond
numCh = trajDf.avgBinFr[0].shape[1]
numCond = trajDf.shape[0]

#For each channel, plot PSTH
numRows = 6
numCol = 5
numChPerFig = numRows*numCol

for cond in range(1):
    figInd = 0
    
    #Get all PSTH for current condition
    traj = trajDf.avgBinFr[cond]
    #time = 
    
    for ch in range(numCh):
        #Create new figure if necessary
        if np.ceil((ch+1)/numChPerFig) > figInd:
            plt.show()
            #plt.savefig(filePath/'waveforms_page_'str(figInd+1),format='png')
            fig, axs = plt.subplots(numRows,numCol, figsize=(20,numRows),layout='constrained')
            figInd = figInd + 1
       
        #Get row and col for plotting
        row = int(np.ceil(((ch+1)%numChPerFig)/numCol) - 1) #zero-indexed
        col = int(((ch+1) % numCol) - 1) #zero-indexed

        #Plot
        axs[row,col].plot(traj[:,ch],'r',linewidth=3)
        bottom,top = axs[row,col].get_ylim()
        left,right = axs[row,col].get_xlim()
        axs[row,col].tick_params(axis='x', which='both',bottom=False)    
        if row == 5:
            axs[row,col].tick_params(axis='x', which='both',bottom=True)
            axs[row,col].set_xlabel('time (ms)')

#     axs[row,col].text(left,top,'ch '+str(curCh)+'  vPP='+str(vPP)+'mV')
#     
#     if col == 0:
#         axs[row,col].set_ylabel('Voltage (mV)')

#     chInd = chInd + 1
    

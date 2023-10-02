# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 15:48:59 2023

@author: pmari
"""
#Import modules
from import_matlab_data import import_matlab_dataset
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


#Import Matlab data, extract spike info
dataset = 'CRS02b_1998_set1'
data = import_matlab_dataset(dataset)
rawSpikes = data['rawSpikes'][0,0]
timestamp = rawSpikes['timestamp'][0,0]
channel = rawSpikes['channel'][0,0]
waveform = rawSpikes['waveform'][0,0]

#Setup save dir
#saveDir = Path('C:/Users/pmari/OneDrive - University of Pittsburgh/Documents/RNEL/Analysis/plots')
#filePath = saveDir / waveforms / dataset 

#Get unique channel list & number of waveforms for each
channelList,numWaveforms = np.unique(channel,return_counts=True)
minNumWaveforms = np.amin(numWaveforms)

#For each unique channel, plot 10 waveforms, mean waveform, and vPP
numRows = 6
numCol = 5
numChPerFig = numRows*numCol
chInd = 0
figInd = 0
for curCh in channelList:
    #Create new figure if necessary
    if np.ceil((chInd+1)/numChPerFig) > figInd:
        plt.show()
        #plt.savefig(filePath/'waveforms_page_'str(figInd+1),format='png')
        fig, axs = plt.subplots(numRows,numCol, figsize=(20,numRows),layout='constrained')
        figInd = figInd + 1
    
    #Get all waveforms, avg waveform,vPP for curCh
    chSpikeInd = np.where(channel==curCh)
    chSpikeInd = chSpikeInd[1]
    allWaveforms = waveform[:,chSpikeInd]
    avgWaveform = np.mean(allWaveforms, axis=1)
    vPP = np.round(np.amax(avgWaveform) - np.amin(avgWaveform))
    
    #Get row and col for plotting
    row = int(np.ceil(((chInd+1)%numChPerFig)/numCol) - 1) #zero-indexed
    col = int(((chInd+1) % numCol) - 1) #zero-indexed
    
    #Plot 10 random waveforms and overlay avg waveform
    pltWfInd = np.random.choice(numWaveforms[chInd],10,replace=False)
    for wfInd in pltWfInd:
        axs[row,col].plot(allWaveforms[:,wfInd],'c')
    axs[row,col].plot(avgWaveform,'r',linewidth=3)
    bottom,top = axs[row,col].get_ylim()
    left,right = axs[row,col].get_xlim()
    axs[row,col].text(left,top,'ch '+str(curCh)+'  vPP='+str(vPP)+'mV')
    axs[row,col].tick_params(axis='x', which='both',bottom=False)
    if col == 0:
        axs[row,col].set_ylabel('Voltage (mV)')
    if row == 5:
        axs[row,col].tick_params(axis='x', which='both',bottom=True)
        axs[row,col].set_xlabel('time (ms)')
    chInd = chInd + 1
    
#After identifying bad channels, get channel list for current dataset


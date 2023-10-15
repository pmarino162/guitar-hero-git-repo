# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 12:58:59 2023

@author: pmari
"""
import numpy as np
import matplotlib.pyplot as plt

def rmCoincidentCh(binCounts):
    #Set parameters
    corrThreshold = 0.5
    
    #Get correlations
    numCh = binCounts.shape[0]
    corrMat = np.full((numCh,numCh),np.nan)
    corrList = np.full(int(((numCh**2)/2)-(numCh/2)),np.nan)
    listInd = 0
    for ch1 in range(numCh):
        for ch2 in range(ch1,numCh):
            ch1BinCounts = binCounts[ch1,:]
            ch2BinCounts = binCounts[ch2,:]
            chPairCorr = np.corrcoef(np.vstack((ch1BinCounts,ch2BinCounts)))[0,1]
            corrMat[ch1,ch2] = chPairCorr
            if ch2 > ch1:
                corrList[listInd] = chPairCorr
                listInd = listInd + 1
    #Plot heatmap
    #fig, ax = plt.subplots()
    #im = ax.imshow(corrMat)
    #Histogram of correlation coefficiencts 
    #fig, ax = plt.subplots()
    #corrList = corrList[np.absolute(corrList)>0.01]
    #ax.hist(corrList[corrList>0.01],bins=10)
    #Apply threshold
    coinPairs = np.transpose((corrMat >corrThreshold).nonzero())
    coinPairs = coinPairs[coinPairs[:,0]!=coinPairs[:,1]]
    rmCh = np.unique(coinPairs[:,1])
    binCounts = np.delete(binCounts,rmCh,0) 
    return binCounts

def rmLowFR(binCounts):
    threshold = 2#Hz
    avgFR = np.mean(binCounts,1)
    #histogram of avgFR
    #fig, ax = plt.subplots()
    #ax.hist(avgFR)
    rmCh = np.asarray((avgFR<threshold).nonzero())
    binCounts = np.delete(binCounts,rmCh,0)
    return binCounts
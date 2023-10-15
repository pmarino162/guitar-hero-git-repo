# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 17:45:12 2023

@author: pmari
"""

#Import modules
from getTrajDf_module import getTrajDf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

#Get trajDf for dataset
dataset = 'CRS02b_1998_set1'
trajDf = getTrajDf(dataset)

#Preallocate X = allAvgFr; observations x features
numCond = trajDf.shape[0]
numCh = trajDf.avgBinFr[0].shape[1]
numBins = trajDf.avgBinFr[0].shape[0]
X = np.full((numCond*numBins,numCh),np.nan)

#Concatenate avgFr across conditions
curRow = 0
for cond in range(numCond):
    X[curRow:curRow+numBins,:] = trajDf.avgBinFr[cond]
    curRow = curRow + numBins
    
    
#Fit PCs (data is automatically centered but not scaled)
numPCs = 10
pca = PCA(n_components = numPCs)
pca.fit(X)
print(pca.explained_variance_ratio_)

#Add PC projections to df
avgPCA = np.full((numCond,numBins,numPCs),np.nan)
for cond in range(numCond): 
    avgBinFR = trajDf.avgBinFr[cond]
    avgPCA[cond,:,:] = pca.fit(X).transform(avgBinFR)       
trajDf['avgPCA'] = list(avgPCA)

    
#Plot
for stimCh in [np.nan]:
    plt.show()
    fig, axs = plt.subplots(2,5, figsize=(10,2),layout='constrained')
    #plt.show()
    for intNote in [10,12,13]:
        if np.isnan(stimCh):
            traj = trajDf[np.isnan(trajDf['stimCh']) & (trajDf['intNote']==intNote)].iloc[0,trajDf.columns.get_loc('avgPCA')]
        else:
            traj = trajDf[(trajDf['stimCh']==stimCh) & (trajDf['intNote']==intNote)].iloc[0,trajDf.columns.get_loc('avgPCA')]
        for pc in range(numPCs):
            if pc < 5:
                row = 0
                col = pc
            else:
                row = 1
                col = pc-5
            axs[row,col].plot(traj[:,pc],'r',linewidth=3)
            
            
        
# -*- coding: utf-8 -*-
"""

Inputs:
    
Output: trajFrame (dataFrame)

Created on Sat Sep 16 10:30:55 2023

@author: pmari
"""
from import_matlab_data import import_matlab_dataset
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d

"DOUBLE CHECK EVERYTHING TO MAKE SURE IT's PLAYING NICE WITH MUTABLE VALUE BEHAVIOR"

def getTrajDf(dataset):
    #Import data
    data = import_matlab_dataset(dataset)
    #Function input parameters
    startTime = -40/1000
    stopTime = 200/1000
    binWidth = 20/1000
    binnedSpikes = data['binnedSpikes'][0,0]
    stimInfo = data['stimInfo'][0,0]
    notes = data['notes'][0,0]
    
    #Unpack inputs
    binTimes = np.squeeze(binnedSpikes['binTimes'][0,0].astype(float))
    binCounts = binnedSpikes['binCounts'][0,0].astype(float)
    trainStartTimes = np.squeeze(stimInfo['trainStartTimes'][0,0].astype(float))
    stimChannel = np.squeeze(stimInfo['channel'][0,0])
    instructedNotes = notes['instructedNotes'][0,0]
    
    #Convert to Hz
    binCounts = np.divide(binCounts,binWidth)
    
    #Cut binCounts rows that don't contain spikes
    hasSpikesMask = np.any(binCounts != 0,axis=1)
    binCounts = binCounts[hasSpikesMask,:]
    numCh = np.sum(hasSpikesMask)
    
    #Smooth binCounts with a Gaussian
    for ch in range(numCh):
        binCounts[ch,:] = gaussian_filter1d(binCounts[ch,:],1)
    
    " Get stimDf"
    trainStopTimes = trainStartTimes + 1
    stimDf = pd.DataFrame({'Train Start Time':trainStartTimes,
                           'Train Stop Time':trainStopTimes,
                           'stimCh':stimChannel
                            })
    
    "Get notesDf"
    #Get columns with a row = 1
    noteBool = (instructedNotes==1).any(axis=0)
    #Get number of notes
    numNotes = 0
    for i in range(noteBool.shape[0]-1):
        curBool = noteBool[i]
        nextBool = noteBool[i+1]
        if (not curBool) and nextBool:
            numNotes = numNotes + 1
    #Preallocate arrays (bins are zero-indexed)
    noteStartBin = np.zeros(numNotes)
    noteStartTime = np.zeros(numNotes)
    noteStopBin = np.zeros(numNotes)
    noteStopTime = np.zeros(numNotes)
    noteId = np.zeros(numNotes)
    #For each note, get start/end bin/time and noteId
    noteInd = 0
    for i in range(noteBool.shape[0]-1):
        curBool = noteBool[i]
        nextBool = noteBool[i+1]
        if (not curBool) and nextBool: 
            #note start
            noteStartBin[noteInd] = i+1
            noteStartTime[noteInd] = binTimes[i+1]
            #note stop
            j = i+1
            while noteBool[j]:
                j = j + 1
            noteStopBin[noteInd] = j-1
            noteStopTime[noteInd] = binTimes[j-1]
            #note Id
            noteId[noteInd] = np.where(instructedNotes[:,i+1]==1)[0][0]
            noteInd = noteInd + 1
    #Store in notesDf
    notesDf = pd.DataFrame({'Note Start Time':noteStartTime,
                            'Note Stop Time':noteStopTime,
                            'noteId':noteId,
                            })
    
    "Get trialDf"
    #Get total number of "trials" (1 per stim and/or note event)
    noteInd = 0
    stimInd = 0
    numTrials = 0
    threshold = .1 #seconds
    while (noteInd < notesDf.shape[0]) and (stimInd < stimDf.shape[0]):
        #get current note and stim times; see which is smaller
        curNoteStartTime = notesDf.loc[noteInd,'Note Start Time']
        curStimStartTime = stimDf.loc[stimInd,'Train Start Time']
        smallerTimeWasStim = bool(np.argmin(np.array([curNoteStartTime,curStimStartTime])))
        #check the other data stream to see if current events were synchronous 
        if np.absolute(curNoteStartTime-curStimStartTime) < threshold: 
            noteInd = noteInd + 1
            stimInd = stimInd + 1
        else:
            if smallerTimeWasStim:
                stimInd = stimInd + 1
            else:
                noteInd = noteInd + 1
        #Increment numTrials        
        numTrials = numTrials + 1
    
    #Preallocate numpy arrays
    #
    noteId = np.full(numTrials,np.nan)
    noteStartTime = np.full(numTrials,np.nan)
    noteStopTime = np.full(numTrials,np.nan)
    stimCh = np.full(numTrials,np.nan)
    stimStartTime = np.full(numTrials,np.nan)
    stimStopTime = np.full(numTrials,np.nan)
    
    #Step through note and stimDf and add data to prellocated arrays
    noteInd = 0
    stimInd = 0
    trial = 0
    while (noteInd < notesDf.shape[0]) and (stimInd < stimDf.shape[0]):
        #get current note and stim times; see which is smaller
        curNoteStartTime = notesDf.loc[noteInd,'Note Start Time']
        curStimStartTime = stimDf.loc[stimInd,'Train Start Time']
        smallerTimeWasStim = bool(np.argmin(np.array([curNoteStartTime,curStimStartTime])))
        #check the other data stream to see if current events were synchronous 
        if np.absolute(curNoteStartTime-curStimStartTime) < threshold: 
            stimCh[trial] = stimDf.loc[stimInd,'stimCh']
            stimStartTime[trial] = stimDf.loc[stimInd,'Train Start Time']
            stimStopTime[trial] = stimDf.loc[stimInd,'Train Stop Time']
    
            noteId[trial] = notesDf.loc[noteInd,'noteId']
            noteStartTime[trial] = notesDf.loc[noteInd,'Note Start Time']
            noteStopTime[trial] = notesDf.loc[noteInd,'Note Stop Time']
            noteInd = noteInd + 1
            stimInd = stimInd + 1
        else:
            if smallerTimeWasStim:
                stimCh[trial] = stimDf.loc[stimInd,'stimCh']
                stimStartTime[trial] = stimDf.loc[stimInd,'Train Start Time']
                stimStopTime[trial] = stimDf.loc[stimInd,'Train Stop Time']
                stimInd = stimInd + 1          
            else:
                noteId[trial] = notesDf.loc[noteInd,'noteId']
                noteStartTime[trial] = notesDf.loc[noteInd,'Note Start Time']
                noteStopTime[trial] = notesDf.loc[noteInd,'Note Stop Time']
                noteInd = noteInd + 1
        #Increment numTrials        
        trial = trial + 1
    
    
    #Store in trialDf
    trialDf = pd.DataFrame({'noteId':noteId,
                            'noteStartTime':noteStartTime,
                            'noteStopTime':noteStopTime,
                            'stimCh':stimCh,
                            'stimStartTime':stimStartTime,
                            'stimStopTime':stimStopTime
                            })
    
    #Get all possible conditions
    allCondDf = trialDf[['noteId','stimCh']]
    allCondDf = allCondDf.drop_duplicates(ignore_index = True)
    allCondDf = allCondDf.sort_values(by=['noteId', 'stimCh'],ignore_index = True)
    numCond = allCondDf.shape[0]
    numBins = int(np.ceil((stopTime-startTime)/binWidth))
    
    #Preallocate trajDf columns (to total num trials for each condition)
    stimCh = np.full((numCond,numTrials),np.nan)
    intNote = np.full((numCond,numTrials),np.nan)
    noteStartTime = np.full((numCond,numTrials),np.nan)
    noteStopTime = np.full((numCond,numTrials),np.nan)
    stimStartTime = np.full((numCond,numTrials),np.nan)
    stimStopTime = np.full((numCond,numTrials),np.nan)
    allBinFr = np.full((numCond,numTrials,numBins,numCh),np.nan)
    avgBinFr = np.full((numCond,numBins,numCh),np.nan)
    noteTime = np.full((numTrials,2),np.nan)
    
    for cond in range(numCond): 
         #Get condDf
         if np.isnan(allCondDf.loc[cond,'noteId']):
             condDf = trialDf[np.isnan(trialDf['noteId']) & (trialDf['stimCh']==allCondDf.loc[cond,'stimCh'])]
         elif np.isnan(allCondDf.loc[cond,'stimCh']):
             condDf = trialDf[(trialDf['noteId']==allCondDf.loc[cond,'noteId']) & np.isnan(trialDf['stimCh'])]
         else:
             condDf = trialDf[(trialDf['noteId']==allCondDf.loc[cond,'noteId']) & (trialDf['stimCh']==allCondDf.loc[cond,'stimCh'])]
         numCondTrials = condDf.shape[0]
         for trial in range(numCondTrials):
             stimCh[cond,trial] = condDf.iloc[trial,condDf.columns.get_loc('stimCh')]
             intNote[cond,trial] = condDf.iloc[trial,condDf.columns.get_loc('noteId')]
             noteStartTime[cond,trial] = condDf.iloc[trial,condDf.columns.get_loc('noteStartTime')]
             noteStopTime[cond,trial] = condDf.iloc[trial,condDf.columns.get_loc('noteStopTime')]
             stimStartTime[cond,trial] = condDf.iloc[trial,condDf.columns.get_loc('stimStartTime')]
             stimStopTime[cond,trial] = condDf.iloc[trial,condDf.columns.get_loc('stimStopTime')]
             #Get binned spikes
             firstEventTime = np.nanmin(np.array([noteStartTime[cond,trial],stimStartTime[cond,trial]]))
             timeWindow = np.array([firstEventTime+startTime,firstEventTime+stopTime])
             timeMask = (binTimes >= timeWindow[0]) & (binTimes < timeWindow[1])
             allBinFr[cond,trial,:,:] = np.transpose(binCounts[:,timeMask])
         avgBinFr[cond,:,:] = np.nanmean(allBinFr[cond,:,:,:],axis=0)
          
    # Clear pages of nans
    #for each condition, clear all blank trials
    
    
    
    #Store in trajDf
    trajDf = pd.DataFrame({'stimCh':list(stimCh),
                          'intNote':list(intNote),
                          'stimStartTime':list(stimStartTime),
                          'stimStopTime':list(stimStopTime),
                          'noteStartTime':list(noteStartTime),
                          'noteStopTime':list(noteStopTime),
                          'allBinFr':list(allBinFr),
                          'avgBinFr':list(avgBinFr)
                            })
    
    return trajDf


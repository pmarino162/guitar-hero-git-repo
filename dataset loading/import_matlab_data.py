# -*- coding: utf-8 -*-
"""
Loads preprocessed Matlab data for use with python

Created on Mon Sep  4 14:56:06 2023

@author: pmari
"""

import numpy as np
import scipy
from pathlib import Path
    
def import_matlab_dataset(dataset):
    #Import Matlab data struct
    saveDir = Path('D:/RNEL Data/')
    filePath = saveDir / dataset / (dataset + '.mat')
    data = scipy.io.loadmat(filePath)
    data = data['data']
    return data


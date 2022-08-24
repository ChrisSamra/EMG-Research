import os
import sys
from time import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import scipy.io as sio
import sklearn
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt, iirnotch, periodogram
from skimage.restoration import denoise_wavelet


def correct_mean_emg(emg_2D, num_chan):
    
    emg_co = np.zeros((emg_2D.shape[0],emg_2D.shape[1]))
    
    for channel in range(0, num_chan):
        emg_co[channel,:] = emg_2D[channel,:] - np.mean(emg_2D[channel,:])
        
    return emg_co

def butter_bandpass_filter(data, lowcut, highcut, sample_rate, order):

    nyq = 0.5 * sample_rate
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y

def butter_highpass_filter(data, lowcut, sample_rate, order):
    
    nyq = 0.5 * sample_rate
    low = lowcut / nyq
    b, a = butter(order, low, btype='high')
    y = filtfilt(b, a, data)
    return y

def iir_notch_filter(data, f0, Q, fs):

    b, a = iirnotch(f0, Q, fs)
    y = filtfilt(b, a, data)
    #still need to filter harmonics
    return y


#try zeroing out later coefficients to remove ecg if possible/needed
def wavelet_denoise(emg_2D, num_chan):
    
    emg_ecg_rem = np.zeros((emg_2D.shape[0],emg_2D.shape[1]))
    
    for channel in range(0, num_chan):
        
        # soft universal thresholding method applied
        # wavelet decomposes signal by 6 levels (6 detail and 6 approximate coefficients)
        # once threshold is applied, signal gets reconstructed, this all happens in one function call
        emg_ecg_rem[channel,:] = denoise_wavelet(emg_2D[channel,:], method='VisuShrink', mode='soft',wavelet_levels=10,wavelet='db7',rescale_sigma=True)

    return emg_ecg_rem
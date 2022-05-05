from audioop import findfactor
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.io import wavfile
from scipy.fft import rfft
import numpy as np

#config
pulse_length_s = 0.003
bandwidth = 4000
center_freq = 22000
pulse_pause_s = 0.3 # time between pulses excluding the pulse itself
speed_of_sound = 343.21 # speed of sound in m/s, may have to be adjusted for accurate distance values
autodetect_peak = True # try to automatically detect pulse, without this set the input WAV will have to start with the first pulse and time drift will cause problems
average = 10 # number of pulses to average

def average_array(array):
    average = 0
    for val in array:
        average += val
    return average / len(array)

def find_fft_peak(startindex, endindex, array):
    highestindex = startindex
    for i in range(endindex - startindex):
        if(average_array(array[highestindex]) < average_array(array[i + startindex])):
            highestindex = i + startindex
    return highestindex

class FFTaverager:
    def __init__(self, fftlen, ffts):
        self.avgarr = [ [0]*fftlen for i in range(ffts)]
        self.ffts = ffts
        self.fftlen = fftlen
        self.avgcount = 0
    
    def add_avg(self, inarray):
        for i in range(len(inarray)):
            for j in range(self.fftlen):
                self.avgarr[i][j] += inarray[i][j]
        self.avgcount += 1

    def get_result(self):
        outarr = [ [0]*self.fftlen for i in range(self.ffts)]
        for i in range(self.ffts):
            for j in range(self.fftlen):
                outarr[i][j] = self.avgarr[i][j] / self.avgcount
        return outarr

    def reset(self):
        self.avgarr = [ [0]*self.fftlen for i in range(self.ffts)]
        self.avgcount = 0

sample_rate, samples = wavfile.read('sonar.wav')
pulsesamples = int((pulse_pause_s) * sample_rate)
fft_n = int(pulse_length_s * sample_rate)
ffts_per_pulse = int(pulsesamples / fft_n)
ffts = []
for i in range(int(len(samples) / fft_n)):
    realindex = i * fft_n
    fftarr = samples[realindex:realindex+fft_n]
    fftresult = rfft(fftarr)
    fftresult2 = []
    for j in range(int(fft_n / 2)):
        freq = j * sample_rate / fft_n
        if(freq <= center_freq + bandwidth and freq >= center_freq - bandwidth):
            fftresult2.append(np.abs(fftresult[j]))
    ffts.append(fftresult2)

fftarr_length = len(ffts[0])

range_arr = []
for i in range(ffts_per_pulse):
    t = pulse_length_s * i * 2
    range_arr.append(int(t * speed_of_sound))
    if(i % 2 != 0):
        range_arr[i] = ""


fftavg = FFTaverager(fftarr_length, ffts_per_pulse)

fig, ax = plt.subplots(1,1)
avgcounter = 0
for i in range(int(len(samples) / pulsesamples)):
    realindex = i * pulsesamples
    fftindex = int(realindex / fft_n)
    if(autodetect_peak):
        fftindex = find_fft_peak(int(realindex / fft_n), int(realindex / fft_n) + ffts_per_pulse, ffts) - 1
    fftavg.add_avg(ffts[fftindex:fftindex + ffts_per_pulse])
    avgcounter += 1
    if(avgcounter % average == 0):
        plt.pcolor(fftavg.get_result())
        ax.set_yticks(range(ffts_per_pulse))
        ax.set_yticklabels(range_arr)
        plt.pause(pulse_pause_s + pulse_length_s)
        plt.pause(3)
        avgcounter = 0
        fftavg.reset()
plt.show()

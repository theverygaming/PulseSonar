import re
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fft import rfft
import numpy as np

#config
pulse_length_s = 0.003
bandwidth = 4000
center_freq = 22000


sample_rate, samples = wavfile.read('sonar.wav')
fft_n = int(pulse_length_s * sample_rate)
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

plt.imshow(ffts[:300])
plt.show()
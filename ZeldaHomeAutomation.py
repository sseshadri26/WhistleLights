
import time
import pyaudio
import wave
import sys
import numpy as np
import paho.mqtt.publish as publish
from collections import deque
import pygame
pygame.mixer.init()
notes=deque([1, 2, 3, 4, 5, 6], maxlen=6)
songTime=deque(['A', 'D', 'F', 'A', 'D', 'F'])
songSun=deque(['A', 'F', 'D', 'A', 'F', 'D'])
minuetForest1=deque(['E', 'D', 'B', 'A', 'B', 'A'])
minuetForest2=deque(['F', 'D', 'B', 'A', 'B', 'A'])
minuetForest3=deque(['G', 'D', 'B', 'A', 'B', 'A'])
minuetForest4=deque(['A', 'D', 'B', 'A', 'B', 'A'])
minuetForest5=deque(['B', 'D', 'B', 'A', 'B', 'A'])
CHUNK = 4096
lastNote='C'
# use a Blackman window
window = np.blackman(CHUNK)
    
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

on=False

p = pyaudio.PyAudio()
print (p.get_device_count())
print (p.get_device_info_by_index(0))

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Starting audio input.")
servoOn=False

while (True):
    try:
        data = stream.read(CHUNK)
        indata = np.array(wave.struct.unpack("%dh"%(CHUNK), data))*window
        fftData=abs(np.fft.rfft(indata))**2
        # find the maximum
        which = fftData[1:].argmax() + 1
        # use quadratic interpolation around the max
        if which != len(fftData)-1:
            y0,y1,y2 = np.log(fftData[which-1:which+2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
            # find the frequency and output it
            thefreq = (which+x1)*RATE/CHUNK
        else:
            thefreq = which*RATE/CHUNK

        if ((570<thefreq<600 or 279<thefreq<309 or 1144<thefreq<1206) and notes[-1]!='D'):
            print("You played D!")
            notes.append('D')
        if ((645<thefreq<675 or 314<thefreq<338 or 1288<thefreq<1348) and notes[-1]!='E'):
            print("You played E!")    
            notes.append('E')
        if ((675<thefreq<725 or 339<thefreq<365 or 1349<thefreq<1450) and notes[-1]!='F'):
            print("You played F!")
            notes.append('F')        
        if ((770<thefreq<800 or 375<thefreq<410 or 1500<thefreq<1640) and notes[-1]!='G'):
            print("You played G!")          
            notes.append('G')
        if ((865<thefreq<895 or 420<thefreq<455 or 1700<thefreq<1830) and notes[-1]!='A'):
            print("You played A!")
            notes.append('A')
        if ((970<thefreq<1000 or 470<thefreq<510 or 1890<thefreq<2025) and notes[-1]!='B'):
            print("You played B!")
            notes.append('B')
        if (notes==songTime):
            pygame.mixer.music.load("/home/pi/Music/OOT_Song_Correct.wav")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                continue
            if (on==False):
                publish.single("ledStatus","1")
                on=True
                print ("You played the Song of Time! Turning light on.")
                notes.append('C')
            else:
                publish.single("ledStatus","0")
                print ("You played the Song of Time! Turning light off.")
                on=False
                notes.append('C')
        if (notes==songSun):
            pygame.mixer.music.load("/home/pi/Music/OOT_Song_Correct.wav")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                continue
            if (on==False):
                publish.single("ledStatus","1")
                on=True
                print ("Good Morning!")
                notes.append('C')
            else:
                publish.single("ledStatus","0")
                print ("Good Night!")
                on=False
                notes.append('C')
        if (notes==minuetForest1 or notes==minuetForest2 or notes==minuetForest3 or notes==minuetForest4 or notes==minuetForest5):
            pygame.mixer.music.load("/home/pi/Music/OOT_Song_Correct.wav")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                continue
            if (on==False):
                publish.single("servoStatus","1")
                servoOn=True
                print ("Minuet")
                notes.append('C')
            else:
                publish.single("servoStatus","0")
                print ("More Minuet")
                servoOn=False
                notes.append('C')
    except:
        print("Ignoring Exception.")

stream.stop_stream()
stream.close()
p.terminate()
publish.single("ledStatus","0")



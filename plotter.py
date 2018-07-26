# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 10:42:36 2018

@author: Suri
NEcesito:
    RPI con pines soldados
    Todos los relojes
    Todas las MicroSD
    Lector de escritorio
"""
from datagetter import DataGetSerial
import matplotlib.pyplot as plt
import numpy as np
from drawnow import *
import csv

def init_list_of_objects(size):
    list_of_objects = list()
    for i in range(0,size):
        list_of_objects.append( list() ) #different object reference each time
    return list_of_objects

n = 9
dgs = DataGetSerial('COM5', n)
plt.ion()
y = init_list_of_objects(n)
#t = []
#dt = 0.01
cnt = 0
def MakeFig():
    plt.ylim(np.amin([y[1], y[2], y[3]])-2, np.amax([y[1], y[2], y[3]])+2)
    plt.xlim(min(y[0]), max(y[0]))
    plt.title("Grafico en tiempo real de salida Arduino")
    plt.grid(True)
    plt.xlabel("Tiempo [segs]")
    plt.ylabel("Salida giroscopio [grados/s]")
    nplot = 1; plt.plot(y[0], y[nplot], 'purple', label="Aceleracion en X")
    nplot +=1; plt.plot(y[0], y[nplot], 'orange', label="Aceleracion en Y")
    nplot +=1; plt.plot(y[0], y[nplot], 'g', label="Aceleracion en z")
    #nplot =1; plt.plot(y[0], y[nplot], 'r', label="Velocidad angular X")
    #nplot =1; plt.plot(y[0], y[nplot], 'g', label="Velocidad angular Y")
    #nplot +=1; plt.plot(y[0], y[nplot], 'b', label="Velocidad angular X, Kalman")
    #nplot +=1; plt.plot(y[0], y[nplot], 'y', label="Velocidad angular Y, Kalman")
    plt.legend(loc='upper left')

with open("data.csv", 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Tiempo', 'AccX', 'AccY', 'AccZ', 'GiroY', 'KalmanGiroY',
                        'Pitch', 'KalmanPitch', 'DMPPitch'])
    while True:
        reading = dgs.get_next()
        print("THIS IS", reading)
        if len(reading) == n+1:
            line = []
            for i in range(n):
                try:
                    curr = float(reading[i])
                    y[i].append(curr)
                    line.append(curr)
                except ValueError:
                    print("Value error!")
                    y[i].append(y[i][-1]+0.00000000001)
                    line.append(y[i][-1]+0.00000000001)
            csvwriter.writerow(line)
        else:
            continue
            #for i in range(n):
            #    y[i].append(0)
        #if len(t) == 0: t.append(0)
        #else: t.append(t[-1] + dt)
        
        #if cnt%5 == 0:
            #drawnow(MakeFig)
            #plt.pause(.000001)
        if cnt > 200:
            #t.pop(0)
            for i in range(n):
                y[i].pop(0)
        cnt += 1
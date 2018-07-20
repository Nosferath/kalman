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

n = 3
dgs = DataGetSerial('COM25', n)
plt.ion()
y = init_list_of_objects(n)
t = []
dt = 0.01
cnt = 0
def MakeFig():
    plt.ylim(np.amin(y)-2, np.amax(y)+2)
    plt.title("Grafico en tiempo real de salida Arduino")
    plt.grid(True)
    plt.ylabel("Salida giroscopio [grados/s]")
    plt.plot(t, y[0], 'r', t, y[1], 'g', t, y[2], 'b')#, label="Velocidad angular")
    #plt.legend(loc='upper left')

with open("data.csv", 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['ax', 'ay', 'az'])
    while True:
        reading = dgs.get_next()
        print("THIS IS", reading)
        if len(reading) == n+2:
            line = []
            for i in range(n):
                try:
                    curr = float(reading[i+1])
                    y[i].append(curr)
                    line.append(curr)
                except ValueError:
                    print("Value error!")
                    y[i].append(0)
                    line.append(0)
            csvwriter.writerow(line)
        else:
            continue
            #for i in range(n):
            #    y[i].append(0)
        if len(t) == 0: t.append(0)
        else: t.append(t[-1] + dt)
        if cnt%6 == 0:
            drawnow(MakeFig)
            plt.pause(.000001)
        if cnt > 100:
            t.pop(0)
            for i in range(n):
                y[i].pop(0)
        cnt += 1
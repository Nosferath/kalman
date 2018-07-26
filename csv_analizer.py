import matplotlib.pyplot as plt
import numpy as np
import csv

first = True
datos = {}
clases = []
with open("data_seria_1.csv", 'r', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for linea in csvreader:
        if first == True:
            for clase in linea:
                datos[clase] = []
                clases.append(clase)
            first = False
        else:
            for i in range(len(linea)):
                datos[clases[i]].append(float(linea[i]))
            
    
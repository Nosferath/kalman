# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np

vuelta = 0
vueltas = []

e_roll = []
std_roll = []
mse_roll = []

e_giro = []
std_giro = []
mse_giro = []

e_kal = []
std_kal = []
mse_kal = []

with open("analisis_errores_rapido.txt", 'r') as archivo_errores:
    for linea in archivo_errores:
        if "VUELTA" in linea:
            vuelta = int(linea.split()[3])
            vueltas.append(vuelta)
            continue
        if "KalmanRoll" in linea:
            if "Error absoluto" in linea:
                e_kal.append(float(linea.split()[-1]))
            elif "Desviacion" in linea:
                std_kal.append(float(linea.split()[-1]))
            elif "MSE" in linea:
                mse_kal.append(float(linea.split()[-1]))
        elif "Roll" in linea:
            if "Error absoluto" in linea:
                e_roll.append(float(linea.split()[-1]))
            elif "Desviacion" in linea:
                std_roll.append(float(linea.split()[-1]))
            elif "MSE" in linea:
                mse_roll.append(float(linea.split()[-1]))
        elif "GiroXAngle" in linea:
            if "Error absoluto" in linea:
                e_giro.append(float(linea.split()[-1]))
            elif "Desviacion" in linea:
                std_giro.append(float(linea.split()[-1]))
            elif "MSE" in linea:
                mse_giro.append(float(linea.split()[-1]))
   
plt.errorbar(vueltas, e_roll, yerr=std_roll, color='b', marker='o', label="Roll")
#plt.errorbar(vueltas, e_giro, yerr=std_giro, color='r', marker='o', label="GiroXAngle")
plt.errorbar(vueltas, e_kal, yerr=std_kal, color='g', marker='o', label="KalmanRoll")
plt.legend(loc='upper left')
plt.xlim([vueltas[0], vueltas[-1]])
plt.xlabel("N° de vuelta")
plt.ylabel("Error absoluto medio [°]")
plt.grid(True)
plt.title("Error absoluto medio por vuelta, prueba rápida")
plt.savefig("plots/error_medio_rapido.png")
plt.clf()

plt.plot(vueltas, mse_roll, 'b', marker='o', label="Roll")
#plt.plot(vueltas, mse_giro, 'r', marker='o', label="GiroXAngle")
plt.plot(vueltas, mse_kal, 'g', marker='o', label="KalmanRoll")
plt.legend(loc='upper left')
plt.xlim([vueltas[0], vueltas[-1]])
plt.xlabel("N° de vuelta")
plt.ylabel("Error cuadrático medio [°]")
plt.grid(True)
plt.title("Error cuadrático medio por vuelta, prueba rápida")
plt.savefig("plots/error_mse_rapido.png")

print("Error absoluto medio total")
print("Roll medido por acelerómetro: {}, +/-{}".format(np.mean(e_roll), np.std(e_roll)))
print("Roll medido por giroscopio: {}, +/-{}".format(np.mean(e_giro), np.std(e_giro)))
print("Roll estimado por Kalman: {}, +/-{}".format(np.mean(e_kal), np.std(e_kal)))

print("Error cuadrático medio total")
print("Roll medido por acelerómetro: {}, +/-{}".format(np.mean(mse_roll), np.std(mse_roll)))
print("Roll medido por giroscopio: {}, +/-{}".format(np.mean(mse_giro), np.std(mse_giro)))
print("Roll estimado por Kalman: {}, +/-{}".format(np.mean(mse_kal), np.std(mse_kal)))

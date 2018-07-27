import matplotlib.pyplot as plt
#import numpy as np
import csv

first = True
datos = {}
clases = []
with open("data_vgirofix_2.csv", 'r', newline='') as csvfile:
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
colores = ['b', 'r', 'g']            
while True:
    print("\nIndica hasta 3 valores para plotear (separados por espacios), o 'Exit' para salir:\n", ", ".join(clases[1:]))
    toplot = input().split(" ")
    if len(toplot) == 1 and toplot[0] in '\'Exit\'': exit()
    if len(toplot) > 3:
        print("Debes indicar 3 valores como maximo")
        continue
    if not set(toplot).issubset(clases[1:]):
        print("Las opciones son:", ", ".join(clases[1:]))
        continue
    nmax = len(datos[clases[0]])-1
    print("\nIndica un rango en X, desde 0 hasta {} para graficar, o deja en blanco para usar todo el rango".format(nmax))
    print("Ejemplo: 0 500")
    rango = input().split(" ")
    if len(rango) == 1 and rango[0] == "":
        indices = [0, nmax]
    elif len(rango) > 2:
        print("Debes ingresar solo dos valores")
        continue
    elif len(rango) == 2:
        try:
            indices = [int(rango[0]), int(rango[1])]
        except ValueError:
            print("Debes ingresar dos numeros enteros entre 0 y {}".format(nmax))
            continue
        if indices[0] not in range(nmax+1) or indices[1] not in range(nmax+1):
            print("Debes ingresar dos numeros enteros entre 0 y {}".format(nmax))
            continue
    n = 0
    plt.grid(True)
    plt.xlim(datos[clases[0]][indices[0]], datos[clases[0]][indices[1]])
    for item in toplot:
        plt.plot([datos[clases[0]][i] for i in range(indices[0], indices[1]+1)],
                 [datos[item][i] for i in range(indices[0], indices[1]+1)],
                   colores[n], label=item)
        n += 1
    plt.legend(loc='upper left')
    plt.show()
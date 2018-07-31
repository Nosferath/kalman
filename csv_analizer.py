import matplotlib.pyplot as plt
#import numpy as np
import csv

gt_t = []
gt_angulo =[]
# gt_dt = 51.555 - 50.06 # caso rapido 171450
gt_dt = 74.062 - 72.34 # caso lento 172312
first = True
with open("datos_172312", 'r', newline='') as gt_file:
    gt_csv = csv.reader(gt_file)
    for linea in gt_csv:
        if first:
            first = False
        else:
            gt_t.append(float(linea[0]) - gt_dt)
            gt_angulo.append(-float(linea[1][:-1]))
first = True
datos = {}
clases = []
with open("data_FINAL_lento.csv", 'r', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for linea in csvreader:
        if first:
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
    #plt.plot(gt_t, gt_angulo, 'purple', label='Ground truth')
    plt.legend(loc='upper left')
    plt.show()
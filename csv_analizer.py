import matplotlib.pyplot as plt
import scipy.interpolate as interp
import numpy as np
import csv

gt_t = []
gt_angulo =[]
# gt_dt = 51.555 - 50.06 # caso lento
gt_dt = 59.077 - 56.45 # caso rapido
first = True
with open("angulos_rapido", 'r', newline='') as gt_file:
    gt_csv = csv.reader(gt_file)
    for linea in gt_csv:
        if first:
            first = False
        else:
            gt_t.append(float(linea[0]) - gt_dt)
            gt_angulo.append(-float(linea[1][:-2]))
first = True
datos = {}
clases = []
with open("data_FINAL2_rapido.csv", 'r', newline='') as csvfile:
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
    print("Puedes agregar adicionalmente Error al final para calcular el error con respecto al ground truth.")
    toplot = input().split(" ")
    if len(toplot) == 1 and toplot[0] in '\'Exit\'': exit()
    if len(toplot) == 1 and toplot[0] == "indices":
        print("%%%TIEMPOS PARA KALMANROLL%%%")
        roll = datos["KalmanRoll"]
        check = roll[0] < -160
        for i in range(len(roll)):
            if check and roll[i] > 160:
                print("Indice {}, tiempo {}".format(i, datos["Tiempo"][i]))
                check = False
            elif roll[i] < -160:
                check = True
        exit()
    if len(toplot) > 3 and "Error" not in toplot:
        print("Debes indicar 3 valores como maximo")
        continue
    use_error = False
    if toplot[-1] == "Error":
        use_error = True
    if not set(toplot).issubset(clases[1:]) and not use_error or not set(toplot[:-1]).issubset(clases[1:]) and use_error:
        print("Las opciones son:", ", ".join(clases[1:]))
        continue
    nmax = len(datos[clases[0]])-1
    if not use_error:
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
    else:
        indices = [0, nmax]
    n = 0
    plt.grid(True)
    plt.xlim(datos[clases[0]][indices[0]], datos[clases[0]][indices[1]])
    datos_t = [datos[clases[0]][i] for i in range(indices[0], indices[1]+1)]
    if not use_error:
        for item in toplot:
            plt.plot(datos_t,
                     [datos[item][i] for i in range(indices[0], indices[1]+1)],
                     colores[n], label=item)
            n += 1
        plt.plot(gt_t, gt_angulo, 'purple', label='Ground truth')
    else:
        # Dejar solo una vuelta
        vuelta = [717, 743]
        datos_t = datos_t[vuelta[0]:vuelta[1]]
        plot_items = []
        for item in toplot[:-1]:
            plot_items.append(datos[item][vuelta[0]:vuelta[1]])
        # Borrar tiempo en datos_t anterior al ground truth
        j = 0
        while datos_t[0] > gt_t[j]:
            j += 1
        gt_t2 = gt_t[j:]
        gt_angulo2 = gt_angulo[j:]
        j = 1
        while datos_t[-1] < gt_t2[-j]:
            j += 1
        gt_t2 = gt_t2[:-j+1] if j != 1 else gt_t2
        gt_angulo2 = gt_angulo2[:-j+1] if j != 1 else gt_angulo2
        """
        j = 0
        while datos_t[j] < gt_t[0]:
            j += 1
        datos_t = datos_t[j:]
        plot_items = []
        for item in plot_items:
            item = item[j:]
        # Borrar el tiempo en gt_t posterior a datos_t
        j = 1
        while gt_t[-j] > datos_t[-1]:
            #print("gt es {} y datos es {}".format(gt_t[-j], datos_t[-1]))
            j += 1
        gt_t2 = gt_t[:-j+1] if j != 1 else gt_t
        gt_angulo2 = gt_angulo[:-j+1] if j != 1 else gt_angulo
        """
        # Mezclar ambos tiempos
        new_time = []
        j = k = 0
        while True:
            if k >= len(datos_t):
                if len(new_time) > 0:
                    if gt_t2[j] != new_time[-1]:
                        new_time.append(gt_t2[j])
                else:
                    new_time.append(gt_t2[j])
                j += 1
            elif j >= len(gt_t2):
                # Evitar que se repitan tiempos
                if len(new_time) > 0:
                    if datos_t[k] != new_time[-1]:
                        new_time.append(datos_t[k])
                else:
                    new_time.append(datos_t[k])
                k += 1
            elif gt_t2[j] <= datos_t[k]:
                # Evitar que se repitan tiempos
                if len(new_time) > 0:
                    if gt_t2[j] != new_time[-1]:
                        new_time.append(gt_t2[j])
                else:
                    new_time.append(gt_t2[j])
                j += 1
            elif gt_t2[j] > datos_t[k]:
                # Evitar que se repitan tiempos
                if len(new_time) > 0:
                    if datos_t[k] != new_time[-1]:
                        new_time.append(datos_t[k])
                else:
                    new_time.append(datos_t[k])
                k += 1
            else:
                print("Stuck in a loop, gt_t[j]={}, datos_t[k]={}".format(gt_t2[j], datos_t[k]))
            if j >= len(gt_t2) and k >= len(datos_t):
                break
        # Generar objetos interpolables e interpolaciones (n_)
        gt_interp = interp.interp1d(gt_t2, gt_angulo2)
        while True:
            try:
                n_gt_interp = gt_interp(new_time)
                break
            except ValueError as e:
                e = str(e)
                if "below" in e:
                    new_time = new_time[1:]
                elif "above" in e:
                    new_time = new_time[:-1]
                else:
                    print("No sirvio m3n")
                    exit(1)
        items_interp = []
        for item in plot_items:
            items_interp.append(interp.interp1d(datos_t, item))
        n_items_interp = []
        for item in items_interp:
            while True:
                try:
                    n_items_interp.append(item(new_time))
                    break
                except ValueError as e:
                    e = str(e)
                    if "below" in e:
                        new_time = new_time[1:]
                    elif "above" in e:
                        new_time = new_time[:-1]
                    else:
                        print("No sirvio m3n")
                        exit(1)
        n_gt_interp = gt_interp(new_time)
        for item in n_items_interp:
            # Calcular error absoluto
            for i in range(len(new_time)):
                item[i] = (item[i] - n_gt_interp[i])**2
            print("Error cuadratico medio de {}: {}".format(toplot[n], np.mean(item)))
            print("Desviacion estandar de MSE de {}: {}".format(toplot[n], np.std(item)))
            plt.plot(new_time, item, colores[n], label=toplot[n])
            n += 1
    plt.xlim([new_time[0], new_time[-1]])
    plt.legend(loc='upper left')
    plt.show()
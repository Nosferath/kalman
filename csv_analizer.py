import matplotlib.pyplot as plt
import scipy.interpolate as interp
import numpy as np
import csv

print("Indica la prueba a analizar [lento, rapido]")
velocidad = input() # "lento" o "rapido"

gt_t = []
gt_angulo =[]
if velocidad == "lento":
    gt_dt = 1.059 - 42.08 # caso lento
elif velocidad == "rapido":
    gt_dt = 59.077 - 56.45 # caso rapido
else:
    print("Variable velocidad debe ser lento o rapido")
    exit(1)
    
print("Indica 'y' si quieres incluir o no el ángulo del ground truth, sino deja en blanco")
use_gt = input()
if use_gt == 'y':
    use_gt = True
    print("Incluyendo ground truth")
else:
    use_gt = False
    print("No se incluirá ground truth")
    
first = True
with open("angulos_{}.csv".format(velocidad), 'r', newline='') as gt_file:
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
with open("data_FINAL2_{}.csv".format(velocidad), 'r', newline='') as csvfile:
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
    print("Puedes agregar adicionalmente Error al final para calcular el error con respecto al ground truth.\nUsar solo con Roll, KalmanRoll y GiroXAngle.")
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
    datos_t_full = [datos[clases[0]][i] for i in range(indices[0], indices[1]+1)]
    if not use_error:
        title = input("Ingresa el título del gráfico: ")
        ylabel = input("Ingresa la etiqueta del eje Y: ")
        for item in toplot:
            plt.plot(datos_t_full,
                     [datos[item][i] for i in range(indices[0], indices[1]+1)],
                     colores[n], label=item)
            n += 1
        if use_gt:
            plt.plot(gt_t, gt_angulo, 'purple', label='Ground truth')
        plt.legend(loc='upper left')
        plt.title(title)
        plt.ylabel(ylabel)
        plt.xlabel("Tiempo [s]")
        plt.show()
    else:
        # Parsear y almacenar indices donde inicia cada nueva vuelta #
        indices_roll = []
        indices_kroll = []
        reading_roll = True
        with open("indices_salto_{}.txt".format(velocidad), 'r') as archivo_indices:
            for linea in archivo_indices:
                if reading_roll and "KALMANROLL" in linea:
                    reading_roll = False
                    continue
                if 'Indice' not in linea:
                    continue
                if reading_roll:
                    indices_roll.append(int(linea.split()[1][:-1]))
                else:
                    indices_kroll.append(int(linea.split()[1][:-1]))
        if len(indices_roll) != len(indices_kroll):
            print("Indices roll tiene largo {} e indices kalmanroll tiene largo {}".format(
                    len(indices_roll), len(indices_kroll)))
            exit(1)
        # Juntar indices de a pares #
        indices_vueltas = []
        for i in range(len(indices_roll)-1):
            indices_vueltas.append((max(indices_roll[i], indices_kroll[i]),
                                    min(indices_roll[i+1], indices_kroll[i+1])))
        for indice in range(len(indices_vueltas)):
            n = 0
            indices = indices_vueltas[indice]
            # Dejar solo una vuelta #
            datos_t = datos_t_full[indices[0]:indices[1]]
            plot_items = []
            for item in toplot[:-1]:
                plot_items.append(datos[item][indices[0]:indices[1]])
            # Borrar tiempos en gt anteriores y posteriores a datos_t #
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
            # Borrar tiempo en datos_t anterior al ground truth #
            j = 0
            while datos_t[j] < gt_t2[0]:
                j += 1
            datos_t = datos_t[j:]
            for item in plot_items:
                item = item[j:]
            # Borrar el tiempo en gt_t posterior a datos_t
            j = 1
            while gt_t2[-j] > datos_t[-1]:
                #print("gt es {} y datos es {}".format(gt_t[-j], datos_t[-1]))
                j += 1
            gt_t2 = gt_t2[:-j+1] if j != 1 else gt_t
            gt_angulo2 = gt_angulo[:-j+1] if j != 1 else gt_angulo
            """
            
            # Mezclar ambos tiempos #
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
            # Generar objetos interpolables e interpolaciones (n_) #
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
            with open("analisis_errores_{}.txt".format(velocidad), 'a') as archivo_errores:
                print("\n####### ANALISIS VUELTA {} #######".format(indice))
                print("\n####### ANALISIS VUELTA {} #######".format(indice), file=archivo_errores)
                for item in n_items_interp:
                    # Calcular error absoluto y MSE #
                    item_mse = []
                    for i in range(len(new_time)):
                        item[i] = abs(item[i] - n_gt_interp[i])
                        item_mse.append(item[i]**2)
                    print("Error absoluto de {}: {}".format(toplot[n], np.mean(item)), file=archivo_errores)
                    print("Desviacion estandar de error de {}: {}".format(toplot[n], np.std(item)), file=archivo_errores)
                    print("MSE de {}: {}\n".format(toplot[n], np.mean(item_mse)), file=archivo_errores)
                    plt.plot(new_time, item, colores[n], label=toplot[n])
                    n += 1
            plt.xlim([new_time[0], new_time[-1]])
            plt.grid(True)
            plt.legend(loc='upper left')
            plt.title("Error absoluto medio en prueba {}, vuelta {}".format(velocidad[:-1]+"a", indice))
            plt.xlabel("Tiempo [s]")
            plt.ylabel("Error absoluto medio [º]")
            plt.savefig("plots/s{}_vuelta_{}.png".format(velocidad, indice))
            plt.clf()
            #plt.show()
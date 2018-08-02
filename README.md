# kalman
## mpu_bluetooth/
    Contiene los programas de Arduino utilizados para conectarse a la IMU y entregar los datos.

## MPU6050/ y SendOnlySoftwareSerial/
    Librerías parcialmente modificadas, necesarias para usar el Arduino
    
## analisis_errores.py
    Genera gráficos de error para cada vuelta, y calcula los errores totales.
    
## angulos_lento.csv y angulos_rapido.csv
    Ground truths de las pruebas lenta y rápida respectivamente. Los tiempos están desfasados.
    
## csv_analizer.py
    Genera gráficos y condensa datos a partir del ground truth y de las mediciones. Seguir instrucciones en pantalla.
    
## data_FINAL2_lento.csv y data_FINAL2_rapido.csv
    Mediciones obtenidas por el Arduino en las pruebas lenta y rápida respectivamente.
    
## datagetter.py
    Librería necesaria para usar imu_data_receive.py. Se conecta por bluetooth.
    
## imu_data_receive.py
    Programa para conectarse al Arduino y guardar los datos en formato csv.
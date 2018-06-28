# -*- coding: utf-8 -*-

import numpy as np

class Kalman:
    def __init__(self):
        # Variables ajustables
        self.Q_angle = 0.001
        self.Q_bias = 0.003
        self.R_measure = 0.03
        
        self.angle = 0.0
        self.bias = 0.0
        self.rate = 0.0
        
        self.P = np.array([[0.0, 0.0], [0.0, 0.0]])

    def get_angle(self, new_angle, new_rate, dt):
        # Paso 1, actualizar xgorro - prediccion de estado
        self.rate = new_rate - self.bias
        self.angle += dt * self.rate

        # Paso 2, actualizar covarianza de error - prediccion de covarianza
        self.P[0][0] += dt * (dt*self.P[1][1] - self.P[0][1] - self.P[1][0] + self.Q_angle)
        self.P[0][1] -= dt * self.P[1][1]
        self.P[1][0] -= dt * self.P[1][1]
        self.P[1][1] += self.Q_bias * dt

        # Paso 3, calcular diferencia de angulo
        y = new_angle - self.angle

        # Paso 4, estimar error
        S = self.P[0][0] + self.R_measure

        # Paso 5, calcular ganancia de Kalman
        K = [self.P[0][0] / S, self.P[1][0] / S]

        # Paso 6, calcular angulo y bias
        self.angle += K[0] * y
        self.bias += K[1] * y

        # Paso 7, actualizar covarianza del error
        P00_temp = self.P[0][0]
        P01_temp = self.P[0][1]

        self.P[0][0] -= K[0] * P00_temp
        self.P[0][1] -= K[0] * P01_temp
        self.P[1][0] -= K[1] * P00_temp
        self.P[1][1] -= K[1] * P01_temp

        return self.angle

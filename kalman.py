# -*- coding: utf-8 -*-

import numpy as np

class Kalman:
    def __init__(self):
        # Variables ajustables
        self.Q_angle = 0.001
        self.Q_bias = 0.003
        self.R_measure = 0.03
        
        self.angle = 0
        self.bias = 0
        
        self.P = np.array([[0, 0] [0, 0]])
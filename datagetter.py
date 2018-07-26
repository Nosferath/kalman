"""ax ay az gx gy gz temp"""

import serial
import io
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation as animation

class DataGetTxt:
    def __init__(self, args):
        pass
    
class DataGetSerial:
    def __init__(self, port='COM24', n=3):
        self.set_up(port, n)
        
    def set_up(self, port, n):
        self.n = n
        print("Conectando a puerto serial %s..."%(port))
        self.serial = serial.Serial(port, 9600, timeout=0.1)
        #self.sio =  io.TextIOWrapper(io.BufferedRandom(self.serial), encoding='ascii')
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.serial, self.serial))
        print("Conectado!")
        
    def loop_next(self):
        try:
            while True: 
                s = self.sio.readline().split('\t')
                print(s)
        except KeyboardInterrupt:
            self.serial.close()
            
    def get_next(self):
        s = self.sio.readline().split('\t')
        if len(s) == 1:
            return [0]*(self.n)
        return s
    
    def close(self):
        self.sio.close()
        self.serial.close()

class LivePlotter:
    def __init__(self, n, dt):
        self.n = n  # Datos maximos a almacenar en x e y
        self.dt = dt
        self.t = [0]*self.n
        self.y = [0]*self.n
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot(np.random.rand(10))
        self.ax.set_ylim(-180, 180)        
        self.dgs = DataGetSerial()
    
    def add_y(self, y):
        del self.y[0]
        del self.t[0]
        self.t.append(self.t[-1] + self.dt)
        self.y.append(y)
        
    def update(self, data):
        """No usado?"""
        self.line.set_ydata(data)
        return self.line,
    
    def run(self, y):
        self.add_y(y)
        self.line.set_data(self.t, self.y)
        return self.line,
        
    def data_gen(self):
        while True:
            try:
                y = self.dgs.get_next()
            except:
                y = 0
            yield y
                
if __name__ == "__main__":
    plt.ion()
    plotter = LivePlotter(1000, 0.01)
    ani = animation.FuncAnimation(plotter.fig, plotter.run, plotter.data_gen,
                                  interval=0, blit=True)
    while True:
        plt.show()
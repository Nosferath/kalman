"""ax ay az gx gy gz temp"""

import bluetooth


class DataGetTxt:
    def __init__(self, args):
        pass
    
class DataGetBt:
    def __init__(self, args=0):
        self.set_up(args)
        
    def set_up(self, args):
        port = 1
        print("Buscando dispositivos Bluetooth...")
        nearby_devices = bluetooth.discover_devices()
        num = 0
        print("Ingresa el numero del dispositivo a conectar:")
        for dev in nearby_devices:
            num += 1
            print(str(num), ": ", bluetooth.lookup_name(dev))
        selection = input("> ") - 1
        print("Has seleccionado", bluetooth.lookup_name(
                nearby_devices[selection]))
        selection = nearby_devices[selection]
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.connect((selection, port))
        
    def get_next(self):
        pass

getter = DataGetBt()
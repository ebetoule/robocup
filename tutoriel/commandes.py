import serial 
# Ouvrir le port série à travers l'USB (ajuster eventuellement l'identifiant du device):
s = serial.Serial(port='/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0', baudrate=115200)
# Les vitesses vont de -255 à 255
# Moteur gauche 100 vers l'avant
s.write(b'A100\n')
# Moteur Droit 100 vers l'arrière
s.write(b'B-100\n')
# Les deux à 0:
s.write(b'C0\n')
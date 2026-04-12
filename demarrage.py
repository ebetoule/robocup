import serial
import subprocess
import threading
import time
port = '/dev/ttyACM0'
en_marche = False
#script_a_lancer = "python3 /home/eloise/Documents/Informatique/Python/robocup/coucou.py"

def commencer():
    bouton_thread = threading.Thread(target=lecture, daemon=True)
    bouton_thread.start()

def lecture():
    global en_marche
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        while True:
            ligne = ser.readline().decode('utf-8').strip()
            if ligne == "A":
                print("Bouton pressé ! Lancement du programme...")
                en_marche = True
            if ligne == "B":
                print("Bouton pressé ! Arrêt du programme...")
                en_marche = False
    except KeyboardInterrupt:
        print("Arrêt du programme.")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == '__main__':
    commencer()
    while True:
        if en_marche:
            print('coucou')
            time.sleep(0.1)
        else:
            print('pas coucou')
            time.sleep(0.1)
            
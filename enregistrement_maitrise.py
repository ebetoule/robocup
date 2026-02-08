import cv2
import threading
import queue
import time
import buildhat
from buildhat import Motor
from picamera2 import Picamera2
from pynput import keyboard
from pynput.keyboard import Key

motor_right = Motor('A')
motor_left = Motor('B')
speed = 10
size = (640,480)

def tout_droit(speed):
    motor_right.start(speed)
    motor_left.start(-speed)

def gauche(speed):
    motor_right.start(speed)
    motor_left.start(speed)
    
def droite(speed):
    motor_right.start(-speed)
    motor_left.start(-speed)
    
def stop():
    motor_right.stop()
    motor_left.stop()

# Fonction pour le thread d'enregistrement
def recording_thread(q, nom, fps=15):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec efficace
    writer = cv2.VideoWriter(nom, fourcc, fps, size)#(width, height))
    print("debut de l'enregistrement")
    nframe = 0
    while True:
        nframe += 1
        frame = q.get()
        if frame is None:  # Signal de fin
            print(f"Arret de l'enregistrement apres {nframe} images")
            break
        # Resize pour réduire la taille (optionnel)
        #frame = cv2.resize(frame, (width, height))
        writer.write(frame)
    writer.release()

# Setup caméra Arducam (ajustez l'index si nécessaire)
def init_pycam():
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"size": size,"format": "RGB888"}, # scale down the image, but maintain the full field of view
        raw={'size': (3280, 2464)},
        buffer_count=2,
        #controls={'FrameRate': 50},
    )
    picam2.configure(config)#"preview")
    picam2.start()
    return picam2

def on_press(key):
    global keypressed
    if key == Key.left:
        print("à gauche")
        gauche(speed)
    if key == Key.right:
        print("à droite")
    if key == Key.up:
        print("en avant")
        tout_droit(speed)
    if key == Key.down:
        print("stop")
        stop()

# Queue pour passer les frames à enregistrer
frame_queue = queue.Queue(maxsize=10)  # Limite pour éviter surcharge

# Lance le thread d'enregistrement
rec_thread = threading.Thread(target=recording_thread, args=(frame_queue, 'test.mp4'))
rec_thread.start()

# Boucle principale : Capture, traitement, contrôle moteurs
picam2 = init_pycam()

# écoute les entrées clavier
listener = keyboard.Listener(on_press=on_press)
listener.start()

while True:

    frame = picam2.capture_array()
    # Passe une copie du frame à la queue pour enregistrement (sans bloquer)
    if not frame_queue.full():
        frame_queue.put(frame.copy())  # Copie pour éviter modification partagée

    if keypressed == Key.down:
        break()
    # Optionnel : Affichez pour debug (mais évitez si pas nécessaire, car ça ralentit)
    # cv2.imshow('Frame', frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# Fin : Signal au thread d'enregistrement
frame_queue.put(None)
rec_thread.join()
cv2.destroyAllWindows()
listener.stop()

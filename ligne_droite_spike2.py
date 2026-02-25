import cv2
import numpy as np
import time
from buildhat import Motor
from picamera2 import Picamera2
from pprint import *
import threading
import queue
from datetime import datetime

now = datetime.now()
filename = now.strftime("%m-%d-%Y_%H-%M-%S")+".mp4"
size = (1280,720)
#size = (640,480)
#size = (480, 270)
vitesse = 30
irow = -5
motor_right = Motor('A')
motor_left = Motor('B')
trajectoire = np.zeros((100))
fps = 15

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
    
    
def get_barycentre(frame, irow, seuil=50):
    """ renvoie le barycentre
    1. transforme en gris
    2. applique un seuil
    3. calcule la moyenne pondérée de la ligne irow
    """
    vid_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, tabimage = cv2.threshold(vid_gray, seuil, 255, cv2.THRESH_BINARY)
        
    dim_y, dim_x = tabimage.shape
    tabimage01 = tabimage.copy()
    tabimage01[tabimage==255] = 0
    tabimage01[tabimage==0] = 1
    sommew = np.sum(tabimage01[irow, :])
    if sommew == 0:
        return np.nan
    barycentre = np.average(np.arange(dim_x), weights=tabimage01[irow, :])
    return barycentre

def droit(vitesse):
    vitesse = max(vitesse, -100)
    vitesse = min(vitesse, 100)
    motor_right.start(vitesse)
    
def gauche(vitesse):
    vitesse = max(vitesse, -100)
    vitesse = min(vitesse, 100)
    motor_left.start(-vitesse)
    
def stop():
    motor_right.stop()
    motor_left.stop()
    
def avancer(vitesse):
    motor_right.start(vitesse)
    motor_left.start(-vitesse)
    
def courbe(trajectoire, index):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1,1)
    ax.plot(trajectoire)
    ax.axvline(x=index, color='r')
    plt.show()

def temps():
    temps = time.time()
    duree = temps - last
    last = temps
    print(duree * 1000)

def suivi(difference, barycentre, dernier, avant):
    if not np.isfinite(barycentre):
        print("perte de la ligne")
        stop()
        print(avant, dernier)
        if avant < dernier:
            gauche(vitesse)
        if avant > dernier:
            droit(vitesse)
    if difference == 0 :
        print("En avant")
        avancer(vitesse)
    if difference > 0 :
        print("à gauche")
        droit(vitesse)
        gauche(2 * vitesse / np.abs(difference))
    if difference < 0 :
        print("à droite")
        gauche(vitesse)
        droit(2 * vitesse / np.abs(difference))

picam2 = init_pycam()
last = 0
lecture = False
index = 0
frame_queue = queue.Queue(maxsize=10)  # Limite pour éviter surcharge

rec_thread = threading.Thread(target=recording_thread, args=(frame_queue, filename))
rec_thread.start()

try:
    while 1:
        frame = picam2.capture_array()
        dim_y, dim_x, _ = frame.shape
        centre = dim_x // 2
        barycentre = get_barycentre(frame, irow)
        if np.isfinite(barycentre):
            index = (index+1)%100
            trajectoire[index] = barycentre
        difference = (centre - barycentre)
        barint = int(barycentre) if np.isfinite(barycentre) else -1
        if lecture:
            cv2.circle(frame, (barint, dim_y+irow), 20, (0, 0, 255), -1) 
            cv2.imshow('frame', frame)
            key = cv2.waitKey(20)
            if key == ord('q'):
                stop()
                break
        else:
            suivi(difference, barycentre, trajectoire[index], trajectoire[index - 1])
        if not frame_queue.full():
            frame_queue.put(frame.copy())

except KeyboardInterrupt:
    stop()
    frame_queue.put(None)
    rec_thread.join()
frame_queue.put(None)
rec_thread.join()
cv2.destroyAllWindows()
stop()
import cv2
import numpy as np
import time
from buildhat import Motor
from picamera2 import Picamera2
from pprint import *
#size = (1280,720)
size = (640,480)
#size = (480, 270)
vitesse = 30
irow = -5
motor_right = Motor('B')
motor_left = Motor('A')
trajectoire = []
def init_pycam():
    picam2 = Picamera2()
    #qpprint(picam2.sensor_modes)
    config = picam2.create_still_configuration(
        main={"size": size,"format": "RGB888"}, # scale down the image, but maintain the full field of view
        raw={'size': (3280, 2464)},
        buffer_count=2,
        #controls={'FrameRate': 50},
    )
    picam2.configure(config)#"preview")
    picam2.start()
    return picam2


def get_barycentre(frame, irow, seuil=50):
    """ renvoie le barycentre
    1. transforme en gris
    2. applique un seuil
    3. calcule la moyenne pondérée de la ligne -10
    """
    vid_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, tabimage = cv2.threshold(vid_gray, seuil, 255, cv2.THRESH_BINARY)
        
    dim_y, dim_x = tabimage.shape
    #print(dim_y)

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
    #print("droit", vitesse)
    motor_right.start(vitesse)
    
def gauche(vitesse):
    vitesse = max(vitesse, -100)
    vitesse = min(vitesse, 100)
    #print("gauche", -vitesse)
    motor_left.start(-vitesse)
    
def stop():
    motor_right.stop()
    motor_left.stop()
    
def avancer(vitesse):
    motor_right.start(vitesse)
    motor_left.start(-vitesse)

def suivi(difference, barycentre):
    if not np.isfinite(barycentre):
        print("perte de la ligne")
        #barycentre = centre
        stop()
    barint = int(barycentre)
    if difference == 0 :
        #print('En avant')
        avancer(vitesse)
    if difference > 0 :
        #print('à gauche')
        droit(vitesse)
        gauche(2 * vitesse / np.abs(difference))
    if difference < 0 :
        #print('à droite')
        gauche(vitesse)
        droit(2 * vitesse / np.abs(difference))
    return barint

picam2 = init_pycam()
last = 0
lecture = False
try:
    while 1:#(video.isOpened()):
  # lire chaque image une par une
    #ret, frame = video.read()
        frame = picam2.capture_array()

        #temps = time.time()
        #duree = temps - last
        #last = temps
        #print(duree * 1000)
        dim_y, dim_x, _ = frame.shape
        centre = dim_x // 2
        barycentre = get_barycentre(frame, irow)
        trajectoire.append(barycentre)
        if not np.isfinite(barycentre):
            print("perte de la ligne")
            stop()
            dernier = trajectoire[-1]
            avant = trajectoire[-4]
            while np.isfinite(barycentre):
                if avant < dernier :
                    gauche(vitesse)
                else:
                    droite(vitesse)
        difference = (centre - barycentre)
        if lecture:
            #cv2.circle(frame, (barint, dim_y+irow), 20, (0, 0, 255), -1) 
            cv2.imshow('frame', frame)
            key = cv2.waitKey(20)
            if key == ord('q'):
                stop()
                break
        else:
            barint = suivi(difference, barycentre)
        
        #cv2.circle(frame, (barint, dim_y+irow), 20, (0, 0, 255), -1) 
        #cv2.imshow('frame', frame)
        #key = cv2.waitKey(20)
        #if key == ord('q'):
            #stop()
            #break

except KeyboardInterrupt:
    stop()
cv2.destroyAllWindows()
stop()
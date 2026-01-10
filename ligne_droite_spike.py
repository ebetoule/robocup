import cv2
import numpy as np
import time
from buildhat import Motor
from picamera2 import Picamera2
#size = (1280,720)
size = (640,480)
vitesse = 40
motor_right = Motor('B')
motor_left = Motor('A')

def init_pycam():
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = size#(1280,720)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()
    return picam2


#video = cv2.VideoCapture(0)


def get_barycentre(frame, irow=-10, seuil=50):
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
    
    barycentre = 0
    denominateur = 0
    for i in range(dim_x):
        barycentre = barycentre + float(i) * tabimage01[irow,i]
        denominateur = denominateur + tabimage01[irow,i]
    barycentre = barycentre / denominateur
    return barycentre

def droite(vitesse):
    motor_right.stop()
    motor_left.start(-vitesse)
    
def gauche(vitesse):
    motor_right.start(vitesse)
    motor_left.stop()
    
def stop():
    motor_right.stop()
    motor_left.stop()
    
def avancer(vitesse):
    motor_right.start(vitesse)
    motor_left.start(-vitesse)

picam2 = init_pycam()
last = 0
while 1:#(video.isOpened()):
  # lire chaque image une par une
    #ret, frame = video.read()
    frame = picam2.capture_array()
    
    if True:
        temps = time.time()
        duree = temps - last
        last = temps
        print(duree)
        #frame = cv2.rotate(frame, cv2.ROTATE_180)
        irow = -10
        dim_y, dim_x, _ = frame.shape
        centre = dim_x // 2
    
        barycentre = get_barycentre(frame, irow=irow)
        if not np.isfinite(barycentre):
            print("perte de la ligne")
            barycentre = centre
            print('STOP')
            stop()
        barint = int(barycentre)
        if barint == centre :
            print('En avant')
            avancer(vitesse)
        if barint > centre :
            print('à gauche')
            droite(vitesse)
        if barint < centre :
            print('à droite')
            gauche(vitesse)
        
        cv2.circle(frame, (barint, dim_y+irow), 20, (0, 0, 255), -1) 
        #cv2.imshow('frame', frame)
        key = cv2.waitKey(20)
        if key == ord('q'):
            stop()
            break
    else:
        break

cv2.destroyAllWindows()
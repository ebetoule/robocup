import cv2
import numpy as np
#video = cv2.VideoCapture(0)

from picamera2 import Picamera2

#size = (640,480)
size = (1280, 720)

def init_pycam():
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = size#(1280,720)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()
    return picam2

def get_barycentre(frame, irow=-10):
    """ renvoie le barycentre
    1. transforme en gris
    2. applique un seuil
    3. calcule la moyenne pondérée de la ligne -10
    """
    vid_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, tabimage = cv2.threshold(vid_gray, 50, 255, cv2.THRESH_BINARY)
        
    dim_y, dim_x = tabimage.shape
    #print(dim_y)

    tabimage01 = tabimage.copy()
    tabimage01[tabimage==255] = 0
    tabimage01[tabimage==0] = 1
    
    ligne = tabimage01[irow]
    barycentre = np.mean(ligne)
    print (barycentre)
    return barycentre

picam2 = init_pycam()

while 1:#(video.isOpened()):
  # lire chaque image une par une
    #ret, frame = video.read()
    frame = picam2.capture_array()
    
    if True:
        #frame = cv2.rotate(frame, cv2.ROTATE_180)
        irow = -10
        dim_y, dim_x, _ = frame.shape
        centre = dim_x // 2

        barycentre = get_barycentre(frame, irow=irow)
        if not np.isfinite(barycentre):
            print("perte de la ligne")
            barycentre = centre
        barint = int(barycentre)
        cv2.circle(frame, (barint, dim_y+irow), 20, (0, 0, 255), -1) 
        cv2.imshow('frame', frame)
        key = cv2.waitKey(20)
        if key == ord('q'):
            break
    else:
        break
    
cv2.destroyAllWindows()
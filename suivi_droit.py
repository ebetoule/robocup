import cv2
import numpy as np
import serial

s = serial.Serial(port='/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0', baudrate=115200)
video = cv2.VideoCapture(0)


def get_barycentre(frame, irow=-10):
    """ renvoie le barycentre
    1. transforme en gris
    2. applique un seuil
    3. calcule la moyenne pondérée de la ligne -10
    """
    vid_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, tabimage = cv2.threshold(vid_gray, 50, 255, cv2.THRESH_BINARY)
        
    dim_y, dim_x = tabimage.shape
    print(dim_y)

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


while(video.isOpened()):
  # lire chaque image une par une
    cv2.rotate()
    ret, frame = video.read()
    irow = -10
    dim_y, dim_x, _ = frame.shape
    centre = dim_x // 2
    if ret == True:
        barycentre = get_barycentre(frame, irow=irow)
        if not np.isfinite(barycentre):
            print("perte de la ligne")
            barycentre = centre
            print('STOP')
            s.write(b'C0\n')
        barint = int(barycentre)
        if barint == centre :
            print('En avant')
            s.write(b'C30\n')
        if barint > centre :
            print('à gauche')
            s.write(b'A0\n')
            s.write(b'B30\n')
        if barint < centre :
            print('à droite')
            s.write(b'A30\n')
            s.write(b'B0\n')
        
        #cv2.circle(frame, (barint, dim_y+irow), 20, (0, 0, 255), -1) 
        #cv2.imshow('frame', frame)
        key = cv2.waitKey(20)
        if key == ord('q'):
            s.write(b'C0\n')
            break
    else:
        break
    
.release()
cv2.destroyAllWindows()
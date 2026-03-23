import cv2
import numpy as np
import time
#from buildhat import Motor
from picamera2 import Picamera2
from pprint import *
import threading
import queue
from datetime import datetime
import camera
from intersections import get_barycentre, centre_inter, detectligne, intersection, segment2rtheta, groupir, deuxun, centers2lines
from deplacements_robot import avancer, gauche, droit, stop, tourner, aller
#import click_and_go as cg
from enregistrement import recording_thread


now = datetime.now()
filename = now.strftime("%m-%d-%Y_%H-%M-%S")+".mp4"
#size = (1280,720)
size = (640,480)
#size = (480, 270)
vitesse = 20
irow = -5
#motor_right = Motor('A')
#motor_left = Motor('B')
trajectoire = np.zeros((100))
fps = 15

    
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

if __name__ == '__main__':
    picam2 = camera.init_pycam()
    last = 0
    running = True
    lecture = False
    write = False
    index = 0
    if write:
        frame_queue = queue.Queue(maxsize=10)  # Limite pour éviter surcharge
        rec_thread = threading.Thread(target=recording_thread, args=(frame_queue, filename))
        rec_thread.start()
    frame = picam2.capture_array()
    try:
        while running:
            frame = picam2.capture_array()
            dim_y, dim_x, _ = frame.shape
            centre = dim_x // 2
            barycentre = get_barycentre(frame, irow)
            if np.isfinite(barycentre):
                index = (index+1)%100
                trajectoire[index] = barycentre
            difference = (centre - barycentre)
            barint = int(barycentre) if np.isfinite(barycentre) else -1
            cdstP, linesP = intersection(frame, False)
            thetacenters, rcenters, theta3, nblignes = groupir(linesP)
            if nblignes == 2:
                print("intersection trouvée !!!")
                x1, y1 = centre_inter(thetacenters, rcenters)
                theta1 = np.arctan2(x1, y1)
                theta1 = np.degrees(theta1)
                dist = np.sqrt(x1**2 + y1**2)
                tourner(-theta1)
                aller(dist)
                tourner(90)
            #suivi(difference, barycentre, trajectoire[index], trajectoire[index - 1])
            if lecture:
                cv2.circle(frame, (barint, dim_y+irow), 20, (0, 0, 255), -1) 
                cv2.imshow('frame', frame)
                key = cv2.waitKey(20)
                if key == ord('q'):
                    stop()
                    break
            if write and not frame_queue.full():
                frame_queue.put(frame.copy())

    except KeyboardInterrupt:
        #stop()
        #frame_queue.put(None)
        #rec_thread.join()
        running = False
    if write:
        frame_queue.put(None)
    #rec_thread.join()
    cv2.destroyAllWindows()
    stop()

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
from deplacements_robot import avancer, gauche, droit, stop, tourner, aller, motor_left, motor_right
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

def passage_inter(thetacenters, rcenters):
    #Prend l'état renvoyé par détection inter et effectue la marche à suivre puis revient en suivi
    x1, y1 = centre_inter(thetacenters, rcenters)
    theta1 = np.arctan2(x1, y1)
    theta1 = np.degrees(theta1)
    dist = np.sqrt(x1**2 + y1**2)
    print(f'tourner de {theta1}, avancer de {dist}')
    tourner(-theta1)
    aller(dist)
    tourner(90)

def normal(frame):
    global index, trajectoire
    #Se met en suivi normal et surveille l'apparition d'intersections ou d'obstacles
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
        passage_inter(thetacenters, rcenters)
        return 'intersection'
    else:
        suivi(difference, barycentre, trajectoire[index], trajectoire[index - 1])
        return 'normal'
    
def gestion_intersection(frame):
    #Lorsqu'on obtient l'intersection, vérifie de quel côté on doit tourner(vert ou ligne devant)
#     speed1 = motor_left.get_speed()
#     speed2 = motor_right.get_speed()
#     print(f'vitesses = {speed1}, {speed2}')
#     if speed1 == 0 and speed2 == 0:
#         return 'normal'
#     else:
#         return 'intersection'
    return 'normal'

if __name__ == '__main__':
    picam2 = camera.init_pycam()
    last = 0
    running = True
    lecture = False
    write = False
    index = 0
    etat_courant = 'normal'
    etats  = {'normal' : normal,
             'intersection' : gestion_intersection}
    if write:
        frame_queue = queue.Queue(maxsize=10)  # Limite pour éviter surcharge
        rec_thread = threading.Thread(target=recording_thread, args=(frame_queue, filename))
        rec_thread.start()
    frame = picam2.capture_array()
    try:
        while running:
            frame = picam2.capture_array()
            etat_courant = etats[etat_courant](frame)
            print(f"Etat : {etat_courant}")
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
        print("on est partis !!!!")
        #stop()
        #frame_queue.put(None)
        #rec_thread.join()
        pass
    if write:
        frame_queue.put(None)
    #rec_thread.join()
    cv2.destroyAllWindows()
    stop()

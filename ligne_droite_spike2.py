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
import click_and_go as cg


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

def passage_inter(thetacenters, rcenters, x1, y1):
    #Prend l'état renvoyé par détection inter et effectue la marche à suivre puis revient en suivi
    print('centre trouvé!')
    x, y = cg.image2damier(x1, y1)
    print('centre converti!')
    theta1 = np.arctan2(x, y)
    theta1 = np.degrees(theta1)
    dist = np.sqrt(x**2 + y**2)
    print(f'tourner de {theta1}')
    tourner(-theta1)
    print(f'avancer de {dist}')
    aller(dist)
    print('tourner de 90')
    tourner(90)
    print('fini!!!')

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
    imgline, linesP = intersection(frame, True)
    if linesP is not None:
        thetacenters, rcenters, theta3, nblignes = groupir(linesP)
        if nblignes == 2:
            print('intersection détecté!')
            x1, y1 = centre_inter(thetacenters, rcenters)
            cv2.circle(imgline, (int(x1), int(y1)), 30, (255,0,0), -1)
            pt1, pt2, pt3, pt4 = centers2lines(thetacenters, rcenters, 2)
            cv2.line(imgline, pt1, pt2, (0,255,255), 3, cv2.LINE_AA)
            cv2.line(imgline, pt3, pt4, (0,255,255), 3, cv2.LINE_AA)
            #passage_inter(thetacenters, rcenters, x1, y1)
            return 'intersection', imgline
        else:
            #suivi(difference, barycentre, trajectoire[index], trajectoire[index - 1])
            if barint != -1:
                pt1, pt2, _, _ = centers2lines(thetacenters, rcenters, 1)
                cv2.line(imgline, pt1, pt2, (0,255,255), 3, cv2.LINE_AA)
                cv2.circle(imgline, (int(barycentre), 475), 10, (0,0,255), -1)
                return 'normal', imgline
            else:
                return 'normal', imgline
    else:
        #suivi(difference, barycentre, trajectoire[index], trajectoire[index - 1])
        return 'normal', imgline
    
def gestion_intersection(frame):
    #Lorsqu'on obtient l'intersection, vérifie de quel côté on doit tourner(vert ou ligne devant)
    speed1 = motor_left.get_speed()
    speed2 = motor_right.get_speed()
    print(f'vitesses = {speed1}, {speed2}')
    if speed1 == 0 and speed2 == 0:
        return 'normal', _
    else:
        return 'intersection', _
    #return 'normal'

if __name__ == '__main__':
    picam2 = camera.init_pycam()
    last = 0
    running = True
    lecture = False
    write = True
    index = 0
    etat_courant = 'normal'
    etats  = {'normal' : normal,
             'intersection' : gestion_intersection}
    if write:
        frame_queue = queue.Queue(maxsize=10)  # Limite pour éviter surcharge
        rec_thread = threading.Thread(target=recording_thread, args=(frame_queue, filename, 15, (640*2, 480)))
        rec_thread.start()
    frame = picam2.capture_array()
    try:
        while running:
            frame = picam2.capture_array()
            etat_courant, _ = etats[etat_courant](frame)
            print(f"Etat : {etat_courant}")
            _, imgline = normal(frame)
            if lecture:
                cv2.circle(frame, (barint, dim_y+irow), 20, (0, 0, 255), -1) 
                cv2.imshow('frame', frame)
                key = cv2.waitKey(20)
                if key == ord('q'):
                    stop()
                    break
            if write and not frame_queue.full():
                frame_queue.put(np.hstack([imgline, frame]))
                

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

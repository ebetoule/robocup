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
import intersections as inter
import analyse
import deplacements_robot as dr
import enregistrement
import click_and_go as cg

lock = threading.Lock()

trajectoire = np.zeros((100))
vitesse = 0.45
intersection = False
detection_intersection = True

def commencer():
    ana_thread = threading.Thread(target=detecter)
    ana_thread.start()

def detecter():
    global intersection, frame
    while detection_intersection:
        with lock:
            framecopy = frame.copy()
        theta3, x, y, _, _, _ = inter.detect_inter(framecopy)
        #print(theta3)
        #time.sleep(0.05)
        #contours, mask, carre = analyse.detectcarre(framecopy)
        if theta3 is not None:
            intersection = True
            print('peut-être')
        else:
            intersection = False
            print("on a pas d'intersection")

def temps():
    global last
    temps = time.time()
    duree = temps - last
    last = temps
    #print(f'{duree * 1000:.2f} ms')# en milliseconde
    return duree * 1000

    
def suivi(barycentre, dernier, avant):
    difference = 640 / 2 - barycentre
    if not np.isfinite(barycentre):
        print("perte de la ligne")
        #dr.stop()
        #print(avant, dernier)
        if avant < dernier:
            dr.droit(-vitesse)
            dr.gauche(vitesse)
        if avant > dernier:
            dr.droit(vitesse)
            dr.gauche(-vitesse)
    if difference >= 0 :
        #print("à gauche")
        dr.droit(vitesse)
        dr.gauche(vitesse + (-2 * vitesse/320)*difference)
    if difference < 0 :
        #print("à droite")
        dr.gauche(vitesse)
        dr.droit(vitesse + (2 * vitesse/320)*difference)
    
if __name__ == '__main__':
    picam2 = camera.init_pycam()#initialisation de la caméra 
    write = True
    durees_execution = []
    running = True#écriture de film 
    index = 0# obtention du dernier barycentre donnée stocké dans le tableau trajectoire
    frame = picam2.capture_array()
    if write:
        enregistrement.demarrer(size=(640, 480))# démarrer l'écriture du film
    commencer()
    last = time.time()
    try:
        while running:
            durees_execution.append(temps())
            with lock:
                frame = picam2.capture_array() #prise de l'image qui va être traitée
            barycentre = inter.get_barycentre(frame, -5)
            if np.isfinite(barycentre):
                index = (index+1)%100
                trajectoire[index] = barycentre
            suivi(barycentre, trajectoire[index], trajectoire[index - 1])
            if intersection:
                dr.stop()
                resultat = inter.gestion_intersection(frame)
                if resultat is not None:
                    p1 = resultat['centre']
                    p2 = resultat['direction finale'][0]
                    print('intersection détecter!')
                    print(f'{p1=},{p2=}')
                    cg.go(p1, p2)
                else:
                    pass
            if write:
                enregistrement.ajouter(frame)#ajouter l'image dans le film
    except KeyboardInterrupt:
        print("on est partis !!!!")
        pass
    
    finally:
        enregistrement.stop()
        detection_intersection = False
        dr.stop()
        print(f'moyenne:{np.mean(np.array(durees_execution)[1:]):.2f},max:{np.max(np.array(durees_execution)[1:]):.2f}, min:{np.min(np.array(durees_execution)[1:]):.2f}')
        picam2.close()
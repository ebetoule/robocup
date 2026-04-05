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
import intersections
import analyse
from intersections import get_barycentre
import deplacements_robot as dr
import enregistrement
last = 0

trajectoire = np.zeros((100))
vitesse = 0.5
intersection = False
detection_intersection = True

def commencer():
    ana_thread = threading.Thread(target=detecter)
    ana_thread.start()

def detecter():
    global intersection, frame
    while detection_intersection:
        contours, frame, carre = analyse.detectcarre(frame)
        if len(carre) > 0:
            intersection = True
            print('on a une intersection!')
        else:
            intersection = False
            print("on a pas d'intersection")
def temps():
    global last
    temps = time.time()
    duree = temps - last
    last = temps
    #print(f'{duree * 1000:.2f} ms')# en milliseconde

    
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
    running = True#écriture de film 
    index = 0# obtention du dernier barycentre donnée stocké dans le tableau trajectoire
    frame = picam2.capture_array()
    if write:
        enregistrement.demarrer(size=(640, 480))# démarrer l'écriture du film
    commencer()
    try:
        while running:
            temps()
            frame = picam2.capture_array() #prise de l'image qui va être traitée
            barycentre = get_barycentre(frame, -5)
            if np.isfinite(barycentre):
                index = (index+1)%100
                trajectoire[index] = barycentre
            suivi(barycentre, trajectoire[index], trajectoire[index - 1])
            if intersection:
                print('intersection détecter!')
                break
            if write:
                enregistrement.ajouter(frame)#ajouter l'image dans le film
    except KeyboardInterrupt:
        print("on est partis !!!!")
        pass
    
    finally:
        enregistrement.stop()
        detection_intersection = False
        dr.stop()
        picam2.close()
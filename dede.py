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
from intersections import get_barycentre
import deplacements_robot as dr
import enregistrement
last = 0

trajectoire = np.zeros((100))
vitesse = 20

def temps():
    global last
    temps = time.time()
    duree = temps - last
    last = temps
    print(f'{duree * 1000:.2f} ms')# en milliseconde

    
def suivi(barycentre, dernier, avant):
    difference = 640 / 2 - barycentre
    if not np.isfinite(barycentre):
        print("perte de la ligne")
        #dr.stop()
        print(avant, dernier)
        if avant < dernier:
            dr.gauche(vitesse)
        if avant > dernier:
            dr.droit(vitesse)
    if difference == 0 :
        print("En avant")
        dr.avancer(vitesse)
    if difference > 0 :
        print("à gauche")
        dr.droit(vitesse)
        dr.gauche(2 * vitesse / np.abs(difference))
    if difference < 0 :
        print("à droite")
        dr.gauche(vitesse)
        dr.droit(2 * vitesse / np.abs(difference))
    
if __name__ == '__main__':
    picam2 = camera.init_pycam()#initialisation de la caméra 
    write = True
    running = True#écriture de film 
    index = 0 # obtention du dernier barycentre donnée stocké dans le tableau trajectoire
    if write:
        enregistrement.demarrer(size=(640, 480))# démarrer l'écriture du film
    try:
        while running:
            temps()
            frame = picam2.capture_array() #prise de l'image qui va être traitée
            barycentre = get_barycentre(frame, -5)
            if np.isfinite(barycentre):
                index = (index+1)%100
                trajectoire[index] = barycentre
            suivi(barycentre, trajectoire[index], trajectoire[index - 1])
            if write:
                enregistrement.ajouter(frame)#ajouter l'image dans le film
    except KeyboardInterrupt:
        print("on est partis !!!!")
        pass
    
    finally:
        enregistrement.stop()
        dr.stop()
        picam2.close()
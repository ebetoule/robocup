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
import demarrage
from buildhat import DistanceSensor

lock = threading.Lock()

#vitesse = 0.4
dist = DistanceSensor('D', threshold_distance=100)
vitesse = 180
intersection = False
detection_intersection = True
fin = False
obstacle = False
zone = False

def detect_obstacle():
    global obstacle
    distance = dist.get_distance()
    #print('distance', distance)
    if distance == -1:
        obstacle = False
    elif distance <= 50:
        obstacle = True
    else:
        obstacle = False
    
def detect_zone(frame):
    global zone
    aire, cx, cy, _ = analyse.entree(frame)
    #print(aire, cy)
    if aire is not None:
        if aire > 25 and aire < 40 and cy > 200:
            zone = True
        else:
            zone = False

def commencer():
    global detection_intersection
    detection_intersection = True
    ana_thread = threading.Thread(target=detecter, daemon=True)
    ana_thread.start()
    
def detecter():
    global intersection, frame, fin
    while detection_intersection:
        with lock:
            framecopy = frame.copy()
        hsv = cv2.cvtColor(framecopy, cv2.COLOR_BGR2HSV)
        fin1 = analyse.detectfin(hsv)
        if fin1 is not None and fin1[1] > 300 :
            #print('fin detectée')
                fin = True
        theta3, x, y, _, _, _ = inter.detect_inter(hsv)
        #print(theta3)
        #time.sleep(0.05)
        #contours, mask, carre = analyse.detectcarre(framecopy)
        if theta3 is not None:
            intersection = True
            #print('peut-être')
        else:
            intersection = False
            #print("on a pas d'intersection")
        detect_zone(hsv)

def temps():
    global last
    temps = time.time()
    duree = temps - last
    last = temps
    #print(f'{duree * 1000:.2f} ms')# en milliseconde
    return duree * 1000

def perte_de_la_ligne(frame, etat_courant):
    print('recherche de pointillés')
    dernier = etat_courant['barycentre']
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    ligne = analyse.ligne_droite(hsv)
    if ligne is not None :
        p1, p2 = ligne
        #print(f'{p1=},{p2=}')
        cg.go(p1, p2)
        etat_courant['etat'] = 'suivi'
        return etat_courant
    etat_courant['etat'] = 'recherche'
    return etat_courant

def sorti():
    sorti = False
    with lock:
        frame = picam2.capture_array()
    ligne = analyse.ligne_droite(frame)
    sorti = False
    while not sorti:
        if ligne is not None :
            p1, p2 = ligne
            #print(f'{p1=},{p2=}')
            cg.go(p1, p2)
            sorti = True
        else:
            dr.tourner(5)
            sorti = False
        
def recherche(frame, etat_courant):
    print('recherche de ligne')
    barycentre = inter.get_barycentre(frame, -5)
    if np.isfinite(barycentre):
        print('ligne retrouvée')
        etat_courant['etat'] = 'suivi'
        return etat_courant
    avant = etat_courant['précédent']
    dernier = etat_courant['barycentre']
    pas = 10
    if avant < dernier:
        #print('à gauche')
        if etat_courant['tour'] == 0:
            #print('tour 0')
            dr.tourner(-pas)
            etat_courant['angle recherche'] = etat_courant['angle recherche'] + (-pas)
            if etat_courant['angle recherche'] < -90:
                etat_courant['tour'] = 1
        else:
            #print('tour 1')
            dr.tourner(pas)
            etat_courant['angle recherche'] = etat_courant['angle recherche'] + pas
            if etat_courant['angle recherche'] > 90:
                etat_courant['tour'] = 0
    else:
        #print('à droite')
        if etat_courant['tour'] == 0:
            #print('tour 0')
            dr.tourner(pas)
            etat_courant['angle recherche'] = etat_courant['angle recherche'] + pas
            if etat_courant['angle recherche'] > 90:
                etat_courant['tour'] = 1
        else:
            #print('tour 1')
            dr.tourner(-pas)
            etat_courant['angle recherche'] = etat_courant['angle recherche'] + (-pas)
            if etat_courant['angle recherche'] < -90:
                etat_courant['tour'] = 0
                
    etat_courant['etat'] = 'recherche'
    return etat_courant
    
def suivi(frame, etat_courant):
    barycentre = inter.get_barycentre(frame, -5)
    if not np.isfinite(barycentre):
        etat_courant['etat'] = 'perte de la ligne'
        return etat_courant
    etat_courant['précédent'] = etat_courant['barycentre']
    etat_courant['barycentre'] = barycentre

    difference = 640 / 2 - barycentre
    if difference >= 0 :
        #print("à gauche")
        dr.droit(vitesse)
        dr.gauche(vitesse + (-2 * vitesse/200)*difference)
    if difference < 0 :
        #print("à droite")
        dr.gauche(vitesse)
        dr.droit(vitesse + (2 * vitesse/200)*difference)
    return etat_courant

etats = {'suivi' : suivi,
         'perte de la ligne': perte_de_la_ligne,
         'recherche' : recherche,
         'sorti' : sorti,
         }
    
def main():
    global last, frame, fin, detection_intersection, obstacle
    picam2 = camera.init_pycam()#initialisation de la caméra
    write = True
    fin = False
    durees_execution = []
    running = True
    nbfois = 0
    etat_courant = {'barycentre' : 320,
                    'précédent' : 320,
                    'etat' : 'suivi',
                    'angle recherche': 0,
                    'tour' : 0,
                    }
    for i in range(10):
        frame = picam2.capture_array()

    if write:
        enregistrement.demarrer(size=(640, 480))# démarrer l'écriture du film
    dr.demarrer()
    commencer()
    last = time.time()
    try:
        while demarrage.en_marche:
            durees_execution.append(temps())
            with lock:
                frame = picam2.capture_array()#prise de l'image qui va être traitée
            etat_courant = etats[etat_courant['etat']](frame, etat_courant)
            detect_obstacle()
            framecopy = frame.copy()
            hsv = cv2.cvtColor(framecopy, cv2.COLOR_BGR2HSV)
            if obstacle:
                print('obstacle détecté')
                dr.passage_obstacle()
            if zone:
                print('entrée dans la zone')
                aire, cx, cy, _ = analyse.entree(hsv)
                p1 = cx, cy
                p2 = p1
                cg.go(p1, p2)
                print(p1, p2)
                sorti()
                demarrage.en_marche = False
                break
            if fin:
                print('fin du parcours')
                p1 = analyse.detectfin(hsv)
                p2 = p1
                cg.go(p1, p2)
                demarrage.en_marche = False
                fin = False
                break
            if intersection:
                #dr.stop()
                dr.avancer(0)
                resultat = inter.gestion_intersection(hsv)
                if resultat is not None:
                    p1 = resultat['centre']
                    p2 = resultat['direction finale'][0]
                    print('intersection détectée!')
                    cg.go(p1, p2)
                    #remettre en suivi
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
        if len(durees_execution) > 1:
            print(f'moyenne:{np.mean(np.array(durees_execution)[1:]):.2f},max:{np.max(np.array(durees_execution)[1:]):.2f}, min:{np.min(np.array(durees_execution)[1:]):.2f}')
        picam2.close()

if __name__ == '__main__':
    demarrage.commencer()
    while True:
        if demarrage.en_marche:
            main()
        else:
            time.sleep(0.1)

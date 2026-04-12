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

lock = threading.Lock()

vitesse = 0.4
intersection = False
fin = False
detection_intersection = True

def commencer():
    ana_thread = threading.Thread(target=detecter)
    ana_thread.start()

def detecter():
    global intersection, frame, fin
    while detection_intersection:
        with lock:
            framecopy = frame.copy()
        fin1 = analyse.detectfin(framecopy)
        if fin1 is not None and fin1[1] > 300: 
            fin = True
        theta3, x, y, _, _, _ = inter.detect_inter(framecopy)
        #print(theta3)
        #time.sleep(0.05)
        #contours, mask, carre = analyse.detectcarre(framecopy)
        if theta3 is not None:
            intersection = True
            #print('peut-être')
        else:
            intersection = False
            #print("on a pas d'intersection")

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
    ligne = analyse.ligne_droite(frame)
    if ligne is not None :
        b2 = inter.get_barycentre(frame, ligne[1])
        y = ligne[1]
        if b2 is not None:
            diff = b2 - dernier
            x1, y1 = cg.image2damier(b2, y)
            angle = np.arctan(x1, y1)
            if diff > -10 and diff < 10:
                cg.go((b2, y), (b2, y))
                etat_courant['etat'] = 'suivi'
                return etat_courant
    etat_courant['etat'] = 'recherche'
    return etat_courant

def recherche(frame, etat_courant):
    print('recherche de ligne')
    barycentre = inter.get_barycentre(frame, -5)
    if np.isfinite(barycentre):
        print('ligne retrouvée')
        etat_courant['etat'] = 'suivi'
        return etat_courant
    avant = etat_courant['précédent']
    dernier = etat_courant['barycentre']
    if avant < dernier:
        print('à gauche')
        if etat_courant['tour'] == 0:
            print('tour 0')
            dr.tourner(-25)
            etat_courant['angle recherche'] = etat_courant['angle recherche'] + (-25)
            if etat_courant['angle recherche'] < -90:
                etat_courant['angle recherche'] = 0
                etat_courant['tour'] = 1
        else:
            print('tour 1')
            dr.tourner(25)
            etat_courant['angle recherche'] = etat_courant['angle recherche'] + 25
            if etat_courant['angle recherche'] < 90:
                etat_courant['angle recherche'] = 0
                etat_courant['tour'] = 0
    else:
        print('à droite')
        if etat_courant['tour'] == 0:
            print('tour 0')
            dr.tourner(25)
            etat_courant['angle recherche'] = etat_courant['angle recherche'] + 25
            if etat_courant['angle recherche'] < 90:
                etat_courant['angle recherche'] = 0
                etat_courant['tour'] = 1
        else:
            print('tour 1')
            dr.tourner(-25)
            etat_courant['angle recherche'] = etat_courant['angle recherche'] + (-25)
            if etat_courant['angle recherche'] < -90:
                etat_courant['angle recherche'] = 0 
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
#         print('toujours perte de la ligne, on retourne')
#         if avant < dernier:
#             dr.tourner(180)
#         elif avant > dernier:
#             dr.tourner(-180)
#         nbfois == 0
    difference = 640 / 2 - barycentre
    if difference >= 0 :
        #print("à gauche")
        dr.droit(vitesse)
        dr.gauche(vitesse + (-2 * vitesse/320)*difference)
    if difference < 0 :
        #print("à droite")
        dr.gauche(vitesse)
        dr.droit(vitesse + (2 * vitesse/320)*difference)
    return etat_courant

etats = {'suivi' : suivi,
         'perte de la ligne': perte_de_la_ligne,
         'recherche' : recherche,
         }
    
def main():
    global last, frame
    picam2 = camera.init_pycam()#initialisation de la caméra 
    write = True
    durees_execution = []
    running = True
    nbfois = 0
    etat_courant = {'barycentre' : 320,
                    'précédent' : 320,
                    'etat' : 'suivi',
                    'angle recherche': 0,
                    'tour' : 0,
                    }
    frame = picam2.capture_array()
    if write:
        enregistrement.demarrer(size=(640, 480))# démarrer l'écriture du film
    commencer()
    last = time.time()
    try:
        while demarrage.en_marche:
            durees_execution.append(temps())
            with lock:
                frame = picam2.capture_array() #prise de l'image qui va être traitée
            etat_courant = etats[etat_courant['etat']](frame, etat_courant)
            if fin:
                print('fin du parcours')
                p1 = analyse.detectfin(frame.copy())
                p2 = p1
                cg.go(p1, p2)
                break
            if intersection:
                dr.stop()
                resultat = inter.gestion_intersection(frame)
                if resultat is not None:
                    p1 = resultat['centre']
                    p2 = resultat['direction finale'][0]
                    print('intersection détecter!')
                    #print(f'{p1=},{p2=}')
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
        print(f'moyenne:{np.mean(np.array(durees_execution)[1:]):.2f},max:{np.max(np.array(durees_execution)[1:]):.2f}, min:{np.min(np.array(durees_execution)[1:]):.2f}')
        picam2.close()

if __name__ == '__main__':
    demarrage.commencer()
    while True:
        if demarrage.en_marche:
            main()
        else:
            time.sleep(0.1)
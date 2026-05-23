import sys
import math
import cv2 
import numpy as np
import time
import matplotlib.pyplot as plt
import analyse
import click_and_go as cg
        
resultats = {'tout droit' : 0,
            'à gauche' : 90,
              'à droite' : -90,
              'demi-tour' : 180}

def gestion_zone(img):
    circles = detect_balle(img)
    if circles is not None:
        print('cercle détecté!')
    return circles[0]

def detect_inter(img):
    #try:
    imgl, lines = analyse.detectdroite(img)
    if lines is None or len(lines) < 2:
        return None, None, None, None, None, None
    thetagroup, rgroup = analyse.groupir2(lines)
    theta3 = np.degrees(thetagroup[1]-thetagroup[0])
    if abs(abs(theta3) - 90) < 10:
        x, y = analyse.centre_inter(thetagroup, rgroup)
        if y > 200:
            return theta3, x, y, thetagroup, rgroup, lines

    return None, None, None, None, None, None
    #except:
    #    print("on a un problème")
    #    return None

def gestion_intersection(img):
    theta3, x, y, thetagroup, rgroup, lines = detect_inter(img)
    fin = analyse.detectfin(img)
    if theta3 is not None:
        dct = analyse.directions_possible(img, thetagroup, rgroup)
        carrebon = analyse.carre_bon(img, (x, y))
        if dct is not None:
            directionf = analyse.direction_finale(carrebon, dct, (x, y))
            if directionf is None:
                return None
            return {'direction finale':directionf,
                    'centre': (x, y),
                    'carres': carrebon,
                    'directions': dct,
                    'lines': lines,
                    'r': rgroup,
                    'theta': thetagroup,
                    'fin': fin}
        else:
            return None
    else:
        return None


def calcul_inter(resultat):
    x1, y1 = resultat['centre']
    x, y = cg.image2damier(x1, y1)
    theta1 = np.arctan2(x, y)
    theta1 = np.degrees(theta1)
    dist = np.sqrt(x**2 + y**2)
    theta2 = resultats[resultat['direction finale']]
    return theta1, theta2, dist
    
def get_barycentre(frame, irow, seuil=50):
    """ renvoie le barycentre
    1. transforme en gris
    2. applique un seuil
    3. calcule la moyenne pondérée de la ligne irow
    """
    vid_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, tabimage = cv2.threshold(vid_gray, seuil, 255, cv2.THRESH_BINARY)
        
    dim_y, dim_x = tabimage.shape
    tabimage01 = tabimage.copy()
    tabimage01[tabimage==255] = 0
    tabimage01[tabimage==0] = 1
    sommew = np.sum(tabimage01[irow, :])
    if sommew == 0:
        return np.nan
    barycentre = np.average(np.arange(dim_x), weights=tabimage01[irow, :])
    return barycentre

def visio(mask, frame):
    """Prend l'image traitée et fait un masque pour qu'on voit ce qu'il détecte"""
    overlay = np.zeros_like(frame)           # même taille que frame
    overlay[:] = (255, 100, 0)
    blue_highlight = cv2.bitwise_and(overlay, overlay, mask=mask)
    alpha = 0.8       # ← intensité du bleu (0.2 = très léger, 0.6 = bien visible)
    result = cv2.addWeighted(frame, 1.0, blue_highlight, alpha, 0.0)
    return result
    
def intersection(frame, draw=True):
    """ Prend l'image traitée et applique la transformation de ouaf pour
    avoir une liste de lignes. Si on veut dessiner, on met draw = True"""
    #img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #ret, mask = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)
    #src = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = detectligne(frame)
    dst = cv2.Canny(mask, 85, 90, apertureSize=3)
    cdstP = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    linesP = cv2.HoughLinesP(dst, rho=1, theta=np.pi / 180, threshold=40, minLineLength=60, maxLineGap=20)
    if draw:
        if linesP is not None:
            #print(len(linesP))
            for i in range(0, len(linesP)):
                l = linesP[i][0]
                cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
    return  cdstP, linesP

def centers2lines(thetacenters, rcenters, nbline):
    a = np.cos(thetacenters[0][0])
    b = np.sin(thetacenters[0][0])
    x = a * rcenters[0]
    y = b * rcenters[0]
    pt1 = (int(x + 1000 * (-b)), int(y + 1000*(a)))
    pt2 = (int(x - 1000*(-b)), int(y - 1000*(a)))
    if nbline == 2:
        a2 = np.cos(thetacenters[1][0])
        b2 = np.sin(thetacenters[1][0])
        x2 = a2 * rcenters[1]
        y2 = b2 * rcenters[1]
        pt3 = (int(x2 + 1000 * (-b2)), int(y2 + 1000*(a2)))
        pt4 = (int(x2 - 1000*(-b2)), int(y2 - 1000*(a2)))
        return pt1, pt2, pt3, pt4
    else:
        return pt1, pt2, 0, 0

if __name__ == '__main__':
    filename = "/home/eloise/monpi/robocup/last.mp4"#"/home/eloise/Documents/Informatique/Python/robocup/last.mp4"#
    video = cv2.VideoCapture(filename)#(input_dir + filename)
    if (video.isOpened() == False):
        print("Error opening the video file")
    timing = []
    ret, exemple = video.read()
    compteur = 0
    try :
        while(video.isOpened()):
            ret, tempframe = video.read()
            if ret:
                compteur = compteur + 1
                timing.append(time.time())
                frame = tempframe
                barycentre = get_barycentre(frame, -5)
                resultat = gestion_intersection(frame)
                fin = analyse.detectfin(frame)
                frame_analysé = analyse.draw_barycentre(frame,barycentre)
                frame_analysé = analyse.draw_result(frame_analysé, resultat)
                frame_analysé = analyse.draw_fin(frame_analysé, fin)
                print(resultat)
                #print(theta3)
                # les dessiner sur cdst
                #plt.scatter(tabr, thetast)
                #if nblignes == 2:
                #x, y = centre_inter(thetagroup, rgroup)
                #mask = detectligne(frame)
                    #pt1, pt2, pt3, pt4 = centers2lines(thetacenters, rcenters, nblignes)
                    #cv2.line(imgline, pt1, pt2, (0,255,255), 3, cv2.LINE_AA)
                   # cv2.line(imgline, pt3, pt4, (0,255,255), 3, cv2.LINE_AA)
                #cv2.circle(imgline, (int(x), int(y)), 30, (255,0,0), -1)
                """
                else :
                    pt1, pt2, pt3, pt4 = centers2lines(thetacenters, rcenters, nblignes)
                    cv2.line(imgline, pt1, pt2, (0,255,0), 3, cv2.LINE_AA)
                    """
                cv2.imshow("barycentre", frame_analysé)
                if resultat is not None:
                    key = cv2.waitKey(1000)
                    print(compteur)
                else:
                    key = cv2.waitKey(20)
                if compteur == 1000:
                    break
                if key == ord('q'):
                    break
                if key == ord("p"):
                    time.sleep(1)
            else:
              break
    finally:
        video.release()
        cv2.destroyAllWindows()
        cv2.imwrite('test.png', frame) 
    moy = np.mean(np.diff(timing))
    print(f'fps = {moy * 1000:.1f} ms')
    
    
    #fig2 = plt.figure("distribution r et theta")
    #axe1, axe2 = fig2.subplots(1, 2)
    #axe1.hist(lines_rs)
    #axe2.hist(thetas)
    #for center in thetacenters:
    #    plt.axvline(center, color="red")
    #pt1, pt2, pt3, pt4 = centers2lines(thetacenters, rcenters)
#     cv2.line(frame, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
#     cv2.line(frame, pt3, pt4, (0,0,255), 3, cv2.LINE_AA)
    #cv2.circle(frame, (int(x), int(y)), 30, (255,0,0), -1)
#     fig = plt.figure()
#     axe1 = fig.subplots(1, 1)
#     axe1.imshow(frame)

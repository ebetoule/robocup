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

def centre_inter(tabtheta, lsr):
    ''' prend les r et theta des deux droites détectées et calcule
    leur intersection '''
    theta1 = tabtheta[0][0]
    theta2 = tabtheta[1][0]
    r1 = lsr[0]
    r2 = lsr[1]
    cos1 = np.cos(theta1)
    cos2 = np.cos(theta2)
    sin1 = np.sin(theta1)
    sin2 = np.sin(theta2)
    y = (r2 * cos1 - cos2 * r1) / (sin2 * cos1 - cos2 * sin1)
    x = (r1 - sin1 * y) / cos1
    return x, y

def detect_inter(img):
    #try:
    imgl, lines = analyse.detectdroite(img)
    if lines is None:
        return None, None, None
    thetagroup, rgroup = analyse.groupir2(lines, img)
    theta3 = np.degrees(thetagroup[1]-thetagroup[0])
    x, y = analyse.centre_inter(thetagroup, rgroup)
    return theta3, x, y
    #except:
    #    print("on a un problème")
    #    return None

def gestion_intersection(img):
    imgl, lines = analyse.detectdroite(img)
    thetagroup, rgroup = analyse.groupir2(lines, img)
    theta3 = np.degrees(thetagroup[1] - thetagroup[0])
    if abs(abs(theta3) - 90) < 10:
        x, y = analyse.centre_inter(thetagroup, rgroup)
        #print(y)
        if y > 100:
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
                        'theta': thetagroup}
            else:
                return None
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


def detectligne(frame):
    """prend l'image et la transforme pour avoir le moins de bruit possible"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #denoised = cv2.medianBlur(hsv, 5)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 250, 90])
    mask = cv2.inRange(hsv, lower_black, upper_black)
    #kernel = np.ones((3,3), np.uint8)           # ou (5,1) si ligne horizontale
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)   # enlève petits points
    #mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=1) # reconnecte un peu
    #mask = ((frame < 50).all(axis=2)*255).astype('uint8')
    return mask

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

def segment2rtheta(xa, ya, xb, yb):
    """prend les coords x, y de deux points et renvoie le rayon et l'angle de la droite"""
    #tan_theta = (xb - xa)/(ya - yb)
    theta = np.arctan((xa - xb) / (yb - ya))#tan_theta)
    r = (xa+xb) * np.cos(theta)+ (ya+yb) * np.sin(theta)
    r = r/2
    return r, theta

def groupir(lines, ngroups=2):
    """ Prend une liste de lines (r, theta) et ne conserve que les lignes principales (2 ou 4).
    Fais la moyenne des lignes par paire. (moyenne de theta, et r)
    """
    lines_rs = []
    thetas = []
    for l in lines:
        r, theta = segment2rtheta(l[0][0], l[0][1], l[0][2], l[0][3])
        lines_rs.append(r)
        thetas.append(theta)
    thetast = np.float32(np.array(thetas))
    tabr = np.float32(np.array(lines_rs))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    thetar = list(zip(thetas, lines_rs))
    try:
        compactness,groups,thetacenters = cv2.kmeans(thetast,ngroups,None,criteria,10,flags)
    except:
        compactness,groups,thetacenters = cv2.kmeans(thetast,1,None,criteria,10,flags)
    thetacenters, rcenters, theta3, nbline = deuxun(groups, thetacenters, tabr, thetar, thetast)
    return thetacenters, rcenters, theta3, nbline, thetast, tabr

def groupir2(lines, ngroups=2):
    """ Prend une liste de lines (r, theta) et ne conserve que les lignes principales (2 ou 4).
    Fais la moyenne des lignes par paire. (moyenne de theta, et r)
    """
    lines_rs = []
    thetas = []
    for l in lines:
        r, theta = segment2rtheta(l[0][0], l[0][1], l[0][2], l[0][3])
        lines_rs.append(r)
        thetas.append(theta)
    thetast = np.float32(np.array(thetas))
    x = np.cos(2 * thetast)
    y = np.sin(2 * thetast)
    tabr = np.float32(np.array(lines_rs))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    thetar = list(zip(thetas, lines_rs))
    try:
        compactness,groups,thetacenters = cv2.kmeans([x, y],ngroups,None,criteria,10,flags)
    except:
        compactness,groups,thetacenters = cv2.kmeans(thetast,1,None,criteria,10,flags)
    thetacenters, rcenters, theta3, nbline = deuxun(groups, thetacenters, tabr, thetar, thetast)
    return thetacenters, rcenters, theta3, nbline, thetast, tabr

def deuxun(groups, thetacenters, tabr, thetar, thetast):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    if len(groups) == 1:
        compactness,groups,rcenters = cv2.kmeans(tabr,1,None,criteria,10,flags)
        return thetacenters, rcenters, 0, 1
    else:
        r1 = []
        r2 = []
        for i in range(len(thetar)):
            if groups[i]==0:
                r1.append(thetar[i])
            else:
                r2.append(thetar[i])
        ls1 = np.array(r1)
        ls2 = np.array(r2)
        rcenters = (np.mean(ls1[:,1]),np.mean(ls2[:,1]))
        theta3 = np.degrees(thetacenters[1][0] - thetacenters[0][0])
        if abs(abs(theta3) - 90) > 10:
            compactness,groups,thetacenters = cv2.kmeans(thetast,1,None,criteria,10,flags)
            compactness,groups,rcenters = cv2.kmeans(tabr,1,None,criteria,10,flags)
            return thetacenters, rcenters, 0, 1
        else:
            return thetacenters, rcenters, theta3, 2
        

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
    filename = "/home/eloise/monpi/robocup/last.mp4"
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
                frame_analysé = analyse.draw_barycentre(frame,barycentre)
                frame_analysé = analyse.draw_result(frame_analysé, resultat)
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

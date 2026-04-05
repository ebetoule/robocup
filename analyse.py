import cv2
import numpy as np

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

def detectvert(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    min_vert = np.array([40, 50, 50])#Teinte, saturation, value
    max_vert = np.array([80, 255, 255])
    mask = cv2.inRange(hsv, min_vert, max_vert)
    return mask

def detectcarre(frame):
    mask = detectvert(frame)
    contours,hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(mask, contours, -1, (0, 0, 255), 5)
    carre = []
    for data in contours:
        try:
            M = cv2.moments(data)
            #print(M)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            carre.append([cx, cy])
            cv2.circle(frame, (int(cx), int(cy)), 1, (255,0,0), -1)
            #print(f'ça marche normalement : {cx}, {cy}')
        except:
            pass
    return contours, frame, carre

def detectdroite(frame):
    """ Prend l'image traitée et applique la transformation de ouaf pour
    avoir une liste de lignes. Si on veut dessiner, on met draw = True"""
    #img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #ret, mask = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)
    #src = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = detectligne(frame)
    dst = cv2.Canny(mask, 85, 90, apertureSize=3)
    imgl = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    linesP = cv2.HoughLinesP(dst, rho=1, theta=np.pi / 180, threshold=40, minLineLength=60, maxLineGap=20)
    return  imgl, linesP

def drawsegments(linesP, imgl, color=(0,0,255)):
    if linesP is not None:
        #print(len(linesP))
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(imgl, (l[0], l[1]), (l[2], l[3]), color, 3, cv2.LINE_AA)
    return imgl

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


def drawdroites(thetas, rs, img):
    for theta, r in zip(thetas, rs):
        pt1, pt2 = lines2segments(theta, r)
        cv2.line(img, pt1, pt2, (0,255,255), 3, cv2.LINE_AA)
    #cv2.circle(img, (int(x), int(y)), 30, (255,0,0), -1)
    return img
    
def lines2segments(theta, r):
    a = np.cos(theta)
    b = np.sin(theta)
    x = a * r
    y = b * r
    pt1 = (int(x + 1000 * (-b)), int(y + 1000*(a)))
    pt2 = (int(x - 1000*(-b)), int(y - 1000*(a)))
    return pt1, pt2

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
        
def groupir2(lines, img, ngroups=2):
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
    compactness,groups,groupcoord = cv2.kmeans(np.array([x, y]).T,ngroups,None,criteria,10,flags)#kmeans veut absolument un tableau dans le bon sens
    xg = groupcoord[:,0]
    yg = groupcoord[:,1]
    deuxthetasgroup = np.arctan2(yg, xg)
    thetagroup = deuxthetasgroup / 2
    colors = [(0, 0, 255), (255, 0, 0), (0, 255, 0)]
    thetargroup = []
    rgroup = []
    for i in range(ngroups):
        danslegroupe = (groups.squeeze() == i)#squeeze enlève une dimension
        thetargroup.append(np.array(thetar)[danslegroupe,:])
        img = drawsegments(lines[danslegroupe,:,:], img, color=colors[i])
        #cas particulier des droites horyzontales
        if np.abs(thetagroup[i]) > np.radians(85):  
            rgroup.append(np.mean(np.sign(thetagroup[i]) * np.sign(thetargroup[i][:,0]) * thetargroup[i][:,1]))
        else:
            rgroup.append(np.mean(thetargroup[i][:,1]))
    #plt.scatter(x, y, c=groups)
    #plt.scatter(lines_rs, thetas, c=groups)
    #plt.xlim(-1, 1)
    #plt.ylim(-1, 1)
    return img, thetagroup, rgroup

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    #plt.close('all')
    img = cv2.imread('test2.png')
    plt.ion()
    #plt.imshow(img)
    
    # test de détectligne
    plt.figure('detectline')#mets un titre à la fenêtre qu'on affiche
    mask = detectligne(img)
    plt.imshow(mask)
    
    #test de detect_vert:
    plt.figure('vert')
    mask2 = detectvert(img)
    plt.imshow(mask2)
    
    contours, mask3, carre = detectcarre(img)
    #print(contours)
    #drawsegments(contours, img, color=(0,0,255))
    plt.figure('contours')
    plt.imshow(mask3)
    # test de detectdroite
#     plt.figure('detectdroite')
#     imgl, lines = detectdroite(img)
#     plt.imshow(drawsegments(lines, imgl))
    
    #test de groupir
#     thetacenters, rcenters, theta3, nbline, thetast, tabr = groupir(lines)
#     pt1, pt2 = lines2segments(thetacenters, rcenters)
#     plt.imshow(drawdroites(thetacenters, rcenters, imgl))
    
    #test de groupir2
#     plt.figure('groups')
#     imgp, thetagroup, rgroup = groupir2(lines, img, ngroups=2)
#     plt.figure('groupir2')
#     drawdroites(thetagroup, rgroup, imgp)
#     plt.imshow(imgp)
    
import cv2
import numpy as np

def draw_result(frame, result):
    if result is not None:
        img_ana = draw_carre(result['carres'], frame.copy())
        img_ana = drawdroites(result['theta'], result['r'], img_ana)
        img_ana = draw_direction_possibles(img_ana, result['centre'], result['directions'])
        img_ana = draw_direction_finale(result['direction finale'], result['centre'], img_ana)
        img_ana = drawsegments(result['lines'], img_ana, color=(0,0,255))
        #print(result['direction finale'])
        return img_ana
    return frame

def detectligne(frame):
    """prend l'image et la transforme pour avoir le moins de bruit possible"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #denoised = cv2.medianBlur(hsv, 5)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 250, 70])
    mask = cv2.inRange(hsv, lower_black, upper_black)
    #kernel = np.ones((3,3), np.uint8)           # ou (5,1) si ligne horizontale
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)   # enlève petits points
    #mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=1) # reconnecte un peu
    #mask = ((frame < 50).all(axis=2)*255).astype('uint8')
    return mask

def centre_inter(tabtheta, lsr):
    ''' prend les r et theta des deux droites détectées et calcule
    leur intersection '''
    theta1 = tabtheta[0]
    theta2 = tabtheta[1]
    r1 = lsr[0]
    r2 = lsr[1]
    cos1 = np.cos(theta1)
    cos2 = np.cos(theta2)
    sin1 = np.sin(theta1)
    sin2 = np.sin(theta2)
    y = (r2 * cos1 - cos2 * r1) / (sin2 * cos1 - cos2 * sin1)
    x = (r1 - sin1 * y) / cos1
    return int(x), int(y)

def draw_centre_inter(img, x, y):
    frame = cv2.circle(img, (x, y), 10, (255,0,0), -1)
    return frame

def directions(thetagroup, rgroup):
    '''On calcule le centre de l'intersection puis on prend quatre points
en haut, en bas, à gauche et à droite sur les lignes de l'intersection'''
    cx, cy = centre_inter(thetagroup, rgroup)
    #print(f'centre = {cx, cy}')
    dct = []
    for theta, r in zip(thetagroup, rgroup):
        for d in 80, -80:
            a = np.cos(theta)
            b = np.sin(theta)
            pt = (int(cx + d * (-b)), int(cy + d*(a)))
            dct.append(pt)
    return dct

def draw_directions(dct, mask, centre):
    for d in dct:
        mask = cv2.line(mask, centre, d, (255, 0, 0), 15, cv2.LINE_AA)
    return mask

def directions_possible(img, thetagroup, rgroup):
    dct = directions(thetagroup, rgroup)
    mask = detectligne(img)
    dct_noir = []
    for cx, cy in dct:
        if couleur_moyenne(mask, cx, cy) > 100 and cy > -1:
            dct_noir.append((cx, cy))
    return dct_noir
            
def couleur_moyenne(mask, x, y, size=[10, 10]):
    '''On fait un 'carré' virtuel de 10 pixel par 10 pixel
et on retourne la moyenne de la couleur du carré'''
    x1 = int(max(x - size[1], 0))
    x2 = int(min(x + size[1], mask.shape[1]))
    y1 = int(max(y - size[0], 0))
    y2 = int(min(y + size[0], mask.shape[0]))
    return np.mean(mask[y1:y2, x1:x2])

def draw_direction_possibles(img, centre, dct, color=(0, 150, 0)):
    color = [(255, 0, 0),(0, 0, 255), (0, 255, 0), (0, 150, 0)]
    i=0
    for d in dct:
        cv2.line(img, centre, d, color[i], 15, cv2.LINE_AA)
        i+=1
    return img

def trouve_minimum(dct):
    ymin = 481
    for i in range(len(dct)):
        if dct[i][1] < ymin:
            ymin = dct[i][1]
            imin = i
    return imin
    
    
def direction_à_prendre(dct, centre):
    imin = trouve_minimum(dct)
    return dct[imin], 'tout droit'
    if len(dct)==4 or len(dct)==3:
        direction = (dct[-1], 'tout_droit')
    else:
        if bdct[0] < centre[0]:
            direction = (bdct, 'à gauche')
        else:
            direction = (bdct, 'à droite')
    return direction

def valeurs_hsv(frame):
    import matplotlib.pyplot as plt
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    legende = ['teinte', 'saturation', 'valeur']
    fig = plt.figure()
    axes = fig.subplots(1,3)#nblignes, nbcolonnes
    for i, axe in enumerate(axes):
        axe.imshow(hsv[:,:,i])
        axe.set_title(legende[i])
    plt.show()
    
def detectrouge(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 200, 200])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 200, 200])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    return mask

def detectfin(frame):
    mask = detectrouge(frame)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for data in contours:
        try:
            area = cv2.contourArea(data)
            if area > 1000:
                M = cv2.moments(data)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                return cx, cy
        except Exception as E:
            print(E)
    return None
    

def detectvert(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    min_vert = np.array([50, 50, 50])#Teinte, saturation, value
    max_vert = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, min_vert, max_vert)
    return mask

def detectcarre(frame):
    mask = detectvert(frame)
    contours,hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(mask, contours, -1, (0, 0, 255), 5)
    carre = []
    for data in contours:
        try:
            area = cv2.contourArea(data)
            if area > 1000:
                M = cv2.moments(data)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                carre.append([cx, cy])
        except Exception as E:
            print(E)
    return mask, carre

def carre_bon(frame, centre):
    mask, carre = detectcarre(frame)
    bon_carre = []
    if len(carre) > 0:
        for i in range(len(carre)):
            if carre[i][1] > centre[1]:
                bon_carre.append(carre[i])
    return bon_carre

def direction_carre(carre, dct, centre):
    if len(carre)==2:
        for i in range(len(dct)):
            if (dct[i][1] - centre[1]) > 50:
                dm = dct[i]
        direction = (dm, 'demi-tour')
    else :
        if carre[0][0] < centre[0]:
            for i in range(len(dct)):
                if (centre[0] - dct[i][0]) > 50:
                    dg = dct[i]
                    direction = (dg, 'à gauche')
        else:
            for i in range(len(dct)):
                if (dct[i][0] - centre[0]) > 50:
                    dd = dct[i]
                    direction = (dd, 'à droite')
    return direction

def direction_finale(carre, dct, centre):
    if len(carre) > 0:
        try:
            direction = direction_carre(carre, dct, centre)
        except:
            return None
    elif len(dct) > 1:
        direction = direction_à_prendre(dct, centre)
    else:
        direction = None
    return direction

def draw_direction_finale(direction, centre, frame):
    if direction is not None:
        color = (255, 0, 255)
        return cv2.arrowedLine(frame, centre, direction[0], color, 3)
    return frame
    
def draw_carre(results, frame):
    frame_analysé = frame.copy()
    for i in range(len(results)):
        cx, cy = results[i]
        cv2.circle(frame_analysé, (cx, cy), 10, (255,0,0), -1)
    return frame_analysé
    
def draw_barycentre(frame, barycentre):
    if np.isfinite(barycentre):
        return cv2.circle(frame.copy(), (int(barycentre), frame.shape[0]-5), 10, (255,0,0), -1)
    else:
        return frame

def detectdroite(frame):
    """ Prend l'image traitée et applique la transformation de ouaf pour
    avoir une liste de lignes. Si on veut dessiner, on met draw = True"""
    #img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #ret, mask = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)
    #src = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = detectligne(frame)
    dst = cv2.Canny(mask, 85, 90, apertureSize=3)
    imgl = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    linesP = cv2.HoughLinesP(dst, rho=0.5, theta=2*np.pi / 180, threshold=40, minLineLength=40, maxLineGap=30)
    return  imgl, linesP

def ligne_droite(frame):
    mask = detectligne(frame)
    contours,hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(mask, contours, -1, (0, 0, 255), 5)
    for data in contours:
        try:
            area = cv2.contourArea(data)
            if area > 1000:
                M = cv2.moments(data)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                if cx is not None:
                    return cx, cy
        except Exception as E:
            print(E)
    return None
    

def drawsegments(linesP, imgl, color=(0,0,255)):
    if linesP is not None:
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
        if np.abs(thetagroup[i]) > np.radians(85):  
            rgroup.append(np.mean(np.sign(thetagroup[i]) * np.sign(thetargroup[i][:,0]) * thetargroup[i][:,1]))
        else:
            rgroup.append(np.mean(thetargroup[i][:,1]))
    return thetagroup, rgroup

if __name__ == '__main__':
    print('jusque là ça va')
    import matplotlib.pyplot as plt
    plt.close('all')
    img = cv2.imread('test.png')
    plt.ion()
    #plt.imshow(img)
    
    # test de détectligne
    plt.figure('detectline')#mets un titre à la fenêtre qu'on affiche
    mask = detectligne(img)
    plt.imshow(mask)
    valeurs_hsv(img)
     #test de detect_vert:
    plt.figure('vert')
    mask3 = detectvert(img)
    plt.imshow(mask3)
    
    mask4, carre = detectcarre(img)
    mask4 = draw_carre(carre, img)
    #print(contours)
    #drawsegments(contours, img, color=(0,0,255))
    plt.figure('contours')
    plt.imshow(mask4)
    
    
    # test de detectdroite
    plt.figure('detectdroite')
    imgl, lines = detectdroite(img)
    plt.imshow(drawsegments(lines, imgl))
    
    #test de groupir
#    thetacenters, rcenters, theta3, nbline, thetast, tabr = groupir(lines)
    
    
    #test des directions:
    thetagroup, rgroup = groupir2(lines, img)
    #pt1, pt2 = lines2segments(thetagroup, rgroup)
    plt.figure('groupir')
    plt.imshow(drawdroites(thetagroup, rgroup, img))
    x, y = centre_inter(thetagroup, rgroup)
    print(x, y)
    mask2 = draw_centre_inter(img, x, y)
    plt.figure('centre')
    plt.imshow(mask2)
    dct1 = directions(thetagroup, rgroup)
    mask1 = draw_directions(dct1, img.copy(), (x, y))
    plt.figure('directions')
    plt.imshow(mask1)
    #cv2.circle(img, (int(x), int(y)), 10, (255,0,0), -1)
    dct = directions_possible(img, thetagroup, rgroup)
#    draw_direction_possibles(imgp, (int(x), int(y)), dct)
#     directionl = direction_à_prendre(dct, (x, y))
#     plt.figure('directions')
#     plt.imshow(imgp)
#     print(directionl)
    # test des carre:
    carrebon = carre_bon(img, (x, y))
    #print(f'{len(carrebon)}carrés en dessous du centre:{carrebon}')
    
    # test direction avec carre:
#     directionc = direction_carre(carrebon, (x, y))
#     print(directionc)
#     import intersections
    directionf = direction_finale(carrebon, dct, (x, y))
    print('direction finale = ', directionf)
    plt.figure('direction finale')
    plt.imshow(draw_direction_finale(directionf, (x, y), img))
#     resultat = intersections.gestion_intersection(img)
    #test de groupir2
#     plt.figure('groups')
#     imgp, thetagroup, rgroup = groupir2(lines, img, ngroups=2)
#     plt.figure('groupir2')
#     drawdroites(thetagroup, rgroup, imgp)
#     plt.imshow(imgp)
    
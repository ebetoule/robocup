import cv2
import camera
import numpy as np
from buildhat import Motor
motor_right = Motor('A')
motor_left = Motor('B')

objpoints = np.array([
    [-4, 13],
    [2, 13],
    [-6, 28.],
    [6,28],
    ], dtype="float32")
imgpoints = np.array([
    [16, 334],
    [500, 335],
    [129., 24],
    [523, 27],
    ], dtype="float32")

#cv2.imread('tutoriel/chess/ccn11.jpg')
M = cv2.getPerspectiveTransform(imgpoints,objpoints)
def tourner(degres):
    degres = degres / 0.56
    motor_left.run_for_degrees(degres, 10, False)
    motor_right.run_for_degrees(degres, 10, False)
    
def aller(distance):
    dist = distance/0.075
    motor_left.run_for_degrees(-dist, 10, False)
    motor_right.run_for_degrees(dist, 10, False)

nbfois = 1
x1 = None
y1 = None

def obtenir_coord(action, x, y, flags, userdata):
    global nbfois, x1, y1
    if action == cv2.EVENT_LBUTTONDBLCLK:
        if nbfois == 2:
            x2, y2 = image2damier(x, y)
            theta1, theta3, dist = xy2thetadist(x1, y1, x2, y2)
            print(f'A = ({x1, y1}), B = ({x2, y2}), angle = {theta1}°, distance = {dist}cm , deuxième angle = {theta3}°')
            tourner(-theta1)
            aller(dist)
            tourner(-theta3)
            nbfois = 1
        elif nbfois == 1:
            x1, y1 = image2damier(x, y)
            nbfois = nbfois + 1

def xy2thetadist(x1, y1, x2, y2):
    theta1 = np.arctan2(x1, y1)
    theta1 = np.degrees(theta1)
    ##print(theta1)
    theta2 = np.arctan2(x1 - x2, y2 - y1)
    theta2 = np.degrees(theta2)
    #print(theta2)
    theta3 = - theta1 - theta2
    #print(theta3)
    dist = np.sqrt(x1**2 + y1**2)
    return theta1, theta3, dist

def image2damier(x, y):
    ''' retourne les points de l'image obtenue par la camera en points réels'''
    #M = np.array([[ 2.85224511e-02,  1.46455029e-02, -5.54372105e+00],
               #[ 1.21992854e-03,  6.51578808e-02, -7.25122927e+00],
               #[-1.82478137e-05,  5.31945922e-03,  1.00000000e+00]])
    x1 = (M[0,0]*x + M[0,1]*y + M[0,2]) / (M[2,0]*x + M[2,1]*y + M[2,2])
    y1 = (M[1,0]*x + M[1,1]*y + M[1,2]) / (M[2,0]*x + M[2,1]*y + M[2,2])
    return x1, y1

if __name__ == '__main__':
    picam2 = camera.init_pycam()
    image = picam2.capture_array()
    cv2.imshow('coucou', image)
    cv2.setMouseCallback('coucou', obtenir_coord)
    while True:
        image = picam2.capture_array()
        cv2.imshow('coucou', image)
        key = cv2.waitKey(20)
        if key == ord('q'):
            break
    cv2.destroyAllWindows()

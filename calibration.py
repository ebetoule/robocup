import cv2
import camera
import numpy as np
"""
[[ 3.48476347e-02 -3.12056777e-03 -1.23421610e+01]
 [ 2.97398611e-03  1.67479070e-02  3.12144966e+01]
 [ 1.06213790e-04  5.38161659e-03  1.00000000e+00]]
"""
imgpoints = np.array([
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    ], dtype="float32")


objpoints = np.array([
    [-3, 11],
    [3, 11],
    [-7, 25.],
    [7,25],
    ], dtype="float32")
compteur = 0

def click(action, x, y, flags, userdata):
    """ cliquer dans l'ordre, sans se tromper :
    -avec le bouton gauche, le coin en bas à gauche
    -avec le bouton droit, le coin en bas à droite
    -avec la touche controle, le coin en haut à gauche
    -avec la touche tab, le coin en haut à droite"""
    global imgpoints
    global compteur
    if action == cv2.EVENT_LBUTTONDBLCLK:
        imgpoints[compteur,0] = x
        imgpoints[compteur,1] = y
        compteur = compteur + 1
        print(f"ok pour le nummero {compteur}")
    if compteur == 4:
        print("ok pour le quatrième")
        print(imgpoints)
        M = cv2.getPerspectiveTransform(imgpoints,objpoints)
        print(M)
    


if __name__ == '__main__':
    picam2 = camera.init_pycam()
    image = picam2.capture_array()
    cv2.imshow('coucou', image)
    cv2.setMouseCallback('coucou', click)
    while True:
        image = picam2.capture_array()
        cv2.imshow('coucou', image)
        key = cv2.waitKey(20)
        if key == ord('q'):
            break
    cv2.destroyAllWindows()

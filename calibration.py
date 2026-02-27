import cv2
import camera
import numpy as np

def click(action, x, y, flags, userdata):
    ''' cliquer dans l'ordre, sans se tromper :
-avec le bouton gauche, le coin en bas à gauche
-avec le bouton droit, le coin en bas à droite
-avec la touche controle, le coin en haut à gauche
-avec la touche tab, le coin en haut à droite'''
    if action == cv2.EVENT_LBUTTONDBLCLK:
        x1, y1 = x, y
    if action == cv2.EVENT_RBUTTONDBLCLK:
        x2, y2 = x, y
    if action == cv2.EVENT_FLAG_CTRLKEY:
        x3, y3 = x, y
    if action == cv2.EVENT_FLAG_ALTKEY :
        x4, y4 = x, y
    
    objpoints = np.array([
        [-4, 13],
        [2, 13],
        [-6, 28.],
        [6,28],
        ], dtype="float32")
    imgpoints = np.array([
        [x1, y1],
        [x2, y2],
        [x3., y3],
        [x4, y4],
        ], dtype="float32")

#cv2.imread('tutoriel/chess/ccn11.jpg')
M = cv2.getPerspectiveTransform(imgpoints,objpoints)



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

import numpy as np
import cv2 as cv
import glob
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
nx = 6#nb de case en abscisse
ny = 6#nb de case en ordonnée
objp = np.zeros((nx*ny,3), np.float32)#tableau des vraies coordonnées 3D
objp[:,:2] = np.mgrid[0:nx,0:ny].T.reshape(-1,2)# z est remplie de 0
# Arrays to store object points and image points from all the images.
objpoints = [] # liste des points 3D
imgpoints = [] # liste des points 2D
images = glob.glob('chess/*.jpg')
for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (ny,nx), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
        
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
# undistort
print(dist)
print(mtx)

def pixel2coord(x, y):
    mtx = np.array([[2.31301612e+04 0.00000000e+00 3.32043767e+02]
                    [0.00000000e+00 2.33779030e+03 5.06553366e+01]
                    [0.00000000e+00 0.00000000e+00 1.00000000e+00]]
                    )
    dist = np.array([[ 9.81528305e+01  6.83774322e+04  5.04370810e+00  3.42687995e-02 -1.65491124e+03]])
    pix = np.array([[[x, y]]])
    coord = cv.undistortPoints(pix, mtx, dist)
    return coord[0], coord[1]

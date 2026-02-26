"""
https://docs.opencv.org/4.x/da/d6e/tutorial_py_geometric_transformations.html
https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html#gaf73673a7e8e18ec6963e3774e6a94b87
"""
import numpy as np
import cv2 as cv
import glob
import matplotlib.pyplot as plt

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
nx = 6 #nb de case en abscisse
ny = 6 #nb de case en ordonnée
cm2pix = 1#80# en cm 80 # en pixel
objp = np.zeros((nx*ny,3), np.float32)#tableau des vraies coordonnées 3D
objp[:,:2] = cm2pix*np.mgrid[0:nx,0:ny].T.reshape(-1,2)# z est remplie de 0

# Arrays to store object points and image points from all the images.
objpoints = [] # liste des points 3D
imgpoints = [] # liste des points 2D
img = cv.imread("ccn16.jpg")
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Find the chess board corners
ret, corners = cv.findChessboardCorners(gray, (ny,nx), None)
# If found, add object points, image points (after refining them)

if ret == True:
    objpoints.append(objp)
    corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
    imgpoints.append(corners2)#corners2
    cv.drawChessboardCorners(img, (nx,ny), corners2, ret)
    
    

pts1 = imgpoints[0].squeeze()[[0,5,30,35],:]
pts2 = objpoints[0].squeeze()[[0,5,30,35],0:2]
print(pts1)
print(pts2)
M = cv.getPerspectiveTransform(pts1,pts2)

def apply_transform(x0, y0):
    x1 = (M[0,0]*x0 + M[0,1]*y0 + M[0,2]) / (M[2,0]*x0 + M[2,1]*y0 + M[2,2])
    y1 = (M[1,0]*x0 + M[1,1]*y0 + M[1,2]) / (M[2,0]*x0 + M[2,1]*y0 + M[2,2])
    return x1, y1


## regarder les images
if 0:
    dst = cv.warpPerspective(img,M,(400,400))

    for x0, y0, c in [(150, 300, (0,255,0)), (100, 200, (255,0,0))]:
        x1, y1 = apply_transform(x0, y0)
        cv.circle(img, center=(x0, y0), radius=5, color=c, thickness=2)
        cv.circle(dst, center=(int(x1), int(y1)), radius=5, color=c, thickness=2)

    #plt.subplot(121),plt.imshow(img),plt.title('Input')
    #plt.subplot(122),plt.imshow(dst),plt.title('Output')

    cv.namedWindow("img")
    cv.imshow('img', img)
    cv.waitKey(0)
    cv.namedWindow("dst")
    cv.imshow('dst', dst)
    cv.waitKey(0)
    cv.destroyAllWindows()

## quelques essais
for x0, y0 in [(150, 300),
               (100, 200),
               (200, 100),
               (50, 50),
               (400, 400),
               (400, 100)]:
    x1, y1 = apply_transform(x0, y0)
    print(x0, y0, x1, y1)
    cv.putText(img, f"{int(x1)},{int(y1)}", (x0, y0), cv.FONT_HERSHEY_SIMPLEX,1, (255,0,0), 2)
    cv.circle(img, center=(x0, y0), radius=5, color=(255,0,0), thickness=2)
    
#cv.namedWindow("img")
cv.imshow('img', img)
cv.waitKey(0)
cv.destroyAllWindows()
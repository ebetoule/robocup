"""
@file hough_lines.py
@brief This program demonstrates line finding with the Hough transform
"""
import sys
import math
import cv2 as cv
import numpy as np


default_file = 'intersection1.jpg'
filename = default_file #argv[0] if len(argv) > 0 else default_file
# Loads an image
src = cv.imread(filename, cv.IMREAD_GRAYSCALE)
src = cv.resize(src, [640, 480])

# Check if image is loaded fine
if src is None:
    print ('Error opening image!')
    print ('Usage: hough_lines.py [image_name -- default ' + default_file + '] \n')
    
cv.imshow("Source", src)

dst = cv.Canny(src, 50, 200, None, 3)

# Copy edges to the images that will display the results in BGR
cdst = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
#ret, thresh = cv.threshold(cdst, 50, 255, cv.THRESH_BINARY)

lines = cv.HoughLines(dst, 10, 30 * np.pi / 180, 100, None, 0, 0)
print("detected lines", len(lines), lines) #lines)
if lines is not None:
    for i in range(0, len(lines)):
        rho = lines[i][0][0]
        theta = lines[i][0][1]
        a = math.cos(theta)
        b = math.sin(theta)
        x0 = a * rho
        y0 = b * rho
        pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
        pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
        cv.line(cdst, pt1, pt2, (0,0,255), 3, cv.LINE_AA)
    
#cv.imshow("Source", src)
#cv.imshow("Detected Lines (in red) - Standard Hough Line Transform", cdst)
#cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP)

#cv.waitKey()
#cv.destroyAllWindows() 

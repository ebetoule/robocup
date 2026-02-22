"""
@file hough_lines.py
@brief This program demonstrates line finding with the Hough transform
"""
import sys
import math
import cv2 
import numpy as np
import time


video = cv2.VideoCapture('02-20-2026_12-26-47.mp4')


if (video.isOpened() == False):
    print("Error opening the video file")

def intersection(frame):
    src = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #Check if image is loaded fine
    #if src is None:
        #print ('Error opening image!')
        #print ('Usage: hough_lines.py [image_nxame -- default ' + default_file + '] \n')
    
    #cv2.imshow("Source", src)

    dst = cv2.Canny(src, 85, 90, apertureSize=3)
    
    #cdst = dst
    cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    cdstP = np.copy(cdst)
    #cv2.imshow("Source", cdst)
    #ret, thresh = cv.threshold(cdst, 50, 255, cv.THRESH_BINARY)

#     lines = cv2.HoughLines(dst, 10, 30 * np.pi / 180, 100, None, 0, 0)
#     if lines is None:
#         print("pas de ligne")
#         return cdst
#     print("detected lines", len(lines), lines) #lines)
#     if lines is not None:
#         for i in range(0, len(lines)):
#             rho = lines[i][0][0]
#             theta = lines[i][0][1]
#             a = math.cos(theta)
#             b = math.sin(theta)
#             x0 = a * rho
#             y0 = b * rho
#             pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
#             pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
#             cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
    linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 10, None, 50, 10)
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
    return  cdstP  #cdst
            
while(video.isOpened()):
    ret, frame = video.read()
    if ret == True:
        cdstP = intersection(frame)
        #cv2.imshow("Detected Lines (in red) - Standard Hough Line Transform", cdst)
        cv2.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP)
        key = cv2.waitKey(20)
        #time.sleep(0.1)
        if key == ord('q'):
            break
    else:
      break
 

video.release()
cv2.destroyAllWindows() 

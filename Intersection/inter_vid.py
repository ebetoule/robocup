import cv2 
import numpy as np
import time

def detectligne(frame):
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
    overlay = np.zeros_like(frame)           # même taille que frame
    overlay[:] = (255, 100, 0)
    blue_highlight = cv2.bitwise_and(overlay, overlay, mask=mask)
    alpha = 0.8       # ← intensité du bleu (0.2 = très léger, 0.6 = bien visible)
    result = cv2.addWeighted(frame, 1.0, blue_highlight, alpha, 0.0)
    return result
    
def intersection(frame):
    #img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #ret, mask = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)
    #src = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = detectligne(frame)
    dst = cv2.Canny(mask, 85, 90, apertureSize=3)
    cdstP = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 10, None, 50, 10)
    if linesP is not None:
        print(len(linesP))
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
    return  cdstP  

if __name__ == '__main__':
    filename = ['02-16-2026_15-12-43.mp4', '02-20-2026_12-26-47.mp4'][0]
    video = cv2.VideoCapture(filename)
    if (video.isOpened() == False):
        print("Error opening the video file")
    timing = []
    ret, exemple = video.read()
    while(video.isOpened()):
        ret, frame = video.read()
        timing.append(time.time())
        if ret == True:
            cdstP = intersection(frame)
            #mask = detectligne(frame)
            cv2.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP)
            #cv2.imshow("Masque", mask)
            #cv2.imshow("Masque", visio(mask, frame))
            key = cv2.waitKey(20)
            #time.sleep(0.1)
            if key == ord('q'):
                break
            if key == ord("p"):
                time.sleep(1)
        else:
          break
 
    moy = np.mean(np.diff(timing))
    print(f'fps = {moy * 1000:.1f} ms')
    video.release()
    cv2.destroyAllWindows() 

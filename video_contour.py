import cv2
video = cv2.VideoCapture('testhd.h264')

if (video.isOpened() == False):
    print("Error opening the video file")
# Savoir si il y a un problème
else:
  # Obtenir les informations qu'on souhaite
    fps = video.get(5)
    print('Frames per second : ', fps,'FPS')
    frame_count = video.get(7)
    print('Frame count : ', frame_count)

while(video.isOpened()):
  # lire chaque image une par une
    ret, frame = video.read()
    
    if ret == True:
        vid_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(vid_gray, 50, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        image_copy = frame.copy()
        cv2.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(252, 173, 3), thickness=2, lineType=cv2.LINE_AA)
        cv2.imshow('frame', image_copy)
        # 20 est en milliseconde
        key = cv2.waitKey(20)
     
        if key == ord('q'):
            break
    else:
        break
 
 
# fremer la fenêtre de vidéo
video.release()
cv2.destroyAllWindows()
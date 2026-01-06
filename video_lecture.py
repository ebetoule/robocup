import cv2
# lire la vidéo
vid_capture = cv2.VideoCapture(0)

fourcc = cv2.VideoWriter_fourcc(*'MPV4')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640,  480))
 
if (vid_capture.isOpened() == False):
    print("Error opening the video file")
# Savoir si il y a un problème
else:
  # Obtenir les informations qu'on souhaite
    fps = vid_capture.get(5)
    print('Frames per second : ', fps,'FPS')
    frame_count = vid_capture.get(7)
    print('Frame count : ', frame_count)
 
while(vid_capture.isOpened()):
  # lire chaque image une par une
    ret, frame = vid_capture.read()
    if ret == True:
        out.write(frame)
        cv2.imshow('Frame',frame)
    # 20 est en milliseconde
        key = cv2.waitKey(20)
     
        if key == ord('q'):
            break
    else:
      break
 
# fremer la fenêtre de vidéo
vid_capture.release()
cv2.destroyAllWindows()
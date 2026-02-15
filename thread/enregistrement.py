import cv2
import threading
import queue
import time

# Fonction pour le thread d'enregistrement
def recording_thread(q, output_file, fps=15, size):
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Codec efficace
    writer = cv2.VideoWriter(output_file, fourcc, fps, size)
    while True:
        frame = q.get()
        if frame is None:  # Signal de fin
            break
        # Resize pour réduire la taille (optionnel)
        frame = cv2.resize(frame, (width, height))
        writer.write(frame)
    writer.release()

# Setup caméra Arducam (ajustez l'index si nécessaire)
cap = cv2.VideoCapture(0)  # Ou 'v4l2src device=/dev/video0 ! video/x-raw,width=640,height=480 ! videoconvert ! appsink' avec GStreamer
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # Limite buffer pour faible latence

# Queue pour passer les frames à enregistrer
frame_queue = queue.Queue(maxsize=10)  # Limite pour éviter surcharge

# Lance le thread d'enregistrement
rec_thread = threading.Thread(target=recording_thread, args=(frame_queue, 'output.avi'))
rec_thread.start()

# Boucle principale : Capture, traitement, contrôle moteurs
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Votre traitement d'image ici (suivi de ligne avec OpenCV)
    # Exemple : gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # ... Détection ligne, commande moteurs via Build HAT ...
    
    # Passe une copie du frame à la queue pour enregistrement (sans bloquer)
    if not frame_queue.full():
        frame_queue.put(frame.copy())  # Copie pour éviter modification partagée
    
    # Optionnel : Affichez pour debug (mais évitez si pas nécessaire, car ça ralentit)
    # cv2.imshow('Frame', frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# Fin : Signal au thread d'enregistrement
frame_queue.put(None)
rec_thread.join()
cap.release()
cv2.destroyAllWindows()
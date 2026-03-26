import cv2
import threading
import queue
import time
import buildhat
from buildhat import Motor
from picamera2 import Picamera2
import curses
from curses import wrapper
from camera import init_pycam, size
from deplacements_robot import avancer, gauche, droit, stop


# Fonction pour le thread d'enregistrement
def recording_thread(q, nom, fps=15, size=size):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec efficace
    writer = cv2.VideoWriter(nom, fourcc, fps, size)#(width, height))
    print("debut de l'enregistrement")
    nframe = 0
    while True:
        nframe += 1
        frame = q.get()
        if frame is None:  # Signal de fin
            print(f"Arret de l'enregistrement apres {nframe} images")
            break
        # Resize pour réduire la taille (optionnel)
        #frame = cv2.resize(frame, (width, height))
        writer.write(frame)
    writer.release()

if __name__ == "__main__":
    speed = 10
    size = (640,480)

    # Queue pour passer les frames à enregistrer
    frame_queue = queue.Queue(maxsize=10)  # Limite pour éviter surcharge

    # Lance le thread d'enregistrement
    rec_thread = threading.Thread(target=recording_thread, args=(frame_queue, 'test.mp4'))
    rec_thread.start()

    # Boucle principale : Capture, traitement, contrôle moteurs
    picam2 = init_pycam()


    def main(stdscr): # wrap the main program to get a clean terminal at exit

        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        stdscr.nodelay(True)
        while True:

            frame = picam2.capture_array()
            # Passe une copie du frame à la queue pour enregistrement (sans bloquer)
            if not frame_queue.full():
                frame_queue.put(frame.copy())  # Copie pour éviter modification partagée

            key = stdscr.getch()
            if key == curses.KEY_UP :
                print('En avant')
                tout_droit(speed)
            if key == curses.KEY_LEFT:
                print('à gauche')
                gauche(speed)
            if key == curses.KEY_RIGHT:
                print('à droite')
                droite(speed)
            if key == curses.KEY_DOWN :
                print('STOP')
                stop()
                break

        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        frame_queue.put(None)
        rec_thread.join()
        cv2.destroyAllWindows()

    wrapper(main)

from betterbuildhatmotors import ModelBasedDCMotorController
from picamera2 import Picamera2
import camera
import intersections as inter
import numpy as np

motor_right = ModelBasedDCMotorController('B')
motor_left = ModelBasedDCMotorController('A')
vitesse = 180

def suivi(frame):
    barycentre = inter.get_barycentre(frame, -5)
    print('barycentre est pris' , barycentre)
    if not np.isfinite(barycentre):
        pass
    difference = 640 / 2 - barycentre
    if difference >= 0 :
        #print("à gauche")
        motor_right.set_speed(vitesse)
        motor_left.set_speed(-(vitesse + (-2 * vitesse/200)*difference))
    if difference < 0 :
        #print("à droite")
        motor_left.set_speed(-vitesse)
        motor_right.set_speed(vitesse + (2 * vitesse/200)*difference)
        
if __name__ == '__main__':
    picam2 = camera.init_pycam()#initialisation de la caméra
    motor_left.autotune('left_cal.npy')
    motor_right.autotune('right_cal.npy')
    for i in range(10):
        frame = picam2.capture_array()

    motor_left.start_control_loop()
    motor_right.start_control_loop()
    try:
        while True:
            frame = picam2.capture_array()#prise de l'image qui va être traitée
            suivi(frame)
            
    except KeyboardInterrupt:
        print("on est partis !!!!")
        pass
    finally:
        motor_left.stop()
        motor_right.stop()
        picam2.close()

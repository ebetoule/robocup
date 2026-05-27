from betterbuildhatmotors import ModelBasedDCMotorController
import time
import numpy as np

vitesse = 180

motor_right = ModelBasedDCMotorController('B')
motor_left = ModelBasedDCMotorController('A')

motor_left.autotune('left_cal.npy')
motor_right.autotune('right_cal.npy')

vitesses = {'droit': 0,
            'gauche': 0}
positions = {'droit': 0,
             'gauche': 0}
cibles = {'droit': 0,
          'gauche': 0}
en_marche = True

def droit(vitesse):
    motor_right.set_speed(vitesse)
    
def gauche(vitesse):
    motor_left.set_speed(-vitesse)

    
def stop():
    motor_right.stop()
    motor_left.stop()
    #motor_right.pwm(0)
    #motor_left.pwm(0)
    #motor_right.stop()
    #motor_left.stop()
    
def avancer(vitesse):
    motor_left.set_speed(-vitesse)
    motor_right.set_speed(vitesse)
    #motor_right.pwm(vitesse)
    #motor_left.pwm(-vitesse)
    #vitesses['droit'] = vitesse
    #vitesses['gauche'] = -vitesse
    
def tourner(degres):
    #degres = degres / 0.56
    degres = degres * 1.65
    #motor_left.run_for_degrees(degres, 10, False)
    #motor_right.run_for_degrees(degres, 10, False)
    #stop()
    motor_left.goto(degres, speed=150, accel=1200)
    motor_right.goto(degres, speed=150, accel=1200)
    motor_left.wait()
    motor_right.wait()
    #mouvement(degres, degres)

def aller(distance):
    #dist = distance/0.075
    dist = distance * 13.
    #motor_left.run_for_degrees(-dist, 10, False)
    #motor_right.run_for_degrees(dist, 10, False)
    #stop()
    motor_left.goto(-dist, speed=180, accel=1200)
    motor_right.goto(dist, speed=180, accel=1200)
    motor_left.wait()
    motor_right.wait()
    #mouvement(-dist, dist)

    
def passage_obstacle():
    print('depassement1')
    tourner(-60)
    print('depassement2')
    aller(20)
    print('depassement3')
    tourner(60)
    print('depassement4')
    aller(15)#à ajuster
    print('depassement5')
    tourner(60)
    aller(20)
    tourner(-60)
    
def passage_inter(theta1, theta2, dist):
    tourner(theta1)
    aller(dist)
    tourner(theta2)
    
def demarrer():
    motor_left.start_control_loop()
    motor_right.start_control_loop()
    motor_left.goto(0)
    motor_right.goto(0)
    
if __name__ == '__main__':
    demarrer()


    #avance(4)
    #import numpy as np
    #avancer(500)
    #time.sleep(10)
    #avancer(0)


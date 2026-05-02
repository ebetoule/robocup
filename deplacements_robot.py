from buildhat import Motor
import time
import numpy as np
vitesse = 150

motor_right = Motor('B')
motor_left = Motor('A')

vitesses = {'droit': 0,
            'gauche': 0}
positions = {'droit': 0,
             'gauche': 0}
cibles = {'droit': 0,
          'gauche': 0}
en_marche = True

def droit(vitesse):
#     vitesse = max(vitesse, -100)
#     vitesse = min(vitesse, 100)
#     motor_right.start(vitesse)
#    motor_right.pwm(vitesse)
    vitesses['droit'] = vitesse
    
def gauche(vitesse):
#     vitesse = max(vitesse, -100)
#     vitesse = min(vitesse, 100)
#    motor_left.pwm(-vitesse)
    vitesses['gauche'] = -vitesse
    
def stop():
    global en_marche
    en_marche = False
    time.sleep(0.01)
    motor_right.pwm(0)
    motor_left.pwm(0)
    #motor_right.stop()
    #motor_left.stop()
    
def avancer(vitesse):
    #motor_right.pwm(vitesse)
    #motor_left.pwm(-vitesse)
    vitesses['droit'] = vitesse
    vitesses['gauche'] = -vitesse
    
def tourner(degres):
    #degres = degres / 0.56
    degres = degres * 1.65
    #motor_left.run_for_degrees(degres, 10, False)
    #motor_right.run_for_degrees(degres, 10, False)
    #stop()
    mouvement(degres, degres)

def aller(distance):
    #dist = distance/0.075
    dist = distance * 13.
    #motor_left.run_for_degrees(-dist, 10, False)
    #motor_right.run_for_degrees(dist, 10, False)
    #stop()
    mouvement(-dist, dist)
    
def mouvement(gauche, droit):
    cible_gauche = positions['gauche'] + gauche
    cible_droite = positions['droit'] + droit
    vitesses['gauche'] = vitesse * np.sign(gauche)
    vitesses['droit'] = vitesse * np.sign(droit)
    #print(gauche, droit)
    while vitesses['gauche'] != 0 or vitesses['droit'] != 0:
        if (cible_gauche - positions['gauche']) * np.sign(gauche) <= 0:
            vitesses['gauche'] = 0
            cibles['gauche'] = cible_gauche
        if (cible_droite - positions['droit']) * np.sign(droit) <= 0:
            vitesses['droit'] = 0
            cibles['droit'] = cible_droite
        time.sleep(0.001)
    #print(cible_gauche - positions['gauche'], cible_droite - positions['droit'])
    
def passage_obstacle():
    print('depassement1')
    tourner(-60)
    print('depassement2')
    aller(20)
    print('depassement3')
    tourner(60)
    print('depassement4')
    aller(10)
    print('depassement5')
    tourner(60)
    aller(20)
    tourner(-60)
    
def passage_inter(theta1, theta2, dist):
    tourner(theta1)
    aller(dist)
    tourner(theta2)

def motor_thread(motor, num):
    global vitesses, positions, cibles
    cibles[num] = motor.get_position()
    vieux_time = time.time()
    while en_marche:
        time.sleep(0.001)
        pos = motor.get_position()
        positions[num] = pos
        nouveau_time = time.time()
        cibles[num] += (nouveau_time - vieux_time) * vitesses[num]
        pwm = (cibles[num] - pos) * 0.006
        if pwm > 1:
            pwm = 1
        if pwm < -1:
            pwm = -1
        motor.pwm(pwm)
        vieux_time = nouveau_time
    motor.pwm(0)
    
def demarrer():
    global en_marche
    import threading
    speed = 0
    en_marche = True
    t1 = threading.Thread(target=motor_thread, args=(motor_right, 'droit'), daemon=True)
    t1.start()
    t2 = threading.Thread(target=motor_thread, args=(motor_left, 'gauche'), daemon=True)
    t2.start()
    
if __name__ == '__main__':
    demarrer()


    #avance(4)
    #import numpy as np
    #avancer(500)
    #time.sleep(10)
    #avancer(0)


from buildhat import Motor

vitesse = 20
motor_right = Motor('D')
motor_left = Motor('C')

def droit(vitesse):
#     vitesse = max(vitesse, -100)
#     vitesse = min(vitesse, 100)
#     motor_right.start(vitesse)
    motor_right.pwm(vitesse)
    
def gauche(vitesse):
#     vitesse = max(vitesse, -100)
#     vitesse = min(vitesse, 100)
    motor_left.pwm(-vitesse)
    
def stop():
    motor_right.stop()
    motor_left.stop()
    
def avancer(vitesse):
    motor_right.pwm(vitesse)
    motor_left.pwm(-vitesse)
    
def tourner(degres):
    degres = degres / 0.56
    motor_left.run_for_degrees(degres, 10, False)
    motor_right.run_for_degrees(degres, 10, False)
    stop()

def aller(distance):
    dist = distance/0.075
    motor_left.run_for_degrees(-dist, 10, False)
    motor_right.run_for_degrees(dist, 10, False)
    stop()
    
def passage_inter(theta1, theta2, dist):
    tourner(theta1)
    aller(dist)
    tourner(theta2)
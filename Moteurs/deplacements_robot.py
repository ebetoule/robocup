from buildhat import Motor

vitesse = 20
motor_right = Motor('A')
motor_left = Motor('B')

def droit(vitesse):
    vitesse = max(vitesse, -100)
    vitesse = min(vitesse, 100)
    motor_right.start(vitesse)
    
def gauche(vitesse):
    vitesse = max(vitesse, -100)
    vitesse = min(vitesse, 100)
    motor_left.start(-vitesse)
    
def stop():
    motor_right.stop()
    motor_left.stop()
    
def avancer(vitesse):
    motor_right.start(vitesse)
    motor_left.start(-vitesse)
import buildhat
from buildhat import Motor

motor_right = Motor('A')
motor_left = Motor('B')
speed = 50

def tout_droit(speed):
    motor_right.start(speed)
    motor_left.start(-speed)

def gauche(speed):
    motor_right.start(speed)
    motor_left.start(speed)
    
def droite(speed):
    motor_right.start(-speed)
    motor_left.start(-speed)
    
def stop():
    motor_right.stop()
    motor_left.stop()

while True:
    key = input()
    if key =='a' :
        print('En avant')
        tout_droit(speed)
    if key == 'g':
        print('à gauche')
        gauche(speed)
    if key == 'd':
        print('à droite')
        droite(speed)
    if key == 's' :
        print('STOP')
        stop()
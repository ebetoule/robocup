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
        s.write(b'C30\n')
    if key == 'g':
        print('à gauche')
        s.write(b'A0\n')
        s.write(b'B30\n')
    if key == 'd':
        print('à droite')
        s.write(b'A30\n')
        s.write(b'B0\n')
    if key == 's' :
        print('STOP')
        s.write(b'C0\n')
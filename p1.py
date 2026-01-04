import serial
import cv2
from picamera2 import Picamera2

s = serial.Serial(port='/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0', baudrate=115200)


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
    if key == 'v' :
        picam2 = Picamera2()
        picam2.preview_configuration.main.size = (1280,720)
        picam2.preview_configuration.main.format = "RGB888"
        picam2.preview_configuration.align()
        picam2.configure("preview")
        picam2.start()
        fourcc = cv2.VideoWriter_fourcc('M', 'P', 'G', '4')
        out = cv2.VideoWriter('Vidéos/enregistrement.mp4', fourcc, 20.0, (1280, 720))
        while True:
                
            out.write(im)
            cv2.imshow("Camera", im)
            if cv2.waitKey(1)==ord('q'):
                break
        cv2.destroyAllWindows()
        out.release
        #video = cv2.import serial
import cv2VideoCapture(cv2.CAP_V4L2)#v0)
        #frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        #frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        #out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))
        #while (video.isOpened()):
            #print(cv2.getBuildInformation())
            #ret, frame = video.read()

            #if ret == True:
                # Write the frame to the output file
                #out.write(frame)
                #print(frame.shape)
                # Display the captured frame
                #if cv2.waitKey(1) == ord('q'):
                    #break
            #else:
                #print("cannot read")
                #break
    #if key == 'k' :
        #cam.release()
        #out.release()




from picamera2 import Picamera2
import matplotlib.pyplot as plt
import cv2 as cv
picam2 = Picamera2()



sensor_modes = picam2.sensor_modes
nom = 10

mode = sensor_modes[1]
#print(f'Mode du capteur: {mode}')
config = picam2.create_still_configuration(sensor={'output_size': mode['size'], 'bit_depth': mode['bit_depth']})
                                               #main={'size': size})
picam2.configure(config)
picam2.start()

nx = 6
ny = 6 
while True:
    #cv.waitKey(5)
    #time.sleep(10)
    frame = picam2.capture_array()
    frame = cv.resize(frame, [640, 480])
    #print(frame.shape)
    #k =input()
    cv.imshow('', frame)
    cv.waitKey(5)
    cv.destroyAllWindows()
    print("Essai de prise d'image: ", nom)
    #images = glob.glob('chess/*.jpg')
    #for fname in images:
    #print(f"processing {fname}")
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (ny,nx), cv.CALIB_CB_FAST_CHECK)
    # If found, add object points, image points (after refining them)
    if ret == True:
        nom = nom + 1
        cv.imwrite(f'ccn{nom}.jpg',frame)
        print("OK")
    else:
        print("On recommence")
    if nom > 20:
        break

picam2.stop()
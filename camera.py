from picamera2 import Picamera2
import matplotlib.pyplot as plt
import cv2
from pprint import pprint
size = (640, 480)
def init_pycam():
    picam2 = Picamera2()
    mode = picam2.sensor_modes[5]
    config = picam2.create_still_configuration(
        sensor={'output_size': mode['size'], 'bit_depth': mode['bit_depth']},
        buffer_count=2,
        main={'size':size, "format": "RGB888"}
        #controls={'FrameRate': 50},
    )
    picam2.configure(config)#"preview")
    print(picam2.camera_configuration())
    picam2.start()
    return picam2

if __name__=="__main__":
    picam2 = Picamera2()
    sensor_modes = picam2.sensor_modes
    pprint(sensor_modes)

    while True:
        mode_num = int(input("Mode:"))
        #size = int(input("Width:")), int(input("height:"))
        mode = sensor_modes[mode_num]
        print(f'Mode du capteur: {mode}')
        config = picam2.create_still_configuration(sensor={'output_size': mode['size'], 'bit_depth': mode['bit_depth']})
                                                   #main={'size': size})
        print(config)
        picam2.configure(config)
        picam2.start()
        frame = picam2.capture_array()

        #cv2.imshow('', frame)
        #plt.imshow(frame)
        cv2.imwrite('ccn7.jpg',frame)
        #cv2.imshow('ccn', frame)
        picam2.stop()

# def config1():
#     config = picam2.create_still_configuration(
#         {#'format': SRGGB10_CSI2P,
#          #'unpacked':'SRGGB10',
#          #'bit_depth': 10,
#          'size': (640, 480),
#          'fps': 103.33,
#          'crop_limits': (1000, 752, 1280, 960),
#          'exposure_limits': (75, 1238765, 20000)}
#         )
#     picam2.configure(config)#"preview")
#     picam2.start()
#     return picam2
# def config2():
#     config = picam2.create_still_configuration(
#         {'format': SRGGB10_CSI2P, 'unpacked': 'SRGGB10', 'bit_depth': 10, 'size': (1640, 1232), 'fps': 41.85, 'crop_limits': (0, 0, 3280, 2464), 'exposure_limits': (75, 1238765, 20000)}
#         )
#     picam2.configure(config)#"preview")
#     picam2.start()
#     return picam2
# 
# def config3():
#     config = picam2.create_still_configuration(
#         {'format': SRGGB10_CSI2P, 'unpacked': 'SRGGB10', 'bit_depth': 10, 'size': (1920, 1080), 'fps': 47.57, 'crop_limits': (680, 692, 1920, 1080), 'exposure_limits': (75, 1238765, 20000)}
#         )
#     picam2.configure(config)#"preview")
#     picam2.start()
#     return picam2
# def config4():
#     config = picam2.create_still_configuration(
#         {'format': SRGGB10_CSI2P, 'unpacked': 'SRGGB10', 'bit_depth': 10, 'size': (3280, 2464), 'fps': 21.19, 'crop_limits': (0, 0, 3280, 2464), 'exposure_limits': (75, 1238765, 20000)}
#         )
#     picam2.configure(config)#"preview")
#     picam2.start()
#     return picam2
# def config5():
#     config = picam2.create_still_configuration(
#         {'format': SRGGB8, 'unpacked': 'SRGGB8', 'bit_depth': 8, 'size': (640, 480), 'fps': 103.33, 'crop_limits': (1000, 752, 1280, 960), 'exposure_limits': (75, 1238765, 20000)}
#         )
#     picam2.configure(config)#"preview")
#     picam2.start()
#     return picam2
# def config6():
#     config = picam2.create_still_configuration(
#         {'format': SRGGB8, 'unpacked': 'SRGGB8', 'bit_depth': 8, 'size': (1640, 1232), 'fps': 41.85, 'crop_limits': (0, 0, 3280, 2464), 'exposure_limits': (75, 1238765, 20000)}
#         )
#     picam2.configure(config)#"preview")
#     picam2.start()
#     return picam2
# def config7():
#     config = picam2.create_still_configuration(
#         {'format': SRGGB8, 'unpacked': 'SRGGB8', 'bit_depth': 8, 'size': (1920, 1080), 'fps': 47.57, 'crop_limits': (680, 692, 1920, 1080), 'exposure_limits': (75, 1238765, 20000)}
#         )
#     picam2.configure(config)#"preview")
#     picam2.start()
#     return picam2
# def config8():
#     config = picam2.create_still_configuration(
#         {'format': SRGGB8, 'unpacked': 'SRGGB8', 'bit_depth': 8, 'size': (1920, 1080), 'fps': 47.57, 'crop_limits': (680, 692, 1920, 1080), 'exposure_limits': (75, 1238765, 20000)}
#         )
#     picam2.configure(config)#"preview")
#     picam2.start()
#     return picam2
# 


from picamera2 import Picamera2

def init_pycam():
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"size": size,"format": "RGB888"}, # scale down the image, but maintain the full field of view
        raw={'size': (3280, 2464)},
        buffer_count=2,
        #controls={'FrameRate': 50},
    )
    picam2.configure(config)#"preview")
    picam2.start()
    return picam2
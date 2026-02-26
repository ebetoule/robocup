import cv2

image = cv2.imread('ccn11.jpg')

def obtenir_coord(action, x, y, flags, userdata):
    if action == cv2.EVENT_LBUTTONDBLCLK:
        print(x, y)
    

while True:
    cv2.imshow('coucou', image)
    cv2.setMouseCallback('coucou', obtenir_coord)
    key = cv2.waitKey(0)
    if key == ord('k'):
        break
cv2.destroyAllWindows()
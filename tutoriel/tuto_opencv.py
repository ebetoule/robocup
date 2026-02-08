import cv2
size = (640,480)
image = cv2.imread('test.jpg',-1)
image = cv2.resize(image, [640, 480])
img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#convertir image
# apply binary thresholding
ret, thresh = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY)
# voir l'image
cv2.imshow('Binary image', thresh)
cv2.waitKey(0)
cv2.imwrite('image_thres1.jpg', thresh)
cv2.destroyAllWindows()

# detect the contours on the binary image using cv2.CHAIN_APPROX_NONE
contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
print(hierarchy)                                      
# draw contours on the original image
image_copy = image.copy()
cv2.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
                
# see the results
cv2.imshow('None approximation', image_copy)
cv2.waitKey(0)
cv2.imwrite('contours_none_image1.jpg', image_copy)
cv2.destroyAllWindows()
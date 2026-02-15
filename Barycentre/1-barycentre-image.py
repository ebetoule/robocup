import cv2
image = cv2.imread('data/test.jpg',-1)
img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ret, tabimage = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY)

dim_y, dim_x = tabimage.shape
milieu = dim_x // 2

tabimage[0:10, milieu] = 128

#cv2.imshow('Binary image', tabimage)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

#transformer en noir et blanc

tabimage01 = tabimage.copy()
tabimage01[tabimage==255] = 0
tabimage01[tabimage==0] = 1
#définir les valeurs


print(tabimage.shape)#afficher dimensions(x=2464, y=3280)

for u in range(1, 11):
    barycentre = 0
    denominateur = 0
    for i in range(dim_x):
        barycentre = barycentre + i * tabimage01[-u,i]
        denominateur = denominateur + tabimage01[-u,i]
    barycentre = barycentre / denominateur
    print(barycentre)
    if barycentre == milieu:
        print("tout droit")
    if barycentre > milieu:
        print("à gauche")
    if barycentre < milieu:
        print("à droite")



#print(barycentre)
#print(denominateur)
#print(barycentre / denominateur)
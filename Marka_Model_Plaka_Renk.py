import cv2
from PIL import Image
import numpy as np
import imutils
import pytesseract
import re
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing import image
import matplotlib.pyplot as plt
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.layers import Dropout
from keras import optimizers
from keras.models import load_model
import sqlite3


classifier = load_model('model_600_450_32_categorical.h5')


img_path = 'C:/Users/MacBookPro/Desktop/Drive/plaka&renk_tespit/d (9).jpg'
image_color = cv2.imread('C:/Users/MacBookPro/Desktop/Drive/plaka&renk_tespit/d (9).jpg',cv2.IMREAD_COLOR)
img_plaka = cv2.imread('C:/Users/MacBookPro/Desktop/Drive/plaka&renk_tespit/d (9).jpg',cv2.IMREAD_COLOR)

# `img` is a PIL image of size 224x224
img = image.load_img(img_path, target_size=(600, 450))
# `x` is a float32 Numpy array of shape (224, 224, 3)
x = image.img_to_array(img)
# We add a dimension to transform our array into a "batch"
# of size (1, 224, 224, 3)
x = np.expand_dims(x, axis=0)
array = classifier.predict(x)



predicted_class_indices=np.argmax(array,axis=1)
#print(predicted_class_indices)
if predicted_class_indices == 0:
    marka_m = "2012_2014_Ford Focus Ön"
    print("Araç Marka Model:",marka_m)
if predicted_class_indices == 1:
    marka_m = "2012_2014_Ford Focus Arka"
    print("Araç Marka Model:",marka_m)
if predicted_class_indices == 2:
    marka_m = "2016_2019_Honda Civic Ön"
    print("Araç Marka Model:",marka_m)
if predicted_class_indices == 3:
    marka_m = "2016_2019_Honda Civic Arka"
    print("Araç Marka Model:",marka_m)


#image_color = cv2.imread('C:/Users/MacBookPro/Desktop/Drive/renk_tespit/honda (1).jpg',cv2.IMREAD_COLOR)
image_color = cv2.resize(image_color, (600,450))
cropped_1 = image_color[100:250, 100:350]  #birinci y ikinci x
b_1 = int(cropped_1.item(100, 100, 0))
g_1 = int(cropped_1.item(100, 100, 1))
r_1 = int(cropped_1.item(100, 100, 2)) 
  
cropped_2 = image_color[100:250, 350:600]
b_2 = int(cropped_2.item(100, 100, 0))
g_2 = int(cropped_2.item(100, 100, 1))
r_2 = int(cropped_2.item(100, 100, 2)) 


cv2.imshow("Crop_Image_1", cropped_1)
cv2.imshow("Crop_Image_2", cropped_2)  
 

#print(b_1, g_1, r_1)
#print(b_2, g_2, r_2)


ort_b = int((b_1)+(b_2))/2
ort_g = int((g_1)+(g_2))/2
ort_r = int((r_1)+(r_2))/2

#print("ort_renk", ort_b, ort_g, ort_r)

renkdizi = [b_1, g_1, r_1]

#print(max(renkdizi))



if (180<=ort_b and ort_b<255 and 180<=ort_g and ort_g<255 and 170<=ort_r and ort_r<255):
    arac_r = "Beyaz"
    print("Aracın Rengi    :",arac_r)
    
elif (110<ort_b and ort_b<150 and 110<ort_g and ort_g<150 and 110<ort_r and ort_r<150):
    arac_r = "Füme"
    print("Aracın Rengi    :",arac_r)   
    
elif (150<ort_b and ort_b<180 and 150<ort_g and ort_g<180 and 150<ort_r and ort_r<170):
    arac_r = "Gri"
    print("Aracın Rengi    :",arac_r)       
    
elif (130<ort_b and ort_b<255 and 25<ort_g and ort_g<150 and 0<ort_r and ort_r<150):
    arac_r = "Lacivert"
    print("Aracın Rengi    :",arac_r)

elif (0<ort_b and ort_b<150 and 0<ort_g and ort_g<150 and 100<ort_r and ort_r<255):
    arac_r = "Kırmızı"
    print("Aracın Rengi    :",arac_r)
       
elif (ort_b<=110 and ort_g<110 and ort_r<110):
    arac_r = "Siyah"
    print("Aracın Rengi    :",arac_r)
     
#img_plaka = cv2.resize(img_plaka, (620,480))
gray = cv2.cvtColor(img_plaka, cv2.COLOR_BGR2GRAY) #convert to grey scale
cv2.imshow("1 - Grayscale Conversion", gray)

gray = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise
cv2.imshow("2 - Bilateral Filter", gray)

edged = cv2.Canny(gray, 30, 200) #Perform Edge detection
cv2.imshow("3 - Canny Edges", edged)


# find contours in the edged image, keep only the largest
# ones, and initialize our screen contour
cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
screenCnt = None

# loop over our contours
for c in cnts:
	# approximate the contour
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
 
	# if our approximated contour has four points, then
	# we can assume that we have found our screen
	if len(approx) == 4:
		screenCnt = approx
		break



if screenCnt is None:
	detected = 0
	print ("No contour detected")
else:
	detected = 1

if detected == 1:
	cv2.drawContours(img_plaka, [screenCnt], -1, (0, 255, 0), 2)

# Masking the part other than the number plate
mask = np.zeros(gray.shape,np.uint8)
new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
new_image = cv2.bitwise_and(img_plaka,img_plaka,mask=mask)

# Now crop
(x, y) = np.where(mask == 255)
(topx, topy) = (np.min(x), np.min(y))
(bottomx, bottomy) = (np.max(x), np.max(y))
Cropped = gray[topx:bottomx+1, topy:bottomy+1]


cv2.imshow("4 - Final ",img_plaka)
cv2.imshow("Tespit Edilen Plaka",Cropped)


#Read the number plate
t_plaka = pytesseract.image_to_string(Cropped, config='--psm 11')


connectdb=sqlite3.connect('test.db')
im=connectdb.cursor()
  

#mm=str(marka_m)

plk = re.sub('\ |\?|\.|\!|\/|\\|\;|\:|\‘|\(|\)|\-|\{|\}|\]|\[|\&|\,|\’|\||\»|\¢|\*|\§|\°|','',t_plaka)
print("Aracın Plakası  :",plk)

im.execute("SELECT * FROM kayitli_araclar where marka_model='"+marka_m+"' and plaka='"+plk+"' and renk='"+arac_r+"'")
           
data = im.fetchone()

if data:
    print("Araç Marka Model, Plaka ve Renk Bilgisi Eşleşti...".format(data[0]))
else:
    print("Eşleşme Başarısız..!")

cv2.waitKey(0)
cv2.destroyAllWindows()




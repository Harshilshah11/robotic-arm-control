import cv2 
import numpy as np

# img = cv2.imread("fruits.jpg")

# img_gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# cv2.imshow("window",img_gray)

# Channel Seperation 

# imgBlue=img[:,:,0]
# imgGreen=img[:,:,1]
# imgRed=img[:,:,2]

# new_img=np.hstack((imgBlue,imgGreen,imgRed))

# cv2.imshow("window",new_img) 

# Resize image 

# img_resize=cv2.resize(img,(256,256))
# cv2.imshow("window",img_resize) 

# img_resize=cv2.resize(img,(img.shape[1]//2,img.shape[0]//2))
# cv2.imshow("window",img_resize) 

# Flip image 

# img_flip=cv2.flip(img,1)
# cv2.imshow("window",img_flip) 

# Crop image 
# img_crop=img[30:150,0:200]
# cv2.imshow("window",img_crop) 

# Save image 
# img_save=cv2.imwrite("fruits_small.jpg",img)

#  Drawing Shapes and Text on Images

# img=np.zeros((512,512,3))
# cv2.rectangle(img, (100,100), (300,300), (255,0,0), 1)
# cv2.circle(img,center=(256,256),radius=100,color=(0,0,255),thickness=3)
# cv2.line(img,(100,100), (400,400), color=(0,0,255),thickness=3)
# cv2.putText(img,org=(250,250),fontScale=4,color=(0,255,255),thickness=2,lineType=cv2.LINE_AA,text="Hello World",fontFace=cv2.FONT_ITALIC)

# cv2.imshow("window",img)

# Events 

drawing=False
flag = False
ix=-1
iy=-1
def draw(event,x,y,flags,parameters):
    global flag,ix,iy 
    if event == 1:
        flag=True
        ix=x
        iy=y
    elif event == 0:
        if flag == True :
           cv2.rectangle(img, (ix,iy), (x,y), (255,0,0), -1)      
    elif event == 4:
        flag=False
        cv2.rectangle(img, (ix,iy), (x,y), (255,0,0), -1) 
    
cv2.namedWindow(winname="window")
cv2.setMouseCallback("window",draw)

img=np.zeros((512,512,3))

while True:
    
    cv2.imshow("window",img)

    if cv2.waitKey(1) & 0xFF==ord('x'):
        break 
    
cv2.destroyAllWindows()

# cv2.waitKey(0)
'''
Created on Dec 13, 2017

@author: davide
'''        
import numpy as np
import cv2
import time
from math import sqrt

def find_center(coord):
    x1,y1,x2,y2 = coord
    return ((x1+x2)/2, (y1+y2)/2)
    
def dist(x1,x2,y1,y2):
    return sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))
    
def quadrant(img_size, target, resolution = (3,3)):
    x_img, y_img = img_size
    x_res, y_res = resolution
    x_target, y_target = find_center(target)
    x_unit = x_img/x_res
    y_unit = y_img/y_res
    x_q = round(x_target/x_unit)
    y_q = round(y_target/y_unit)
    return (x_q,y_q)
    
def distance_from_center(img_size, obj_position):
    x_img, y_img = img_size
    x_cent, y_cent = find_center((0,0,x_img, y_img))
    x_obj, y_obj = obj_position
    if(obj_position == (0,0)):
        x_obj, y_obj = x_cent, y_cent
    return (x_obj-x_cent)*1.0/x_img, (y_cent-y_obj)*1.0/y_img
    
def choose_face(list_of_faces, previous_center = None, criterium = 0):
    if(len(list_of_faces) > 0):
        if(criterium == 0):  #CRITERIUM 0: BIGGEST AREA
            x,y,w,h = list_of_faces[0]
            for e in list_of_faces:
                if(e[2]*e[3] > h*w):
                    x,y,w,h = e
        if(previous_center is not None and criterium == 1): #CRITERIUM 2: CLOSENESS TO PREVIOUS
            x,y,w,h = list_of_faces[0]
            min_dist = dist((find_center((x,y,x+w,y+h))), (previous_center))
            for e in list_of_faces:
                new_dist = dist((find_center((e[0],e[1],e[0]+e[2],e[1]+e[3]))), previous_center)
                if(new_dist < min_dist):
                    x,y,w,h = e
                    min_dist = new_dist
        return x,y,w,h
    return  0,0,0,0

class compass:
    def __init__(self, criterium = 0, do_show_image = True):
        self.face_cascade = cv2.CascadeClassifier('haar_frontal_face.xml')
#         self.cap = cv2.VideoCapture(0)
#         ret, image = self.cap.read()
#         self.width = image.shape[0]
#         self.heigth = image.shape[1]
        self.last_face = (0,0,0,0)
        self.last_face_center = find_center(self.last_face)
        self.criterium = criterium
        self.do_show_image = do_show_image
        
        
    def direction2center(self, image = None, return_image = False):
        x,y,w,h = self.last_face
        if image is None:
            ret, image = self.cap.read()
        res_image = image
        self.width = image.shape[0]
        self.heigth = image.shape[1]
        gray = cv2.cvtColor(res_image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)
        x,y,w,h = choose_face(faces, self.last_face_center, criterium = self.criterium)
        
#         cv2.rectangle(res_image,(x,y),(x+w,y+h),(255,0,0),2)
        # Our operations on the frame come here
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Display the resulting frame

        if cv2.waitKey(1) & 0xFF == ord('q'):
            raise SystemExit("Someone wants to quit")
        x_f, y_f = find_center([x,y,x+w,y+h])
        cv2.circle(image, find_center((0,0,self.heigth, self.width)), radius = 20, color = np.array([0,255,255]))
        cv2.circle(image, (x_f,y_f), radius = 20, color = np.array([0,0,255]))
        if self.do_show_image:
            cv2.imshow('frame',res_image)
        if(w*h > 0):
            self.last_face = (x,y,w,h)
            self.last_face_center = find_center(self.last_face)
        tmp1, tmp2 = distance_from_center((self.heigth, self.width), (x_f, y_f))
        if(return_image):
            return tmp1, tmp2, w*h, image
        return distance_from_center((self.heigth, self.width), (x_f, y_f)) , w*h

if __name__ == "__main__":
    c = compass(0)
    count = 0
    folder = "./21071213_img_zoheb_proj/"
    start_10 = time.clock()
    for i in [0,1,2,3]:
        img = cv2.imread(folder + "IMG" + str(i) + ".jpg")
        ret_dir2c = c.direction2center(img,True)
        cv2.imwrite(folder + "det_IMG" + str(i) + ".jpg", img)
        
        
        
        
        
        
        
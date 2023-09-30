import numpy as np 
import cv2 
import dlib 
import math
from math import degrees
from scipy.spatial import distance 
from glob import glob
import os

# imagepath = glob("./test/*.jpg") # 이미지 경로
# 다운로드 링크 = https://github.com/opencv/opencv/tree/master/data/haarcascades
face_cascade_path = "./haarcascade_frontalface_default.xml" # "haarcascade_frontalface_default.xml" 경로
# 다운로드 링크 = http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
predictor_path = "./shape_predictor_68_face_landmarks.dat" # "shape_predictor_68_face_landmarks.dat" 경로

faceCascade = cv2.CascadeClassifier(face_cascade_path)
predictor = dlib.shape_predictor(predictor_path)

def get_faceshape(imagepath):
    imagepath = glob(imagepath)
    for path in imagepath:
        name = os.path.basename(path)
        image = cv2.imread(path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gauss = cv2.GaussianBlur(gray,(3,3), 0)

        # 얼굴 탐지
        faces = faceCascade.detectMultiScale(
            gauss,
            scaleFactor=1.05,
            minNeighbors=5,
            minSize=(100,100),
            flags=cv2.CASCADE_SCALE_IMAGE
            )
        # 얼굴 탐지 여부
        for i in range(1):
            if len(faces) >= 2:
                return "2명 이상"
            elif len(faces) == 0:
                return "얼굴 X"
            else:
                (x,y,w,h) = faces[0]
                # facelandmark 탐지
                dlib_rect = dlib.rectangle(int(x), int(y), int(x+w), int(y+h))
                detected_landmarks = predictor(image, dlib_rect).parts()
                landmarks = np.matrix([[p.x,p.y] for p in detected_landmarks])
                for idx, point in enumerate(landmarks):
                    pos = (point[0,0], point[0,1] )
                    cv2.circle(image, pos, 3, color=(0,255,255))

                # 미간
                center = (int((landmarks[22,0]+landmarks[21,0])/2), int((landmarks[22,1]+landmarks[21,1])/2))

                # 이마 끝
                x1 = landmarks[8, 0] - center[0]
                y1 = landmarks[8, 1] - center[1]
                y2 = center[1] - y
                x2 = (x1*y2)/y1
                forehead_end = (int(center[0]-x2), int(y))

                # 세로(이마 끝 - 턱 끝)
                top = forehead_end
                bottom = (landmarks[8,0],landmarks[8,1])
                dis_hei = distance.euclidean(bottom,top)
                # cv2.line(image, top, bottom,color=(0,255,0), thickness = 2)

                # 가로
                left = (landmarks[0,0],landmarks[0,1])
                right = (landmarks[16,0],landmarks[16,1])
                dis_wid = distance.euclidean(right,left)
                # cv2.line(image, left, right, color=(0,255,0), thickness = 2)

                # 가로2
                left = (landmarks[2,0],landmarks[2,1])
                right = (landmarks[14,0],landmarks[14,1])
                dis_wid2 = distance.euclidean(right,left)
                # cv2.line(image, left, right, color=(0,255,0), thickness = 2)

                # 왼쪽 턱 각도
                angle_list = []
                for i in [1,2,3,4,5]:
                    ax,ay = landmarks[0,0],landmarks[0,1]
                    bx,by = landmarks[i,0],landmarks[i,1]
                    cx,cy = landmarks[8,0],landmarks[8,1]
                    alpha0 = math.atan2(by-ay,bx-ax)
                    alpha1 = math.atan2(cy-by,cx-bx)
                    alpha = alpha1-alpha0
                    angle = abs(degrees(alpha))
                    angle = 180-angle
                    angle_list.append(angle)
                for i in [15,14,13,12,11]:
                    ax,ay = landmarks[16,0],landmarks[16,1]
                    bx,by = landmarks[i,0],landmarks[i,1]
                    cx,cy = landmarks[8,0],landmarks[8,1]
                    alpha0 = math.atan2(by-ay,bx-ax)
                    alpha1 = math.atan2(cy-by,cx-bx)
                    alpha = alpha1-alpha0
                    angle = abs(degrees(alpha))
                    angle = 180-angle
                    angle_list.append(angle)
                # print(min(angle_list))
                
                if dis_wid/dis_hei <= 0.75:
                    return "긴 얼굴형"
                else:
                    if min(angle_list) <= 126:
                        return "각진 얼굴형"
                    elif min(angle_list) >= 140:
                        return "역삼각 얼굴형"
                    else:
                        if dis_wid2/dis_hei >=0.76:
                            return "둥근 얼굴형"
                        else:
                            return "계란 얼굴형"

                # cv2.imshow('output',image)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
# from msvcrt import LK_LOCK
from re import S
from imutils import face_utils
import numpy as np
import dlib
import cv2

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

glasses = "glasses/circle/1.png"
image = "faceset/woman/taehee.jpg" # 이미지 경로 입력

def get_glass_img(image, glasses, filename):
    img_glasses = cv2.imread(glasses, cv2.IMREAD_UNCHANGED)
    img_face = cv2.imread(image, cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(img_face, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)

    for (i, rect) in enumerate(rects):
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        (x, y, w, h) = face_utils.rect_to_bb(rect) 
    H, W, _ = img_face.shape
    img_rgb = cv2.cvtColor(img_face, cv2.COLOR_RGBA2RGB)
    rects = detector(img_rgb)
    if len(rects) == 0:
        return "no face detected"
    rect = rects[0]
    landmarks_dlibtype = predictor(img_rgb, rect)

    landmarks = []

    for j in range(68):
        landmarks.append([landmarks_dlibtype.part(j).x, landmarks_dlibtype.part(j).y])
    landmarks = np.array(landmarks)     

    mid_ver = landmarks[40][1]
    mid_hor = landmarks[27][0]
    wei = 2*min((landmarks[16][0]-mid_hor), (mid_hor-landmarks[0][0]))

    h, w = img_glasses.shape[:2]
    hei = (h*wei)//w
    img_glasses = cv2.resize(img_glasses, (wei, hei))

    _, mask = cv2.threshold(img_glasses[:,:,3], 1, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    img_glasses = cv2.cvtColor(img_glasses, cv2.COLOR_BGRA2BGR)
    roi = img_face[mid_ver-(hei//2):mid_ver-(hei//2)+hei, mid_hor-(wei//2):mid_hor-(wei//2)+wei]

    masked_fg = cv2.bitwise_and(img_glasses, img_glasses, mask=mask)
    masked_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

    added = masked_fg + masked_bg
    img_face[mid_ver-(hei//2):mid_ver-(hei//2)+hei, mid_hor-(wei//2):mid_hor-(wei//2)+wei] = added

    cv2.imwrite('static/result/{}.jpg'.format(filename), img_face)
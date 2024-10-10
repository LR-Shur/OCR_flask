from numpy.ma.core import shape

from ocr.detect_yolo import detect_yolo
from ocr.detect_ocr_Cnocr import detect_ocr
import cv2
import numpy as np
def detect_interface(image):
    # 读取图像
    # image = cv2.imread(image_path)

    # cv2.imshow( "image", image)


    # 检测是否有物体
    list1 = detect_yolo(image)
    if list1 == -1:
        print("没检测出来有身份证")
        return "没检测出来有身份证"
    if list1 == -2:
        print("身份证数量大于一")
        return "身份证数量大于一"

    if list1 == -3:
        shape = image.shape
        image = np.rot90(image, 1)
        size = image.shape
        image = cv2.resize(image, (size[1], size[0]), interpolation=cv2.INTER_AREA)
        list1 = detect_yolo(image)





    image1 = image[int(list1[0][1]):int(list1[2][1]),int(list1[0][0]):int(list1[1][0])]

    result = detect_ocr(image1)
    return result





if(__name__=="__main__"):
    path =r'../sources/images/12.jpg'
    detect_interface(path)
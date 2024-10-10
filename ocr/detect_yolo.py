from ultralytics import YOLO
import cv2
import numpy as np


#-1: no object detected, -2: more than one object detected
def detect_yolo(image):
    model = YOLO('../sources/models/best.pt')
    results = model(image)
    boxes=results[0].boxes
    if(len(boxes)==0):
        return -1;
    if(len(boxes)>1):

        return -2;

    box=boxes[0]
    # 获取边界框坐标 (x_center, y_center, width, height)
    x_center, y_center, width, height = box.xywh[0].tolist()

    # 计算矩形四个角点
    x_min = x_center - width / 2
    y_min = y_center - height / 2
    x_max = x_center + width / 2
    y_max = y_center + height / 2

    # 矩形的四个角点坐标
    top_left = (x_min, y_min)
    top_right = (x_max, y_min)
    bottom_right = (x_max, y_max)
    bottom_left = (x_min, y_max)

    if(height>width):
        return -3
    list1=[top_left,top_right,bottom_right,bottom_left,width,height]
    return list1


if(__name__=="__main__"):
    path =r'../sources/images/11.jpg'

    # 读取图像
    image = cv2.imread(path)
    shape = image.shape
    if shape[0] > shape[1]:
        dst = np.rot90(image, 1)
    size = dst.shape
    image = cv2.resize(dst, (size[1], size[0]), interpolation=cv2.INTER_AREA)


    list1 = detect_yolo(image)
    print(list1)

    # 将坐标转化为 NumPy 数组，并格式化为 (x, y) 的形状
    points = np.array(list1[:4], np.int32)

    # 绘制多边形框，isClosed=True 表示绘制闭合多边形
    cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=2)

    # 显示或保存绘制后的图像
    cv2.imshow("Image with Box", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print(list1[-2]/list1[-1])



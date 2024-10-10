from ultralytics import YOLO
import cv2
import numpy as np


# -1: no object detected
def detect_yolo(image):
    model = YOLO('../sources/models/best.pt')
    results = model(image)
    boxes = results[0].boxes  # 获取检测到的边界框
    return boxes  # 返回检测到的框


def draw_boxes(image, boxes):
    for box in boxes:
        x_center, y_center, width, height = box.xywh[0].tolist()
        x_min = int(x_center - width / 2)
        y_min = int(y_center - height / 2)
        x_max = int(x_center + width / 2)
        y_max = int(y_center + height / 2)

        print(x_min, y_min, x_max, y_max)
        # 画出矩形框
        # cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

    return image


if __name__ == "__main__":
    path = r'../sources/images/9.jpg'

    # 读取图像
    image = cv2.imread(path)
    if image is None:
        print("Error: Image not found.")
        exit(1)

    shape = image.shape
    if shape[0] > shape[1]:
        image = np.rot90(image, 1)  # 如果高度大于宽度，顺时针旋转90度

    boxes = detect_yolo(image)  # 获取检测结果
    if len(boxes) > 0:

        image_with_boxes = draw_boxes(image, boxes)  # 绘制所有边界框
        cv2.imshow("Image with Boxes", image_with_boxes)  # 显示结果
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No objects detected.")

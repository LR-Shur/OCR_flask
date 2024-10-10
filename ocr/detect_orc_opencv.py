import cv2
import numpy as np
from cnocr import CnOcr
from detect_yolo import detect_yolo

def show(image, window_name):
    cv2.namedWindow(window_name, 0)
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



def preprocessing(image):
    show(image, "image")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    show(gray, "gray")

    blur = cv2.medianBlur(gray, 7)
    show(blur, "blur")

    threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    show(threshold, "threshold")

    canny = cv2.Canny(threshold, 100, 150)
    show(canny, "canny")

    kernel = np.ones((3, 3), np.uint8)
    dilate = cv2.dilate(canny, kernel, iterations=5)
    show(dilate, "dilate")

    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    image_copy = image.copy()
    res = cv2.drawContours(image_copy, contours, -1, (255, 0, 0), 20)
    show(res, "res")

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[0]
    image_copy = image.copy()
    res = cv2.drawContours(image_copy, contours, -1, (255, 0, 0), 20)
    show(res, "contours")

    epsilon = 0.02 * cv2.arcLength(contours, True)
    approx = cv2.approxPolyDP(contours, epsilon, True)
    n = []
    for x, y in zip(approx[:, 0, 0], approx[:, 0, 1]):
        n.append((x, y))
    n = sorted(n)
    sort_point = []
    n_point1 = n[:2]
    n_point1.sort(key=lambda x: x[1])
    sort_point.extend(n_point1)
    n_point2 = n[2:4]
    n_point2.sort(key=lambda x: x[1])
    n_point2.reverse()
    sort_point.extend(n_point2)
    p1 = np.array(sort_point, dtype=np.float32)
    h = sort_point[1][1] - sort_point[0][1]
    w = sort_point[2][0] - sort_point[1][0]
    pts2 = np.array([[0, 0], [0, h], [w, h], [w, 0]], dtype=np.float32)

    # 生成变换矩阵
    M = cv2.getPerspectiveTransform(p1, pts2)
    # 进行透视变换
    dst = cv2.warpPerspective(image, M, (w, h))
    # print(dst.shape)
    show(dst, "dst")

    if w < h:
        dst = np.rot90(dst)
    size = dst.shape
    resize = cv2.resize(dst, (size[1], size[0]), interpolation=cv2.INTER_AREA)
    return resize


def detect_orc(image):

    #image = preprocessing(image)

    temp_image = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #show(gray, "gray")

    # 二值化
    threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    #show(threshold, "threshold")

    # 中值滤波
    blur = cv2.medianBlur(threshold, 5)
    #show(blur, "blur")

    #闭运算
    kernel = np.ones((3, 3), np.uint8)
    morph_open = cv2.morphologyEx(blur, cv2.MORPH_OPEN, kernel)
    #show(morph_open, "morph_open")

    kernel = np.ones((7, 7), np.uint8)
    dilate = cv2.dilate(morph_open, kernel, iterations=6)
    show(dilate, "dilate")

    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    resize_copy = image.copy()
    res = cv2.drawContours(resize_copy, contours, -1, (255, 0, 0), 2)
    show(res, "res")

    # 保存每个区域的坐标
    labels = ['姓名', '性别', '民族', '出生年', '出生月', '出生日', '住址', '公民身份证号码']
    positions = []
    data_areas = {}
    resize_copy = image.copy()
    size1 = resize_copy.shape
    threshold_height_min = 0.03 * size1[0]
    threshold_height_max = 0.2 * size1[0]
    threshold_x_max = 0.6 * size1[1]
    for contour in contours:
        epsilon = 0.003 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        x, y, w, h = cv2.boundingRect(approx)
        if h > threshold_height_min and x < threshold_x_max and h < threshold_height_max:
            res = cv2.rectangle(resize_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
            area = gray[y:(y + h), x:(x + w)]
            blur = cv2.medianBlur(area, 3)
            data_area = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            positions.append((x, y))
            data_areas['{}-{}'.format(x, y)] = data_area

    show(res, "res")

    # 对区域进行排序
    positions.sort(key=lambda p: p[1])
    result = []
    index = 0
    threshold_interval = 0.7 * size1[0]
    while index < len(positions) - 1:
        if positions[index + 1][1] - positions[index][1] < threshold_interval:
            temp_list = [positions[index + 1], positions[index]]
            for i in range(index + 1, len(positions)-1):
                if positions[i + 1][1] - positions[i][1] < threshold_interval:
                    temp_list.append(positions[i + 1])
                else:
                    break
            temp_list.sort(key=lambda p: p[0])
            positions[index:(index + len(temp_list))] = temp_list
            index = index + len(temp_list) - 1
        else:
            index += 1

    # 加载CnOcr的模型
    ocr = CnOcr(model_name='densenet_lite_136-gru')

    for index in range(len(positions)):
        position = positions[index]
        data_area = data_areas['{}-{}'.format(position[0], position[1])]
        ocr_data = ocr.ocr(data_area)

        #print(ocr_data)  # 打印ocr_data的内容

        # 初始化结果列表
        ocr_results = []

        # 遍历 OCR 返回的每个结果
        for result_item  in ocr_data:
            # 确保结果包含 'text' 键
            if 'text' in result_item :
                ocr_results.append(result_item ['text'])  # 取出识别出的文本
            else:
                print(f"Unexpected result format: {result_item }")  # 打印意外格式

        # 合并结果
        ocr_result = ''.join(ocr_results).replace(' ', '')
        # print('{}：{}'.format(labels[index], ocr_result))
        result.append('{}：{}'.format(labels[index], ocr_result))
        show(data_area, "data_area")

    for item in result:
        print(item)
    show(res, "res")










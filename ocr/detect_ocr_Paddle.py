import paddlehub
import paddlehub as hub
import cv2
import paddle as pp



def detect_ocr_paddle(image):
    ocr = hub.Module(name="chinese_ocr_db_crnn_mobile",enable_mkldnn=True)
    results = ocr.recognize_text(images=[image],
                                 use_gpu=False,  # 是否使用 GPU；若使用GPU，请先设置CUDA_VISIBLE_DEVICES环境变量
                                 output_dir='ocr_result',  # 图片的保存路径，默认设为 ocr_result；
                                 visualization=True,  # 是否将识别结果保存为图片文件；
                                 box_thresh=0.5,  # 检测文本框置信度的阈值；
                                 text_thresh=0.5)
    return results

if(__name__=="__main__"):
    path =r'../sources/images/12.jpg'
    image = cv2.imread(path)
    results = detect_ocr_paddle(image)
    print(results)

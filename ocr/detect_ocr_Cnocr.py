from cnocr import CnOcr
import cv2
import numpy as np
import re

def detect_ocr(image):

    # 检测是否有物体
    ocr = CnOcr()
    results = ocr.ocr(image)
    print(results)

    results = sort_by_position(results)
    print(results)
    datas = ''
    for result in results:
        data = result['text']
        datas = datas + data

    datas = removeSpace(datas)
    datas = removePunctuation(datas)
    datas = removeLetter(datas)
    #print(datas)
    datas = findResult(datas)
    return datas



def sort_by_position(data, pixel_threshold=0.3):
    # 先按 y 坐标（即 position[0][1]）升序排序，y 值相同时按 x 坐标（即 position[0][0]）升序排序
    sorted_data = sorted(data, key=lambda x: (x['position'][0][1], x['position'][0][0]))

    # 最终结果
    result = []

    # 临时存放 y 近似相同的元素
    current_line = []

    # 当前 y 参考值
    current_y = sorted_data[0]['position'][0][1]

    for item in sorted_data:
        item_y = item['position'][0][1]

        # 检查当前项的 y 值是否与 current_y 的偏差在 pixel_threshold 范围内
        if abs(item_y - current_y) <= pixel_threshold:
            current_line.append(item)
        else:
            # 如果 y 偏差大于 pixel_threshold，意味着我们进入了新的一行
            # 先将 current_line 按 x 坐标排序，并加入结果中
            result.extend(sorted(current_line, key=lambda x: x['position'][0][0]))
            # 更新 current_y，并开始新的行
            current_line = [item]
            current_y = item_y

    # 最后将剩余的 current_line 加入结果中
    if current_line:
        result.extend(sorted(current_line, key=lambda x: x['position'][0][0]))

    return result


def removeSpace (long_str):
    #去除空格
    noneSpaceStr = ''
    str_arry = long_str.split()
    for x in range(0,len(str_arry)):
        noneSpaceStr = noneSpaceStr+str_arry[x]
    return noneSpaceStr


def removePunctuation(noneSpaceStr):
   #去除标点符号
    punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~“”？，！『【】（）、。：；’‘……￥·"""
    s =noneSpaceStr
    dicts={i:'' for i in punctuation}
    punc_table=str.maketrans(dicts)
    nonePunctuationStr=s.translate(punc_table)
    return nonePunctuationStr

#去除字母
def removeLetter(nonePunctuationStr):
    letter = r"""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"""
    s = nonePunctuationStr
    dicts = {i: '' for i in letter}
    letter_table = str.maketrans(dicts)
    noneLetterStr = s.translate(letter_table)
    return noneLetterStr

def find_first_digit_index(input_str):
    match = re.search(r'\d', input_str)
    if match:
        return match.start()
    else:
        return -1  # 如果没有找到数字，返回 -1


def find_last_digit_index(input_str):
    # 使用正则表达式找到所有连续的数字段
    matches = list(re.finditer(r'\d+', input_str))

    # 如果有找到数字段，返回最后一个数字段的起始索引
    if matches:
        last_match = matches[-1]  # 最后一段数字
        return last_match.start()  # 返回其起始索引
    else:
        return -1  # 如果没有找到数字，返回 -1

def findResult(nonePunctuationStr):
    name = "姓名"
    sex = "性别"
    race = "民族"
    birth = "出生"
    address = "住址"
    idCardNumber = "公民身份号码"

    index1 =find_first_digit_index(nonePunctuationStr)
    index2 = nonePunctuationStr.find("民")
    index3 = nonePunctuationStr.find("住")
    index4 = nonePunctuationStr.rfind("公")
    index5 = find_last_digit_index(nonePunctuationStr)
    index6 = nonePunctuationStr.find("日",index1)
    index7 = nonePunctuationStr.find("姓")


    numberName = nonePunctuationStr[index7:index7+4]
    numberSex = nonePunctuationStr[index2-1]
    numberRace = nonePunctuationStr[index2+2:index1]
    numberBirth = nonePunctuationStr[index1:index6+1]
    numberAddress = nonePunctuationStr[index6+1:index4]
    numberIdCardNumber = nonePunctuationStr[index5:]

    if(len(numberName)==0):
        numberName = nonePunctuationStr[:index2-1]


    reverseDict = {name: numberName, sex: numberSex, race: numberRace, birth: numberBirth, address: numberAddress,
                   idCardNumber: numberIdCardNumber}
    return reverseDict


if(__name__=="__main__"):
    path =r'../sources/images/13.png'

    # 读取图像
    image = cv2.imread(path)
    result = detect_ocr(image)
    print(result)
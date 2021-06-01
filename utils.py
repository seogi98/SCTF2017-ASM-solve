import cv2
BLUE = 0
GREEN = 1
RED  = 2
def get_chars(image, color):
    other_1 = (color + 1) % 3
    other_2 = (color + 2) % 3
    c = image[:, :, other_1] == 255
    image[c] = [0, 0, 0]
    c = image[:, :, other_2] == 255
    image[c] = [0, 0, 0]
    c = image[:, :, color] < 170
    image[c] = [0, 0, 0]
    c = image[:, :, color] != 0
    image[c] = [255, 255, 255]
    return image

# 전체 이미지에서 왼쪽부터 단어별로 이미지를 추출합니다.
def extract_chars(image):
    chars = []
    colors = [BLUE, GREEN, RED]
    for color in colors:
        image_from_one_color = get_chars(image.copy(), color)
        image_gray = cv2.cvtColor(image_from_one_color, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(image_gray, 127, 255, 0)
        # RETR_EXTERNAL 옵션으로 숫자의 외각을 기준으로 분리
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        # 추출된 이미지 크기가 50 이상인 경우만 실제 문자 데이터인 것으로 파악
        area = cv2.contourArea(contour)
        if area > 50:
            x, y, width, height = cv2.boundingRect(contour)
            roi = image_gray[y:y + height, x:x + width]
            chars.append((x, roi))
    chars = sorted(chars, key=lambda char: char[0])
    return chars

import numpy as np
# 특정한 이미지를 (20 x 20) 크기로 Scaling 합니다.
def resize20(image):
    resized = cv2.resize(image, (20, 20))
    return resized.reshape(-1, 400).astype(np.float32)
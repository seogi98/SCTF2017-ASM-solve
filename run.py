import numpy as np
import cv2
import utils
import inti
FILE_NAME = "trained.npz"


# 각 글자의 (1 x 400) 데이터와 정답 (0 ~ 9, +, *)
with np.load(FILE_NAME) as data:
    train = data['train']
    train_labels = data['train_labels']
knn = cv2.ml.KNearest_create()
knn.train(train, cv2.ml.ROW_SAMPLE, train_labels)


def check(test, train, train_labels):
    # 가장 가까운 K개의 글자를 찾아, 어떤 숫자에 해당하는지 찾습니다. (테스트 데이터 개수에 따라서 조절)
    ret, result, neighbours, dist = knn.findNearest(test, k=1)
    return result

def get_result(file_name):
    image = cv2.imread(file_name)
    chars = utils.extract_chars(image)
    result_string = ""
    for char in chars:
        matched = check(utils.resize20(char[1]), train, train_labels)
        if matched < 10:
            result_string += str(int(matched))
            continue
        if matched == 10:
            matched = '+'
        elif matched == 11:
            matched = '-'
        elif matched == 12:
            matched = '*'
        result_string += matched
    return result_string
# print(get_result(inti.startAdd+"./images/1.png"))

# 파싱 시작
import requests
import time
import shutil
import inti
host = "http://192.168.0.97:10000/"
url = '/start'

with requests.Session() as s:
    answer = ''
    start_time = time.time()
    for i in range(100):
        params = {'ans':answer}
        response = s.post(host+url,params)
        print("Server Return" + response.text)
        if response.text == "-1":
            print("Error")
            break
        # 처음에 받아왔을때
        if i == 0:
            returned = response.text
            image_url = host + returned
            url = '/check'
        else:
            returned = response.json()
            image_url = host + returned['url']
        print('Problem ' + str(i) + ': ' + image_url)
        # 특정한 폴더에 이미지 파일을 다운로드 받습니다.
        response = s.get(image_url, stream=True)
        target_image = inti.startAdd+'/target_images/' + str(i) + '.png'
        with open(target_image, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        # 다운로드 받은 이미지 파일을 분석하여 답을 도출합니다.
        answer_string = get_result(target_image)
        print('String: ' + answer_string)
        answer_string = utils.caculateStr(answer_string)
        print(answer_string)
        answer = str(answer_string)
        print('Answer: ' + answer)
        print("--- %s seconds ---" % (time.time() - start_time))
print("성공")
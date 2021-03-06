# 2017 삼성전자 해킹방어대회 ASM 문제

## 프로젝트 개요
인터넷에서 널리 사용되고 있는 번호를 입력하는 captcha을 자동으로 뚫을 수 있는 기술을 찾아보다가, 다음 유튜브 영상을 참고할 수 있으면 좋을 것 같아서 컨텐츠를 제작해봅니다.

https://www.youtube.com/watch?v=vKktSCf2ru0&t=71s 참고 사이트

- Problem Define
- 데이터 수집과 분석
- 데이터 정제
- 해킹 자동화
  
순으로 진행됩니다.
<hr>

## 1. Problem Define


요구사항은 다음과 같습니다.
- START 버튼을 누르면 80초 타이머가 동작합니다.
- Captcha와 같은 형태로 수식이 등장하며, 이를 반복적으로 풀어야 합니다.
- 80초 안에 100개의 수식에 대하여 연속적으로 정답 처리를 받아야 합니다.

주어진 설명에 따라서 홈페이지를 실행하면 다음과 같은 화면이 뜹니다.
![image](https://user-images.githubusercontent.com/44061558/121295336-cde34d80-c929-11eb-9220-7eaa23298e43.png)

start 버튼을 누르면 다음과 같이 사진이 뜹니다. 정답을 입력하면 계속 진행이 됩니다.

![image](https://user-images.githubusercontent.com/44061558/121295606-4a762c00-c92a-11eb-83f5-76ce66600535.png)

점점 수식이 길어지므로 손으로 100개의 수식을 계산하기는 어려워 집니다. 따라서 opencv를 이용해 각각의 하나의 숫자와 기호로 분리 해놓은후 knn 알고리즘을 이용해 학습시켜 계산을 할 예정입니다.
<hr>

## 2. 데이터 수집과 분석
데이터 수집을 위해 홈페이지에서 수식이 들어 있는 사진을 가져와야 합니다. 저는 사진을 가져오기 위해서 파이썬 자동화 모듈인 셀레니움을 사용했습니다. 코드는 다음과 같습니다.


```py
## get_image.py 
import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import cv2
from urllib.request import urlretrieve
import inti
import os


image_folder = "./captcha/images/"
url = "http://192.168.0.97:10000/"
driver = webdriver.Chrome(r"C:\Users\seogi\Downloads\chromedriver_win32\chromedriver.exe");
wait = WebDriverWait(driver, 100)
#크롬 실행
driver.get(url)
ImageXpath = "/html/body/div[1]/div/div/div/div[1]/img["
# src 담아서 저장한다.
imageSrc = []

for i in range(1,10):
    nextImageXpath = ImageXpath + str(i) + "]"
    # 이미지 보일때 까지 대기
    wait.until(EC.element_to_be_clickable((By.XPATH,nextImageXpath)))
    image_elem = driver.find_elements_by_xpath(nextImageXpath)
    for image in image_elem:
        print(image.get_attribute('src'))
        imageSrc.append(image.get_attribute('src'))
    print((image_elem))
path = inti.startAdd+'/images/'
file_count = len(next(os.walk(path))[2])
for index, link in enumerate(imageSrc):           #리스트에 있는 원소만큼 반복, 인덱스는 index에, 원소들은 link를 통해 접근 가능
    start = link.rfind('.')         #.을 시작으로
    end = link.rfind('?')           #?를 끝으로
    filetype = link[start:end]      #확장자명을 잘라서 filetype변수에 저장 (ex -> .jpg)
    urlretrieve(link, './captcha/images/{}{}'.format(file_count+index, ".png")) 

```
문제 이미지의 xpath는 img[1] img[2]..와 같이 늘어 납니다. 따라서 다음이미지가 나올때 까지 대기하다가 이미지가 나오면 자동으로 사진을 가져와 png형식으로 저장해주면 됩니다.

<hr>

## 3. 데이터 정제

크롤링을 통해 충분히 이미지를 확보하였으니 이를 opencv를 사용해서 각각의 문자로 분리해야 합니다. 문자를 분리하기 위해서
 이미지 RGB각각의 색상이 들어있는 부분 나눕니다.

```py
# util.py
def get_chars(image, color):
    # 들어온 색상과 다른 색상
    other_1 = (color + 1) % 3
    other_2 = (color + 2) % 3
    # 색상이 다를경우 [0,0,0]으로 바꿈
    c = image[:, :, other_1] == 255
    image[c] = [0, 0, 0]
    c = image[:, :, other_2] == 255
    image[c] = [0, 0, 0]
    # 중간 색상
    c = image[:, :, color] < 170
    image[c] = [0, 0, 0]
    # 원하는 색상
    c = image[:, :, color] != 0
    image[c] = [255, 255, 255]
    return image
```
나눈 각각의 색상을 바탕으로 문자를 추출합니다.

```py
# 전체 이미지에서 왼쪽부터 단어별로 이미지를 추출합니다.
def extract_chars(image):
    chars = []
    colors = [BLUE, GREEN, RED]
    for color in colors:
        # 색상별로 분리
        image_from_one_color = get_chars(image.copy(), color)
        # grey 색상으로 변경
        image_gray = cv2.cvtColor(image_from_one_color, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(image_gray, 127, 255, 0)
        # RETR_EXTERNAL 옵션으로 숫자의 외각을 기준으로 분리
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            # 추출된 이미지 크기가 50 이상인 경우만 실제 문자 데이터인 것으로 파악
            area = cv2.contourArea(contour)
            if area > 30:
                x, y, width, height = cv2.boundingRect(contour)
                # 숫자의 위치를 저장한다.
                roi = image_gray[y:y + height, x:x + width]
                chars.append((x, roi))
    # x좌표를 기준으로 문자를 정렬한다.
    chars = sorted(chars, key=lambda char: char[0])
    return chars
```
나눈 데이터를 저장하는 함수
```py
# make_train_data
path = startAdd+'/images/'
file_count = len(next(os.walk(path))[2])
# 파일 크기만큼 돌면서
for filename in range(0,file_count-1):
    #png 파일을 열고
    tmp  = startAdd+"/images/"+str(filename)+".png"
    image = cv2.imread(tmp)
    # 각각의 문자를 추출해서
    chars = utils.extract_chars(image)
    print(os.getcwd())
    for char in chars:
        cv2.imshow('Image', char[1])
        # 사용자가 무슨값인지 적어서 mapping 
        # 0~12로 입력해서 저장한다.
        input = cv2.waitKey(0)
        resized = cv2.resize(char[1], (20, 20))
        if input >= 48 and input <= 57:
            name = str(input - 48)
            file_count = len(next(os.walk(startAdd+'/training_data/' + name + '/'))[2])
            cv2.imwrite(startAdd+'/training_data/' + str(input - 48) + '/' +
                        str(file_count + 1) + '.png', resized)
        elif input == ord('a') or input == ord('b') or input == ord('c'):
            name = str(input - ord('a') + 10)
            file_count = len(next(os.walk(startAdd+'/training_data/' + name + '/'))[2])
            cv2.imwrite(startAdd+'/training_data/' + name + '/' +
                        str(file_count + 1) + '.png', resized)

```

이제 이미지를 문자로 나누어서 각각의 폴더에 저장해 두었습니다.
저장된 데이터를 바탕으로 학습 데이터를 만들어 봅시다.

```py
import os
import cv2
import numpy as np
import inti
startAdd = inti.startAdd
#0~9,+,-,* 문자들
file_names = list(range(0, 13))
train = []
train_labels = []
for file_name in file_names:
    path = startAdd+'/training_data/'+str(file_name)+'/'
    file_count = len(next(os.walk(path))[2])
    for i in range(1, file_count):
        tmp  = path + str(i) + '.png'
        img = cv2.imread(path + str(i) + '.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # train에 이미지 데이터 저장
        train.append(gray)
        # 라벨에 무슨 문자인지 저장
        train_labels.append(file_name)
x = np.array(train)
# 이미지 정보
train = x[:, :].reshape(-1, 400).astype(np.float32)
# 레이블 정보
train_labels = np.array(train_labels)[:, np.newaxis]
print(train.shape)
print(train_labels)
np.savez("trained.npz", train=train, train_labels=train_labels)

```

## 해킹 자동화
```py
#run.py
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
host = inti.host
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
```
<hr>

## 최종 결과
위 코드로 100문제 해결하는데 총 15초가 소모되었습니다.
![image](https://user-images.githubusercontent.com/44061558/121447669-1a359880-c9d1-11eb-9ad4-70b17d23a529.png)

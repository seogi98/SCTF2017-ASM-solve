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
url = "http://192.168.1.82:10000/"
driver = webdriver.Chrome(r"C:\Users\seogi\Downloads\chromedriver_win32\chromedriver.exe");
wait = WebDriverWait(driver, 100)
#크롬 실행
driver.get(url)
ImageXpath = "/html/body/div[1]/div/div/div/div[1]/img["
# src 담아서 저장한다.
imageSrc = []

for i in range(1,5):
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

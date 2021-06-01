import os
import cv2
import utils
import inti
# training_data 폴더 생성 및 그 내부에 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 폴더 생성
# (10 => +) (11 =>-) (12 => *)

# 시작 주소
startAdd = inti.startAdd

path = startAdd+'/images/'
file_count = len(next(os.walk(path))[2])
for filename in range(13,file_count-1):
    tmp  = startAdd+"/images/"+str(filename)+".png"
    image = cv2.imread(tmp)
    chars = utils.extract_chars(image)
    print(os.getcwd())
    for char in chars:
        cv2.imshow('Image', char[1])
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

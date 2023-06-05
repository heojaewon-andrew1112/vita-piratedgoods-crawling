#!/usr/bin/env python
# coding: utf-8

# 필요 모듈 import 
import requests
from requests import get

import urllib.request
from urllib.request import urlopen
from urllib.request import urlretrieve

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
import os
import pandas as pd
from multiprocessing import Pool

import cv2
from io import BytesIO
from PIL import Image

# 헤더
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
hdr = {'User-Agent' : user_agent}

# 이미지 바이트 조건
image_raw =  BytesIO(urllib.request.urlopen('https://imgnews.pstatic.net/image/016/2023/06/01/20230601000634_0_20230601170401674.jpg?type=w430').read())

image_raw.seek(-1, 2)
last_byte = image_raw.read() # 마지막 바이트

image_raw.seek(0)
first_byte = image_raw.read(1) # 첫번째 바이트
first_byte

# 이미지 높이, 너비 검사
def image_width_height(imgurl):
    image_raw =  BytesIO(requests.get(imgurl, headers = hdr).content)
    image = Image.open(image_raw)
    width, height = image.size
    if (width > 200) and (height > 200): # 높이와 너비가 각각 200 이상
        print(f'width: {width}, height: {height}')
        return 1 
    else:
        return -1
    
# 이미지 사이즈 검사 
def image_size_check(imgurl):
    path = BytesIO(requests.get(imgurl, headers = hdr).content)
    path.seek(0, 2)  # 0 bytes from the end
    size = path.tell()
    if size > 3000: # 이미지 사이즈가 3000 이상
        print(f'size: {size}')
        return 1 
    else:
        return -1

# 이미지 바이트 조건 검사
def image_byte_check(imgurl):
    image_check =  BytesIO(requests.get(imgurl, headers = hdr).content)
    image_check.seek(-1, 2)
    last_byte_check = image_check.read()
    image_check.seek(0)
    first_byte_check = image_check.read(1)
    first_same = (first_byte_check == first_byte) # 위에 정의한 이미지 first_byte와 동일한지 확인
    last_same = (last_byte_check == last_byte) # 위에 정의한 이미지 last_byte와 동일한지 확인
    if (first_byte_check == first_byte) and (last_byte_check == last_byte):
        print(f'first_same: {first_same}, last_same: {last_same}')
        return 1
    else:
        return -1 # -1 부적합

# 폴더 생성
# directory 경로가 존재하지 않으면 폴더 생성
def create_folder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)

# 이미지 다운로드 함수
def image_download(keyword, folder_name, file_name):
    start = time.time()
    create_folder('C:/vita_piratedgoods_crawling/야후 이미지 크롤링/data/yahoo_image_download/' + str(folder_name)) # 원하는 경로에 create_folder 함수로 폴더 생성

    options = webdriver.ChromeOptions() # 크롬 옵션 객체 생성
    options.add_argument('headless') # headless 모드 설정
    options.add_argument("window-size=1920x1080") 
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("disable-gpu") 
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # 속도 향상을 위한 옵션 해제
    # prefs = {'profile.default_content_setting_values': {'cookies' : 2, 'images': 2, 'plugins' : 2, 'popups': 2, 'geolocation': 2, 'notifications' : 2, 'auto_select_certificate': 2, 'fullscreen' : 2, 'mouselock' : 2, 'mixed_script': 2, 'media_stream' : 2, 'media_stream_mic' : 2, 'media_stream_camera': 2, 'protocol_handlers' : 2, 'ppapi_broker' : 2, 'automatic_downloads': 2, 'midi_sysex' : 2, 'push_messaging' : 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop' : 2, 'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement' : 2, 'durable_storage' : 2}}   
    # options.add_experimental_option('prefs', prefs)

    # driver 객체 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    driver.implicitly_wait(10)

    print(keyword, '검색')

    # 야후 이미지 검색 사이트 열기
    driver.get('https://search.yahoo.co.jp/image')
    driver.implicitly_wait(10)

    # 키워드 검색 창에 입력
    keyword_input = driver.find_element(By.XPATH, '//*[@id="search"]/form/div[1]/div/input[1]')
    keyword_input.send_keys(keyword)

    # 검색 아이콘 클릭
    driver.find_element(By.XPATH, '//*[@id="search"]/form/div[1]/button').send_keys(Keys.ENTER)

    # 검색 후 검색 결과 스크롤
    print(keyword + ' 스크롤 중........')
    elem = driver.find_element(By.TAG_NAME, 'body')
    for i in range(60):
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.1)


    try:
        driver.find_element(By.XPATH, '//*[@id="more"]/div/button').send_keys(Keys.ENTER)# 결과 더보기 버튼 클릭
        for i in range(60): # 더보기로 펼친다음 다시 스크롤링
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.1)
    except Exception as e:
        pass
        print('결과 더보기 버튼 클릭 오류', e)

    i = 0
    index = 0

    # 이미지 CSS 찾기
    images = driver.find_elements(By.CSS_SELECTOR, "img.sw-Thumbnail__innerImage")
    print(keyword + ' 찾은 이미지 개수:', len(images))
    print()

    # 이미지 src 주소에 포함되면 안될 금지단어
    # 명품 사이트는 크롤링 자체가 막혀있기 때문에 필요함
    words = ['cartier', 'bulgari', 'vancleefarpels', 'chanel', 'louisvuitton', 'tiffany', 'dior', 'hermes', 'burberry', 'montblanc'] 

    # images를 반복문 돌려 개별 이미지 원본 수집 및 저장
    for img in images:
        i+=1
        if(index < 80):
            try:
                webdriver.ActionChains(driver).click(img).perform() # 아마자 쿨락
                time.sleep(0.5)
                contains_any = False

                # 클릭 후, 원본 이미지 src 주소 추출
                img_url = driver.find_element(By.CSS_SELECTOR, 'img.sw-PreviewPanel__image').get_attribute("src")
                
                for word in words: # 이미지 src에 금지단어 포함되어 있는지 확인
                    if word in img_url:
                        contains_any = True
                        print('이미지 다운로드가 불가능합니다.')
                        break
                if contains_any == True:
                    continue 

                # 이미지 너비 높이, 크기, 바이트 조건 검사
                if(image_width_height(img_url) > 0) and (image_size_check(img_url) > 0) and (image_byte_check(img_url) > 0):
                    print('수집용 이미지 기준에 적합합니다.')
                    print(f'{keyword} 링크 수집완료: {i} / {len(images)}')
                else:
                    print('수집용 이미지 기준에 부적합합니다. 다음 이미지로 넘어갑니다.\n')
                    continue

            except Exception as e:
                print(f'{i}번째 링크 수집 실패\n', e)
                continue
            
            # 위에서 조건 만족하는 이미지 저장
            try:
                with urlopen(img_url) as f:
                    with open('C:/vita_piratedgoods_crawling/야후 이미지 크롤링/data/yahoo_image_download/' + str(folder_name) + '/' + str(file_name) + str(index) + '.jpg', 'wb') as h:
                        r_img = f.read()
                        h.write(r_img)
                        index += 1 # 다운로드까지 모두 완료되었을때 인덱스 올림
                print(f'{keyword} 이미지 다운로드 완료: {index} / {len(images)}\n')
            except Exception as e:
                print(f'{i}번째 이미지 다운로드 실패/n', e
                     )

        else:
            break

    end = time.time()
    tot_time = end - start
    print("시간 : " + str(tot_time) + ", " + str(keyword) + ' ---다운로드 완료---')
    print("")

    driver.close() # 품목 하나 다운받은 후 driver 닫기

# 엑셀 파일에서 키워드, 폴더명, 파일명 추출
meta_file = pd.read_excel('yahoo_data.xlsx')
folder_name = []
keyword = []
file_name = []

# 엑셀의 FILE_NAME, KEYWORD, FOLDER_NAME 컬럼 가져오기
excel_file_name = meta_file['FILE_NAME']
excel_model_name = meta_file['KEYWORD']
excel_folder_name = meta_file['FOLDER_NAME']

# 엑셀에서 가져온 컬럼들 각각 리스트화
keyword = excel_model_name.values.tolist()
folder_name = excel_folder_name.values.tolist()
file_name = excel_file_name.values.tolist()

# 메인 함수
if __name__ == '__main__':
    start = time.time()
    tasks = [*zip(keyword, folder_name, file_name)]
    with Pool(4) as pool: # 병렬처리를 위해 쓰레드 4개 생성
        pool.starmap(image_download, iterable=tasks) # image_download 함수 호출
    delta_t = time.time() - start
    print("Time :", str(delta_t)) 
    
    pool.close() 
    pool.join()
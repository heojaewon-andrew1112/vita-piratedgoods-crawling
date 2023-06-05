# 필요 모듈 import
import fitz
import io
from PIL import Image
import natsort
import os
import cv2
import pandas as pd

# PDF 파일 리스트 가져오기
file_list = os.listdir('C:/vita_piratedgoods_crawling/PDF 이미지 추출/pdf/') # pdf 파일들이 위치한 경로

# 위 file_list에서 pdf 파일 이름 확장자 제거하고 file_name 리스트에 담기
file_name = []
for file in file_list:
    if file.count(".") == 1:
        name = file.split('.')[0]
        file_name.append(name)

# pdf 폴더가 있는 곳으로 디렉토리 변경
# 코드 실행을 위해서 필요함
os.chdir('C:/vita_piratedgoods_crawling/PDF 이미지 추출/pdf')

# pdf에서 이미지 추출
for idx in range(len(file_list)):
    pdf = file_list[idx] 
    try:
        pdf_file = fitz.open(pdf) # pdf 파일 열기
        print(pdf_file)
    except Exception as e:
        continue
        print(e)
    
    pdf_file_name = file_name[idx] # pdf 파일 이름 변수에 담기

    try:
        if not os.path.exists(f"C:/vita_piratedgoods_crawling/PDF 이미지 추출/pdf_image_downlaod/{pdf_file_name}"): # pdf 파일 이름을 가진 폴더가 있는지 확인
            os.makedirs(f"C:/vita_piratedgoods_crawling/PDF 이미지 추출/pdf_image_downlaod/{pdf_file_name}") # 없으면 해당 pdf 파일 이름으로 폴더 생성
    except OSError:
        print(f'Error: Creating directory. {pdf_file_name}')

    # fitz로 연 pdf 파일을 페이지 별로 반복문을 돌려 이미지 추출
    for page_index in range(len(pdf_file)):     
        page = pdf_file[page_index]
        try:
            image_list = page.get_images() # 페이지에 있는 모든 이미지 가져오기
        except ValueError as e:
            print(e)
            pass
        # 페이지 별로 몇 개의 이미지 존재하는지
        if image_list:
            print(f"fileName : {pdf_file_name}, Found a total of {len(image_list)} images in page {page_index+1}")
        else:
            print(f"No images found on page {page_index+1}")
            continue

        # 페이지별로 반복문을 돌려 페이지 안에 있는 이미지 추출
        # 한 반복문 cycle은 pdf 파일의 한 페이지
        for image_index, img in enumerate(image_list, start = 1):
            xref = img[0]
            base_image = pdf_file.extract_image(xref)
            try:
                image_bytes = base_image["image"]
            except Exception as e:
                print(e)
                continue
            image_ext = base_image["ext"]
            image = Image.open(io.BytesIO(image_bytes))
            page_as_string = str(image_index)
            image_path = f"C:/vita_piratedgoods_crawling/PDF 이미지 추출/pdf_image_downlaod/{pdf_file_name}/{pdf_file_name}_{page_index+1}page_{page_as_string}th.{image_ext}" # 이미지 다운로드 시, 파일명 지정
            # 저장하려는 경로에 이미지 파일 중복 존재 여부 확인
            if os.path.isfile(image_path): 
                continue # 있으면 다음 이미지로 넘어감
            try:
                # 위에서 생성한 폴더에 이미지 저장
                image.save(open(f"C:/vita_piratedgoods_crawling/PDF 이미지 추출/pdf_image_downlaod/{pdf_file_name}/{pdf_file_name}_{page_index+1}page_{page_as_string}th.{image_ext}", "wb")) # 이미지 다운로드 시, 파일명 지정
                print(f"{page_index+1}페이지의 {page_as_string}번째 이미지 다운로드 성공")
            except Exception as e:
                print(f"{page_index+1}페이지의 {page_as_string}번째 이미지 다운로드 실패", e)            
                print(e)
                pass

    print("")


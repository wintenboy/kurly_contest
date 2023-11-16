import re
import os
import sys
import math
import random
import requests
import datetime
import argparse
import numpy as np
import pandas as pd
from selenium import webdriver
from urllib.request import urlopen
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException as NSEE


parser = argparse.ArgumentParser(description='마켓컬리 홈페이지 크롤링')
parser.add_argument('--brand', help='브랜드 명 (뷰티컬리, 마켓컬리)')
parser.add_argument('--category_name', help='크롤링한 제품의 카테고리 명')


args = parser.parse_args()

def transform_likes(value):
    parts = value.split()
    if len(parts) > 1 and parts[1].isdigit():
        return int(parts[1])
    else:
        return 0

def main():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)


    url = 'https://www.kurly.com/collections/beauty-best?site=beauty&page=1&filters=category%3A363&per_page=96&sorted_type=4'
    driver.get(url)
    driver.implicitly_wait(10)
    time.sleep(5)

    category = []
    contents = []
    likes = []
    titles = []
    dates = []

    text_path = '/html/body/div/div[3]/div[1]/div[2]/div[2]/div[2]/div/span'
    category = driver.find_element(By.XPATH,text_path).text



    for i in range(1, 5):
        try:
            driver.find_element(By.XPATH, '/html/body/div/div/div[3]/div[2]/nav/ul/li[3]/a/span[1]').click()
        except:
            print('리뷰 개수 오류 발생')
        
        time.sleep(1)

        for j in range(4, 14):


            content_text_path = '/html/body/div/div/div[3]/div[2]/div/div[3]/section/div[2]/div[' + str(j) + ']/article/div/p'
            content = driver.find_element(By.XPATH, contents_text_path).text
            contents.append(contents)

            # 좋아요 추출
            like_text_path = '/html/body/div/div/div[3]/div[2]/div/div[3]/section/div[2]/div[' + str(j) + ']/article/div/footer/button/span[2]'
            like = driver.find_element(By.XPATH, like_text_path).text
            likes.append(like)

            date_text_path = '/html/body/div/div/div[3]/div[2]/div/div[3]/section/div[2]/div[' + str(j) + ']/article/div/footer/div/span'
            date = driver.find_element(By.XPATH, date_text_path).text
            dates.append(date)
        driver.get(url)
        driver.implicitly_wait(10)
        time.sleep(5)

        data = []

        for i in range(4):
            for j in range(10):
                index = i * 10 + j 
                data.append({
                    'category': category,
                    'productname': titles[i],
                    'content': contents[index],
                    'likes': likes[index],
                    'datetime': dates[index]
                })

        df = pd.DataFrame(data)
        df['likes'] = df['likes'].apply(transform_likes)  # 추가 전처리 (도움돼요 글자 삭제)
        df.to_csv(f'data/homepage_reviews/{args.brand_name}_{args.category_name}_content.csv', index = False)




if __name__ == '__main__':
    main()
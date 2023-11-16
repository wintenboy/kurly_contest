import numpy as np
import pandas as pd
import re
from konlpy.tag import Okt
from kiwipiepy import Kiwi
from tqdm import tqdm, tqdm_pandas
from itertools import product

def add_commas(string):
    return ', '.join(string.split())

def add_brackets(string):
    return f'[{string}]'

def del_list(text):
    text = re.sub(r'\[|\]', '', str(text))
    text = re.sub(r'\'', '',str(text))

    return text

def create_network(data) -> pd.DataFrame():
    all_combinations = []

    for importance, hashtags, keyword in zip(data['importance'], data['hashtags'], data['keyword']):
        importance_list = [importance]
        combinations = list(product(importance_list, hashtags, keyword))
        all_combinations.extend(combinations)


    df = pd.DataFrame(all_combinations, columns = ['weight', 'to', 'from'])

    tqdm.pandas()

    df['from'] = df['from'].progress_apply(del_list)
    df['to'] = df['to'].progress_apply(del_list)
    df['weight'] = df['weight'].progress_apply(del_list)

    df['weight'] = df['weight'].astype('float')

    result_df = df[~df['to'].str.contains('마켓컬리') & ~df['from'].str.contains('마켓컬리')]
    result_df = df[~df['to'].str.contains('컬리') & ~df['from'].str.contains('컬리')]    

    return df

def noun_extractor(text):
    results = []
    kiwi = Kiwi()
    result = kiwi.analyze(text)
    for token, pos, _, _ in result[0][0]:
        if len(token) != 1 and (pos.startswith('N') or pos.startswith('SL')):
            results.append(token)
    return results


class PreProcessing():

    def __init__(self, df):
        self.df = df

    def preprocess_text_for_blog(self, text):
        # 1. 불필요한 메타데이터 제거
        text = text.split('인쇄')[0]

        # 2. 줄바꿈 및 들여쓰기 제거
        text = text.replace('\n', ' ').strip()

        # 3. 텍스트 정규화
        text = text.lower() # 모두 소문자로 변환
        text = re.sub(r'[^\w\s]', ' ', text) # 문장 부호 및 특수 문자 제거

        # 4. Tokenization and stemming
        okt = Okt()
        tokens = okt.morphs(text)

        # 5. 불용어 제거
        stopwords = ['이', '그', '것', '의', '을', '를', '와', '과']
        filtered_tokens = [word for word in tokens if word not in stopwords]

        return ' '.join(filtered_tokens)
    

    def prerpocess_text_for_homepage(self, text) -> str:
        # 1. 텍스트 정규화
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text) # 문장 부호 및 특수 문자 제거

        # 2. 숫자 + 단위, 단위 + 숫자 제거
        text = re.sub(r'\d+[가-힣]+', '', text) # Remove patterns like 숫자+단위
        text = re.sub(r'[가-힣]+\d+', '', text) # Remove patterns like 단위+숫자

        # 3. 2회 이상 띄어쓰기 제거   
        text = re.sub(r'\s+', ' ', text)
        
        # 4. 토큰화 & stemming
        okt = Okt()
        tokens = okt.morphs(text)

        # 불용어
        stopwords = ['이', '그', '것', '의', '을', '를', '와', '과']
        filtered_tokens = [word for word in tokens if word not in stopwords]

        return ' '.join(filtered_tokens)

    def preprocess_product_name_for_homepage(self, text) -> str:
        #1. 숫자+단위, 단위+ 숫자 제거
        text = re.sub(r'\d+[가-힣]+', '', text) # Remove patterns like 숫자+단위
        text = re.sub(r'[가-힣]+\d+', '', text) # Remove patterns like 단위+숫자
        
        #2. 제품 이름에서 특수 문자와 숫자 영어 제거
        text = re.sub(r'[^가-힣\s]', '', text) # 한글과 영문자만 남기고 제거
        
        #3. 구매 시 제거
        text = re.sub(r'구매 시', ' ', text)
        
        #4. 2회 이상 띄어스기 제거
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    # 해시태그 추출 함수
    def extract_hashtags(self, text) -> str:
        hashtags = re.findall(r'\n#\w+', text)
        return hashtags
    
    # 공감 수 추출 함수
    def extract_likes(self, text) -> str:
        match = re.search(r'\n공감 (\d+)', text)
        if match:
            return int(match.group(1))
        return None

    # 댓글 수 추출 함수
    def extract_comments(self, text) :
        match = re.search(r'\n댓글 (\d+)', text)
        if match:
            return int(match.group(1))
        return None

    # 해시태그 칼럼 전처리
    def hashtag_split(self, text) -> str:
        text = text.replace('\n#','')
        return text

    def del_oddsments(self, list_):
        new_list = list(map(self.hashtag_split, list_))
        return new_list
    
    def preprocess_for_blog(self) -> pd.DataFrame:
        '''
        마켓컬리, 뷰티컬리 블로그 포스팅 데이터 전처리 함수
        '''
        tqdm.pandas()

        self.df['hashtags'] = self.df['content'].progress_apply(self.extract_hashtags)
        self.df['likes'] = self.df['content'].progress_apply(self.extract_likes)
        self.df['comments'] = self.df['content'].progress_apply(self.extract_comments)

        self.df['hashtags'] = self.df['hashtags'].progress_apply(self.del_oddsments)
        self.df['likes'] = self.df['likes'].fillna(0)
        self.df['comments'] = self.df['comments'].fillna(0)

        self.df['preprocessed_content'] = self.df['content'].progress_apply(self.preprocess_text_for_blog)
        self.df['importance'] = self.df['likes'].values + self.df['comments'].values

        return self.df[['datetime','hashtags','preprocessed_content','importance']]

    def preprocess_for_homepage(self) -> pd.DataFrame:
        '''
        마켓컬리, 뷰티컬리 홈페이지 리뷰 데이터 전처리 함수
        '''
        tqdm.pandas()

        self.df['preprocessed_category'] = self.df['category'].progress_apply(self.preprocess_product_name_for_homepage)
        self.df['preprocessed_productname'] = self.df['productname'].progress_apply(self.preprocess_product_name_for_homepage)
        self.df['preprocessed_content'] = self.df['content'].progress_apply(self.prerpocess_text_for_homepage)
        self.df['datetime'] = pd.to_datetime(self.df['datetime'])
        self.df.sort_values(by='datetime', inplace=True)

        return self.df[['datetime', 'preprocessed_category','preprocessed_productname','preprocessed_content','likes']]


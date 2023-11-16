import argparse
import numpy as np
import pandas as pd
from kiwipiepy import Kiwi
from keybert import KeyBERT
from transformers import BertModel
from tqdm import tqdm, tqdm_pandas
from utils import PreProcessing, noun_extractor, add_commas, add_brackets


parser = argparse.ArgumentParser(description = '리뷰 데이터 전처리 프로그램')

parser.add_argument('--data_path', help = 'csv file 경로를 입력해주세요.')
parser.add_argument('--encoding', default = 'utf-8', help = '어떤 방식으로 인코딩할지 선택해주세요.')
parser.add_argument('--types', default = '블로그 포스팅' ,help ='블로그 포스팅인지 홈페이지 리뷰인지 선택해주세요.')
parser.add_argument('--output_path', help = '저장할 csv file 경로를 입력하세요.')
args = parser.parse_args()




def main():

    df = pd.read_csv(args.data_path, encoding = args.encoding)

    preprocess = PreProcessing(df)
    model = BertModel.from_pretrained('skt/kobert-base-v1')
    kw_model = KeyBERT(model)

    if args.types == '블로그 포스팅':
        result_df = preprocess.preprocess_for_blog()
        content_list = result_df['preprocessed_content'].tolist()
        extracted_keywords = []
        
        for text in tqdm(content_list):

            # 명사 추출
            nouns = noun_extractor(text)
            after_kiwi_text = ' '.join(nouns)

            # KeyBERT를 사용한 키워드 추출
            # 상위 3개의 단어만 추출 !!
            preprocessed_content_keywords = kw_model.extract_keywords(after_kiwi_text, keyphrase_ngram_range=(1, 1), stop_words=None, top_n=3)

            # 추출된 키워드 리스트에 저장
            extracted_keywords.append(preprocessed_content_keywords)

        words_only = [[keyword[0] for keyword in keywords_list] for keywords_list in extracted_keywords]

        keywords_df = pd.DataFrame({
            'Extracted_Keywords': words_only
            })

        network_df = pd.concat([result_df[['datetime','hashtags','importance']], keywords_df], axis=1)
    elif args.types == '홈페이지 리뷰':
        result_df = preprocess.preprocess_for_homepage()
        content_list = result_df['preprocessed_content'].tolist()
        extracted_hashtags = []

        for text in tqdm(content_list):

            # 명사 추출
            nouns = noun_extractor(text)
            after_kiwi_text = ' '.join(nouns)

            keywords = kw_model.extract_keywords(after_kiwi_text, keyphrase_ngram_range=(1, 1), stop_words=None, top_n=3)
            extracted_hashtags.append(keywords)

        words_only = [[keyword[0] for keyword in keywords_list] for keywords_list in extracted_hashtags]

        result_df['Extracted_Keywords'] = result_df['preprocessed_category'] + " " + result_df['preprocessed_productname']
        result_df['hashtags'] = [' '.join(keyword_list) for keyword_list in words_only]

        result_df.rename(columns = {'likes' : 'importance'}, inplace = True)
        result_df = result_df[result_df['importance'] > 0]
        result_df['hashtags'] = result_df['hashtags'].progress_apply(add_commas)
        result_df['hashtags'] = result_df['hashtags'].progress_apply(add_brackets)
        result_df['Extracted_Keywords'] = result_df['Extracted_Keywords'].progress_apply(add_commas)
        result_df['Extracted_Keywords'] = result_df['Extracted_Keywords'].progress_apply(add_brackets)

        network_df = result_df[['datetime','hashtags','importance','Extracted_Keywords']]


    network_df.to_csv(args.output_path, encoding=args.encoding, index=None)
    print('DONE')

if __name__ == '__main__':
    main()




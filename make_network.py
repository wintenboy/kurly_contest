import csv
import argparse
import itertools
import pandas as pd
import networkx as nx
from itertools import product
from utils import del_list, create_network


parser = argparse.ArgumentParser(description = '전처리 데이터로 지식 그래프 데이터 생성')

parser.add_argument('--data_path', help = 'csv file 경로를 입력해주세요.')
parser.add_argument('--encoding', default = 'utf-8', help = '어떤 방식으로 인코딩할지 선택해주세요.')
parser.add_argument('--types', default = '블로그 포스팅' ,help ='블로그 포스팅인지 홈페이지 리뷰인지 선택해주세요.')
parser.add_argument('--output_path', help = '저장할 csv file 경로를 입력하세요.')
args = parser.parse_args()


def main():

    df = {
    
    'hashtags': [],
    'importance': [],
    'keyword': []
    
    }
    if args.types == '블로그 포스팅':
        with open(args.data_path, 'r', encoding = args.encoding) as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)

            for row in csv_reader:
                hashtags = row[1]
                importance = float(row[2])
                keywords = row[3]

                hashtags = hashtags.replace("'", "")

                hashtags = [tag.strip("[]").replace("'", "").split(', ') for tag in hashtags.split(", ")]
                keywords = [keyword.strip("[]").replace("'", "").split(', ') for keyword in keywords.split(", ")]

                df['importance'].append(importance)
                df['hashtags'].append(hashtags)
                df['keyword'].append(keywords)

        result_df = create_network(df)
        result_df.to_csv(args.output_path, encoding=args.encoding, index=None)
        print('Done')
    elif args.types == '홈페이지 리뷰':
        with open(args.data_path, 'r', encoding = args.encoding) as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)

            for row in csv_reader:
                hashtags = row[1]
                importance = float(row[2])
                keywords = row[3]

                hashtags = hashtags.replace("'", "")

                hashtags = [tag.strip("[]").replace("'","").split(', ') for tag in hashtags.split(", ")]
                keywords = [keyword.strip("[]").replace("'", "").split(', ') for keyword in keywords.split(", ")]

                df['importance'].append(importance)
                df['hashtags'].append(hashtags)
                df['keyword'].append(keywords)

        result_df = create_network(df)
        result_df.to_csv(args.output_path, encoding=args.encoding, index=None)
        print('Done')

if __name__ == '__main__':
    main()
    

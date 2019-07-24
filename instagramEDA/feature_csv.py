import boto3
import json
import pandas as pd
from io import StringIO

#sys.path.append("../")
from feature import *

bucketName = 'instagram-post'
s3 = boto3.resource('s3')
my_bucket = s3.Bucket(bucketName)

csv = pd.read_csv('instagram.csv', index_col=0, header=None, names=['username'])

result = pd.DataFrame()

for json_file in my_bucket.objects.all():
    content_object = s3.Object(bucketName, json_file.key)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    data = json.loads(file_content)

    username = csv.loc[json_file.key[:-5]][0]

    influencer = {'name': username,
            'youtube': json_file.key[:-5],
            'avg_hashtag': avg_hashtags(data),   
            'avg_comment': avg_comments(data),
            'avg_self_comment': avg_self_comments(data, username),
            'post_interval': post_interval(data),
            'ppl_img_ratio': ppl_img_ratio(data) # 이미지 당 인물 등장 비율
            'lang_ratio': lang_detection(data)}  # 몇 개만 잘라서 그냥 딕셔너리 형태로 넣을지?  
        # 프로필 크롤링 결과에서 칼럼 추가...
    influencer = dict(influencer, **user_comment(data))
    #influencer = dict(influencer, **lang_detection(data))

    result = pd.concat([result, pd.DataFrame(influencer)])

csv_buffer = StringIO()
result.reset_index(drop=True).to_csv(csv_buffer)
s3.Object(bucketName, 'result.csv').put(Body=csv_buffer.getvalue())
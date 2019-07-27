import boto3
import json
import pandas as pd
from io import StringIO


bucket = "gender"
file_name = "new_instagram.csv"

s3 = boto3.client('s3')
# 's3' is a key word. create connection to S3 using default config and all buckets within S3

obj = s3.get_object(Bucket= bucket, Key= file_name)
# get object and file (key) from bucket

csv = pd.read_csv(obj['Body'], index_col=0, header=None, names=['username']) # 'Body' is a key word


instaList = csv.index.tolist()


bucketName = 'instagram-post'
s3 = boto3.resource('s3')
my_bucket = s3.Bucket(bucketName)


result = pd.DataFrame()


for json_file in my_bucket.objects.all():
    if json_file.key[:-5] in instaList:
        i+=1
        content_object = s3.Object(bucketName, json_file.key)
        file_content = content_object.get()['Body'].read().decode('utf-8')
        data = json.loads(file_content)

        username = csv.loc[json_file.key[:-5]][0]

        commenters = []
        for post in data:
            if post.get('comments'):
                for comment in post.get('comments'):
                    commenters.append(comment.get('author'))

        influencer = {'name': username,
                'youtube': json_file.key[:-5],
                'commenters': set(commenters)}
                # 프로필 크롤링 결과에서 칼럼 추가...

        result = pd.concat([result, pd.DataFrame(influencer)])
        print(i,'out of',csv.shape[0])

result.reset_index(drop=True).to_csv("commenters.csv")

csv_buffer = StringIO()
result.reset_index(drop=True).to_csv(csv_buffer)
s3.Object(bucketName, 'commenters.csv').put(Body=csv_buffer.getvalue())

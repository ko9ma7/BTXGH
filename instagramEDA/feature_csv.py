import boto3
import json
import pandas as pd
from io import StringIO

#sys.path.append("../")
from feature import *

bucketName = 'instagram-post'
s3 = boto3.resource('s3')
my_bucket = s3.Bucket(bucketName)

#csv = pd.read_csv('c:/users/home/desktop/instagram-crawler_/instagram.csv', index_col=0, header=None, names=['username'])
#csv = pd.read_csv('instagram.csv', index_col=0, header=None, names=['username'])
csv = pd.read_csv('new_instagram.csv', index_col=0, header=None, names=['username'])
instaList = csv.index.tolist()

result = pd.DataFrame()
###################
# profile csv (influencer, followers)
#info = pd.read_csv('c:/users/home/desktop/followers_of_jfla.csv', encoding='euc-kr', usecols=['num_of_posts', 'followers', 'following', 'isprivate', 'bio_url', 'username'])
# usecols=['bio'] -> unicode error


###################
i = 0
for json_file in my_bucket.objects.all():
    if json_file.key[:-5] in instaList:
        i+=1
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
                'ppl_img_ratio': ppl_img_ratio(data), # 이미지 당 인물 등장 비율
                'comment_user_num': str(user_comment(data)), # 몇 개만 잘라서 넣을지?
                'lang_ratio': str(lang_detection(data))}
                # 프로필 크롤링 결과에서 칼럼 추가...
        ###################################################
        ## 프로필 추가 부분
       # profile = info[info.username==username]

        #profile_info = {'num_of_posts': profile['num_of_posts'][0],
        #'followers': profile['followers'][0],
        #'following': profile['following'][0],
        #}

        ## 팔로워의 프로필 추가 부분
        # 해당 인플루언서에 대한 팔로워를 필터? csv가 어떤 형식?
        # 팔로워/팔로잉 비율
        #info['follow_ratio'] = info['followers']/info['following']
        #info[info.follow_ratio >= 1.2].shape[0]
        #info[(info.follow_ratio > 1.2) & (info.follow_ratio <= 0.8)].shape[0]
        #info[info.follow_ratio < 0.8].shape[0]

        # 게시글 개수
        #info[info.num_of_posts > 100].shape[0]
        #info[(info.num_of_posts <= 100) & (info.num_of_posts > 30)].shape[0]

        # bio에 url있는 팔로워 비율 --> bio url여부:인스타활동 활발함 척도?
        #bio_url_ratio = info['bio_url'].dropna().shape[0]/info.shape[0]

        #follower_info = {'avg_like_follower_ratio': avg_like_follower_ratio(data, profile_info.get('followers'))}

        ###################################################
       # influencer = dict(influencer, profile_info)
        #influencer = dict(influencer, follower_info)
        result = pd.concat([result, pd.DataFrame(influencer)])
        print(i,'out of',csv.shape[0])

csv_buffer = StringIO()
result.reset_index(drop=True).to_csv(csv_buffer)
s3.Object(bucketName, 'result.csv').put(Body=csv_buffer.getvalue())

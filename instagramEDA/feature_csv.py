import boto3
import json
import pandas as pd
from io import StringIO

#sys.path.append("../")
from feature import *

bucketName = 'instagram-post'
s3 = boto3.resource('s3')
my_bucket = s3.Bucket(bucketName)

#csv = pd.read_csv('c:/users/home/desktop/BTXGH/instagramEDA/new_instagram.csv', index_col=0, header=None, names=['username'])
#csv = pd.read_csv('instagram.csv', index_col=0, header=None, names=['username'])
csv = pd.read_csv('new_instagram.csv', index_col=0, header=None, names=['username'])
instaList = csv.index.tolist()

######################################
# profile csv (influencer, followers)
#info = pd.read_csv('c:/users/home/desktop/followers_of_jfla.csv', encoding='euc-kr', usecols=['num_of_posts', 'followers', 'following', 'isprivate', 'bio_url', 'username'])
# usecols=['bio'] -> unicode error

obj = s3.Object('instagram-profile', 'profile_influencer.csv')
influencer_profile = pd.read_csv(obj.get()['Body'], index_col=0)
profile_list = [profile_csv.key[13:-4] for profile_csv in s3.Bucket('instagram-profile').objects.all() if 'followers' in profile_csv.key]

######################################
result = pd.DataFrame()

i = 0 

for json_file in my_bucket.objects.all():
    # if json_file.key[:-5] in instaList:
    if json_file.key[:-5] in instaList and csv.loc[json_file.key[:-5]][0] in profile_list: # follower profile sample
        i+=1
        content_object = s3.Object(bucketName, json_file.key)
        file_content = content_object.get()['Body'].read().decode('utf-8')
        data = json.loads(file_content)
        
        username = csv.loc[json_file.key[:-5]][0]
        
        # 포스트 정보
        influencer = {'name': username,
                'youtube': json_file.key[:-5],
                'avg_hashtag': avg_hashtags(data),   
                'avg_comment': avg_comments(data),
                'avg_self_comment': avg_self_comments(data, username),
                'post_interval': post_interval(data),
                'ppl_img_ratio': ppl_img_ratio(data), # 이미지 당 인물 등장 비율
                'comment_user_num': str(user_comment(data)), # 몇 개만 잘라서 넣을지?
                'lang_ratio': str(lang_detection(data))}   

        # 프로필 정보
        profile = influencer_profile[influencer_profile.username==username]
        
        profile_info = {'num_of_posts': profile['num_of_posts'].iloc[0],
                        'followers': profile['followers'].iloc[0],
                        'following': profile['following'].iloc[0],
                        'bio_url': profile['bio_url'].iloc[0]
                        }

        #### 팔로워 프로필 추가 부분
        # sample 2500명
        obj = s3.Object('instagram-profile', 'followers_of_'+username+'.csv')
        followers = pd.read_csv(obj.get()['Body'], index_col=0, header=None, names=['index', 'alias', 'bio', 'bio_url', 'followers', 'following', 'isprivate', 'num_of_posts', 'scraped', 'username'])
        
        if followers['alias'].iloc[0]=='alias':
                followers = followers.iloc[1:,:]
        
        followers[['followers', 'following', 'num_of_posts']] = followers[['followers', 'following', 'num_of_posts']].astype(int)
 
        ## 팔로워/팔로잉 비율
        followers['follow_ratio'] = followers['followers']/followers['following']
        # 팔로우 대비 팔로워가 많은 유저: 영향력 높은 유저?
        high = round(followers[followers.follow_ratio >= 1.2].shape[0] / followers.shape[0], 2)
        # 팔로우, 팔로워 수 비슷한 유저: 지인 소통 위주인 유저?
        mid = round(followers[(followers.follow_ratio < 1.2) & (followers.follow_ratio >= 0.8)].shape[0]/followers.shape[0], 2)
        # 팔로워 대비 팔로우가 많은 유저: 관심있는 정보 얻기 위해 사용하는 유저? 
        low = round(followers[followers.follow_ratio < 0.8].shape[0]/followers.shape[0], 2)
        
        ## 게시글 개수
        # 게시글 100개 이상인 팔로워 비율
        #many_posts = round(followers[followers.num_of_posts > 100].shape[0] / followers.shape[0], 2)
        #followers[(followers.num_of_posts <= 100) & (followers.num_of_posts > 30)].shape[0]

        # bio에 url있는 팔로워 비율 --> bio url여부:인스타활동 활발함 척도?
        yes_url = round(followers['bio_url'].dropna().shape[0]/followers.shape[0], 2)
        
        follower_info = {'avg_like_follower_ratio': avg_like_follower_ratio(data, profile_info.get('followers')),
                        'folw:follower>follow': high, 'folw:follower=follow': mid, 'folw:follower<follow': low,
                        'folw:bio_url': yes_url}
                
        ###################################################
        influencer = dict(influencer, **profile_info)
        influencer = dict(influencer, **follower_info)
        result = pd.concat([result, pd.DataFrame(influencer)])
        
        print(i,'out of',csv.shape[0])

csv_buffer = StringIO()
result.reset_index(drop=True).to_csv(csv_buffer)
s3.Object(bucketName, 'result.csv').put(Body=csv_buffer.getvalue())
result.to_csv('c:/users/home/desktop/sample_result.csv')
#result.to_excel('c:/users/home/desktop/sample_result.xlsx', index=None)

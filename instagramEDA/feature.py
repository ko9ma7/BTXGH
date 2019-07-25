import datetime
from collections import Counter, OrderedDict
import re

# avg hashtag
def avg_hashtags(json_file):
    hashtags = []
    for post in json_file:
        if post.get('hashtags'):
            hashtags.extend(post.get('hashtags'))
    return [len(hashtags)/10] # dataframe 만들기 위해 list 형태로 반환

# post interval
def post_interval(json_file):
    date1 = datetime.datetime.strptime(json_file[0].get('datetime')[:-5].replace('T',' '),"%Y-%m-%d %H:%M:%S")
    date2 = datetime.datetime.strptime(json_file[9].get('datetime')[:-5].replace('T',' '),"%Y-%m-%d %H:%M:%S")
    post_per_day = 10/(date1-date2).days
    #post_per_week = post_per_day*7
    return [post_per_day]

# self comment
def avg_self_comments(json_file, username):
    self_comment = []
    for post in json_file:
        if post.get('comments'):
            for comment in post.get('comments'):
                if comment.get('mentions') and comment.get('author')==username:
                    self_comment.extend(comment.get('comment'))
    return [len(self_comment)/10]

# avg comment num
def avg_comments(json_file):
    comments = []
    for post in json_file:
        if post.get('comments') and not post.get('mentions'): # 답글 제외
            comments.extend(post.get('comments'))
        #comments.extend(post.get('comments')) # 답글 포함
    return [len(comments)/10]

# post x, image당 people image ratio
def ppl_img_ratio(json_file):
    people = 0
    img_num = 0
    for post in json_file:
        for img in post.get('img_desc'):
            if 'people' in img:
                people+=1
            if img: # 비디오 제외
                img_num+=1
    return [round(people/img_num,2)]

# loyal user
# 총 댓글이 n개인 유저 수
def user_comment(json_file):
    total_comment = []
    for post in json_file:
        if post.get('comments'):
            for comment in post.get('comments'):
                total_comment.append(comment.get('author'))
    value = Counter(total_comment)
    
    user_by_comment={}
    for i in range(1,11):
        user_by_comment['comment{0}'.format(i)] = len({k : v for k,v in value.items() if v==i})
    over_10 = len({k : v for k,v in value.items() if v>10})

    user_by_comment = dict(user_by_comment, **{'over_10': over_10})
    
    return user_by_comment

# language ratio
def lang_detection(json_file):
    lang = []
    emoji = []
    comments_num = 0
    for post in json_file:
        if post.get('comments'):
            for comment in post.get('comments'):
                text = comment.get('comment')
                comments_num += 1
                try:
                    if detect(text):
                        lang.append(detect(text))
                except:
                    p = re.compile(r'[ㄱ-ㅎㅏ-ㅣ가-힣A-Z\d]', re.I)
                    if p.search(text):
                        lang.append('ko')
                    else:
                        lang.append('emoji')
                        emoji.append(text) # 문장부호/특수기호만 있는 경우에도 이 리스트에 포함
    lang_dist = {k : '{0:.2f}'.format(v/comments_num*100) for k,v in OrderedDict(Counter(lang).most_common(3)).items()}
    return lang_dist

# E(like/follower)
def avg_like_follower_ratio(json_file, follower):
    total_likes = 0
    for post in json_file:
        if post.get('likes'):
            total_likes += post.get('likes')
    return round((total_likes/follower)/10, 2)

# profile pic

# E(post len) (hashtag 제외)

# follower's post num

# 팔로워 유형



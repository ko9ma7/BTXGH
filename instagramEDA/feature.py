import datetime

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

# E(like/follower)

# profile pic

# E(post len) (hashtag 제외)

# follower's post num

# 팔로워 유형
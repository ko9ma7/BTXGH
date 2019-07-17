#!/usr/bin/env python
# coding: utf-8

# In[7]:


import boto3
import io
import json
from urllib.parse import urlparse, urlencode, parse_qs
from urllib.request import urlopen
from pandas import DataFrame
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import collections
import os
import downloader
api_key = "AIzaSyCBJWC2b0FAn7pEqfhIrd0yIMOOVO8qqTk"


# In[8]:


bucket = "btxgh-test"
inputfile = "youtuber.csv"
#outputfile = "output.json"

s3_resource = boto3.resource("s3",  aws_access_key_id='AKIA3DLH7IX4UJMDWR42', aws_secret_access_key='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')
s3 = boto3.client('s3')

obj = s3.get_object(Bucket = bucket, Key = inputfile)

df = pd.read_csv(obj['Body'], index_col = False, low_memory = False)


# In[9]:


def channel_dict(fileName): #유튜버의 유튜브 링크 가져오기
    csv_df = pd.read_csv(fileName)
    channel_dict = {}
    for i in range(len(csv_df['유튜버아이디'])):
        channel_dict[csv_df['유튜버아이디'][i]] = csv_df['유튜브링크'][i]
    return channel_dict

fileName = inputfile

channel_dict = channel_dict(fileName)


# In[10]:


def make_c_v_dict(channel_id, api_key):
    
    api_data = requests.get(f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&maxResults=50&key={api_key}")
    json_data = json.loads(api_data.content.decode("utf-8"))
    
    play_lists = []
    for item in range(0,len(json_data['items'])):
        play_lists.append(json_data['items'][item]['contentDetails']['relatedPlaylists']['uploads'])
    #print(play_lists)
    
    video_list = []
    for play_list_id in play_lists:
        api_data = requests.get(f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={play_list_id}&maxResults=50&key={api_key}")
        json_data = json.loads(api_data.content.decode("utf-8"))
        
        videos = []
        for item in range(0,len(json_data['items'])):
            if json_data['items'][item]['snippet']['publishedAt'][:4] == '2019': #여기에 날짜 조건 추가, 지금은 2019, 나중에 변경 가능
                videos.append(json_data['items'][item]['snippet']['resourceId']['videoId'])    
        video_list += videos
        nextPageToken = json_data.get("nextPageToken")
        i = 1
        print(f"{len(video_list)} videos")
        
        while nextPageToken and i <= 20:
            api_data = requests.get(f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={play_list_id}&pageToken={nextPageToken}&maxResults=50&key={api_key}")
            json_data = json.loads(api_data.content.decode("utf-8"))
            videos = []
            for item in range(0,len(json_data['items'])):
                if json_data['items'][item]['snippet']['publishedAt'][:4] == '2019': #여기에 날짜 조건 추가, 지금은 2019, 나중에 변경 가능
                    videos.append(json_data['items'][item]['snippet']['resourceId']['videoId'])
            video_list += videos
            print(f"{len(video_list)} videos")
            try:
                nextPageToken = json_data.get("nextPageToken")
                i += 1
            except:
                nextPageToken = False
            if json_data['items'][item]['snippet']['publishedAt'][:4] == '2018': #불필요한 추가작업을 막기 위해 2018이 뜨면 break
                print("채널별 동영상 수집 완료")
                break
    return video_list


# In[11]:


youtuber_list = []

for channel_id in channel_dict.items():
    youtuber_list.append(channel_id[0])


# In[12]:


c_v_dict = []

for channel_id in channel_dict.items():
    c_v_dict.append(channel_id[1])


# In[39]:


for i in range (12,len(c_v_dict)):
    #print (i)
    youtuber_name = youtuber_list[i]
    youtuber_name = youtuber_name.replace(" ", "_")
    youtuber_name = youtuber_name.replace("/", "")
    youtuber_name = youtuber_name.replace(":", "")
    youtuber_name = youtuber_name.replace("'", "")
    print (youtuber_name)
    if i==12:
        continue
    vid_list = make_c_v_dict(c_v_dict[i], api_key)
    compiler = []
    for j in range(len(vid_list)):
        if j==3:
            break
        tmp = []
        if vid_list[j][0] == '-':
            continue
        os.system("python downloader.py --youtubeid %s --output %s%s.json --limit 100" %(vid_list[j],youtuber_name,str(j)))
        print (vid_list[j])
        jsonname = youtuber_name + str(j) + ".json"
        tmp.append("%s" %vid_list[j])
        for line in open(jsonname, 'r', encoding='UTF8'): ########################
            tmp.append(json.loads(line))
        compiler.append(tmp)
        os.system("del %s" %(jsonname))
    print(len(compiler), youtuber_name)
    saveas = youtuber_name+".json"
    s3object = s3_resource.Object(bucket, saveas)
    with open(saveas, 'w') as json_file:
        json.dump(compiler, json_file)
        s3object.put(
            Body=(json.dumps(compiler).encode('UTF-8'))
        )


# In[ ]:





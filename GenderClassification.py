## File I/O

import pandas as pd
import boto3

bucket = "gender"
file_name = "followers_chaerin.csv.csv"

s3 = boto3.client('s3')
# 's3' is a key word. create connection to S3 using default config and all buckets within S3

obj = s3.get_object(Bucket= bucket, Key= file_name)
# get object and file (key) from bucket

followers = pd.read_csv(obj['Body']) # 'Body' is a key word

## Basic Importation

from pyagender import PyAgender
import numpy as np
import matplotlib.pyplot as plt
import cv2
from urllib.request import urlopen

## Pretrained NN

agender = PyAgender()

## Define "No-Profile"

img_sample = followers['imgUrl'][180]

req = urlopen(img_sample)
arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
img = cv2.imdecode(arr, -1)

no_profile = img

## Store Results in Dict -> DataFrame

data = {'name': [], 'tested': [], 'male': [], 'no_profile': [], 'ratio': []}

## Missing Values

followers.dropna(subset=['query', 'imgUrl'], inplace=True, how='any')

## List of Influencers to iterate from

influencers = list(set(followers['query']))

## Loop through each influencer and his/her followers, illicit gender info from their profile pics


for influencer in influencers:

    print(influencer[26:])

    tcnt = 0
    mcnt = 0
    ncnt = 0
    rel_ = followers[followers['query'].isin([influencer])]

    n_sample = 8000

    rel = rel_.sample(n_sample)

    for index, row in rel.iterrows():

        # Looping through followers' profile images

        img = row['imgUrl']

        if img == None:
            continue

        # Evade HTTP 404 Error

        try:
            req = urlopen(img)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            image = cv2.imdecode(arr, -1)

            if np.all(image == no_profile):
                tcnt += 1
                ncnt += 1
                continue

            face = agender.detect_genders_ages(image)

          # Face Recognition Failed

            if len(face) == 0:
                continue

          # Male

            elif face[0]['gender'] <= 0.5:
                mcnt += 1
                tcnt += 1

          # Female

            elif face[0]['gender'] > 0.5:
                tcnt += 1

        except:
            continue

        data['name'].append(influencer)
        data['tested'].append(tcnt)
        data['male'].append(mcnt)
        data['no_profile'].append(ncnt)
        data['male_ratio'].append(mcnt*100/(tcnt-ncnt))


df = pd.DataFrame(data)

df.to_csv("InstaGenderProfile.csv", index=False, encoding='utf-8' )

bucket_name = "gender"
new_file = "InstaGenderProfile.csv"

s3.put_object(Body=output, Bucket=bucket_name, Key=new_file)

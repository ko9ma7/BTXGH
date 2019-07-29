import pandas as pd
from pyagender import PyAgender
import numpy as np
import matplotlib.pyplot as plt
import cv2
from urllib.request import urlopen
from datetime import datetime
print("Importation Complete!")

def list_format(phrase):
    return phrase[1:-1].replace("'", "").replace(" ", "").split(',')

df = pd.read_csv("with_source.csv", encoding='utf-8')
agender = PyAgender()
print("csv read, agender created")

df['urls'] = df['urls'].apply(list_format)

img_sample = df.iloc[2]['urls'][1]

req = urlopen(img_sample)
arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
img = cv2.imdecode(arr, -1)

no_profile = img
print("no profile announced")

data = {'name': [], 'tested': [], 'male': [], 'no_profile': [], 'male_ratio': []}

for index, row in df.iterrows():

    print(index, row['name'], datetime.now())

    if len(list(row['urls'])) == 0:
        print("Empty!")
        continue

    tcnt = 0
    mcnt = 0
    ncnt = 0

    for img in list(row['urls']):

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
        print(tcnt, "from", len(list(row['urls'])))

    data['name'].append(row['name'])
    data['tested'].append(tcnt)
    data['male'].append(mcnt)
    data['no_profile'].append(ncnt)
    try:
        data['male_ratio'].append(mcnt*100/(tcnt-ncnt))
    except:
        data['male_ratio'].append('N/A')

    if index % 5 == 0:
        gato = pd.DataFrame(data)
        gato.to_csv(str(index)+".csv", encoding='utf-8')
        print("{0}.csv complete!".format(index))

final = pd.DataFrame(data)
final.to_csv("gender_final.csv", encoding='utf-8')

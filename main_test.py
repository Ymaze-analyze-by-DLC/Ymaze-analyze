from cv2 import threshold
import pandas as pd
from pathlib import Path
import numpy as np
import os
import matplotlib.pyplot as plt
from utils import *

def judge_outliers(a1, a2):
    threshold = 1000
    if (a1[0] - a2[0]) ** 2 + (a1[1] - a2[1]) ** 2 > threshold ** 2:
        return True
    else:
        return False

def judge_outliers_row(row1, row2):
    row1_point = [[row1[df_columns[y + x]] for x in range(2)] for y in [0, 3, 6]]
    row2_point = [[row2[df_columns[y + x]] for x in range(2)] for y in [0, 3, 6]]
    if judge_outliers(row1_point[0], row2_point[0]) or judge_outliers(row1_point[1], row2_point[1]) or judge_outliers(row1_point[1], row2_point[1]):
        return True
    else:
        return False

#读取h5文件
video_path='D:\ymazeV'
video='207.mp4'
DLCscorer='DLC_resnet50_ymazeanalysis10_27shuffle1_50000'
dataname = str(Path(video).stem) + DLCscorer + '.h5'

#loading output of DLC
df = pd.read_hdf(os.path.join(video_path,dataname),header=4)

df_columns = df.columns.values
i = 1
while True:
    if judge_outliers_row(df.loc[i - 1], df.loc[i]):
        df = df.drop(i)
        df = df.reset_index(drop = True)
    else:
        i += 1
    if i == len(df):
        break
print(i)

vd = LoadVideo()
vd.SetRefFrame()
area = MarkArea(vd.ref_frame)

poi_list = [[[int(df.loc[i][df_columns[y + x]]) for x in range(2)] for y in [0, 3, 6]] for i in range(len(df))]
marker_list = [[] for x in range(4)]
print(poi_list)
for i in range(len(poi_list)):
    for j in range(3):
        marker_list[j].append(area.PointInRegion(poi_list[i][j]))
    if marker_list[0][i] == marker_list[1][i] and marker_list[0][i] == marker_list[2][i] and marker_list[1][i] == marker_list[2][i]:
        marker_list[3].append(marker_list[0][i])
    else:
        marker_list[3].append('0')
df[(df_columns[0][0], df_columns[0][1], 'marker')] = marker_list[0]
df[(df_columns[3][0], df_columns[3][1], 'marker')] = marker_list[1]
df[(df_columns[6][0], df_columns[6][1], 'marker')] = marker_list[2]
df[(df_columns[0][0], 'total', 'marker')] = marker_list[3]
df.to_excel('./result.xlsx')
from cv2 import threshold
import pandas as pd
from pathlib import Path
import numpy as np
import os
import matplotlib.pyplot as plt
from utils import *
from collections import Counter

filepath = './video/207DLC_resnet50_ymazeanalysis10_27shuffle1_50000.h5'
df = pd.read_hdf(filepath)
df = df.droplevel('scorer',axis=1)
#%%
vd = LoadVideo()
area = MarkArea(vd.ref_frame)
#%%
poi1=[]; poi2=[]; poi3=[]
for i in range(len(df)):
    poi1.append([round(df[('bodypart1','x')][i]),
                 round(df[('bodypart1','y')][i])])
    poi2.append([round(df[('bodypart2','x')][i]),
                 round(df[('bodypart2','y')][i])])
    poi3.append([round(df[('bodypart3','x')][i]),
                 round(df[('bodypart3','y')][i])])
#%%
pos1 = [area.PointInRegion(poi, isnum=True) for poi in poi1]
pos2 = [area.PointInRegion(poi, isnum=True) for poi in poi2]
pos3 = [area.PointInRegion(poi, isnum=True) for poi in poi3]
#%%
pos = []
for i in range(len(pos1)):
    poss = [pos1[i], pos2[i], pos3[i]]
    cnt = dict(Counter(poss))
    pos_now3 = [key for key,value in cnt.items() if value==3]
    pos_now2 = [key for key,value in cnt.items() if value==2]
    pos_now1 = [key for key,value in cnt.items() if value==2 and key==0]
    if 4 in poss:
        pos.append(4)
    elif pos_now3:
        pos.append(pos_now3[0])
    elif pos_now1:
        pos.append([key for key,value in cnt.items() if value==1][0])
    elif pos_now2 and 4 not in poss:
        pos.append(4)
    elif pos_now2:
        pos.append(pos_now2[0])
    else:
        pos.append(4)
        
    # elif 0 in poss:
    #     poss = poss.remove(0)
    #     if poss[0]==poss[1]:
    #         pos.append(poss[0])
    #     else:
    #         pos.append(4)
#%%
# import time
plt.figure('test')
i=512
plt.imshow(vd.frames[i],cmap="gray")
plt.text(50,80,str(pos[i]),fontsize=50,color='r')
    # time.sleep(1/17)
#%%
temp = pos[0]
frm = 0
hh = []
for i in range(8370):
    if pos[i] == temp:
        frm += 1
    else:
        hh.append([pos[i-1],frm])
        temp = pos[i]
        frm = 1
hh.append([pos[i],frm])

hh = [[i[0],i[1]/vd.fps] for i in hh]       
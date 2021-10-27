# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 16:46:20 2021

@author: Fanding Xu
"""

import numpy as np
import matplotlib.pyplot as plt
import cv2 
from PIL import Image
import tkinter.filedialog
from tkinter import *
from PIL import Image
from pylab import *

class Video:
    def __init__(self, frames, size, total_frames, fps):
        self.frames = frames
        self.size = size
        self.total_frames = total_frames
        self.fps = fps
        self.ref_frame = self.frames[11]
        
    def SetRefFrame(self, target_frame = 10): # 手动设置参考帧，不设置或无参数默认为第10帧
        self.ref_frame = self.frames[target_frame+1]
        
# Area：通过所有顶点封装迷宫区域
class Area:
    def __init__(self, x):
        self.x0 = [list(x[i]) for i in [2,5,8]]
        self.x1 = [list(x[i]) for i in [0,1,2,8]]
        self.x2 = [list(x[i]) for i in [2,3,4,5]]
        self.x3 = [list(x[i]) for i in [5,6,7,8]]
    
    def PointInRegion(self, poi):
        if isPointWithinRegion(poi,self.x0):
            return 'Reg 0'
        if isPointWithinRegion(poi,self.x1):
            return 'Reg 1'
        if isPointWithinRegion(poi,self.x2):
            return 'Reg 2'
        if isPointWithinRegion(poi,self.x3):
            return 'Reg 3'
        return 'Out'
    
    def DrawRegions(self):
        regs = {'0': self.x0, '1': self.x1, '2': self.x2, '3': self.x3}
        for i in ['0','1','2','3']:
            draw_reg(regs[i])
            
# =============================================================================
# 视频输入与初始化
# =============================================================================
def process_bar(percent, start_str='Loading', end_str='100%', total_length=0):
    bar = ''.join(["\033[31m%s\033[0m"%'   '] * int(percent * total_length)) + ''
    bar = '\r' + start_str + bar.ljust(total_length) + ' {:0>4.1f}%|'.format(percent*100) + end_str
    print(bar, end='', flush=True)
    
    
def LoadVideo():
    root = Tk()
    filename = tkinter.filedialog.askopenfilename(title='选择视频文件（.mp4）',
                                                  filetypes=[('mp4', '*.mp4'),
                                                             ('All Files', '*')],
                                                  initialdir='C:\\Windows\\WsdlFile')
    root.destroy()
    root.mainloop()
    if filename == '':
        print("error: null file")
    else:
        cap = cv2.VideoCapture(filename)
        video_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                      int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps = int(cap.get(cv2.CAP_PROP_FPS))
        frames = []
        for i in range(1,total_frames+1):
            process_bar(i/total_frames)
            ret, frame = cap.read() 
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            frames.append(frame)
        cap.release()
        print("\nVideo loaded: filename" + filename)
    return Video(frames, video_size, total_frames, video_fps)


# 9点标记检测区域
def MarkArea(img, gauss_size = 3, gauss_sima = 10, tresh1 = 50, tresh2 = 150):
    img = cv2.GaussianBlur(img, (gauss_size,gauss_size), gauss_sima)
    canny = cv2.Canny(img, tresh1, tresh2)
    plt.figure('Area Marker', dpi = 150)
    plt.imshow(canny, cmap="gray")
    plt.axis('off')
    plt.title('Click to mark 9 inflection points successively.\nNotice the order is as shown in formpic.png')
    print('Please click to mark 9 inflection points successively, the order is as shown in formpic.png')
    x = ginput(9)
    plt.close('Area Marker')
    print('Area marked: ', x)
    return Area(x)
# =============================================================================
# 位置识别
# =============================================================================
# draw_reg：绘制区域
def draw_reg(reg):
    X = [reg[i][0] for i in range(len(reg))]
    X.append(reg[0][0])
    Y = [reg[i][1] for i in range(len(reg))]
    Y.append(reg[0][1])
    plt.plot(X,Y,'o--')

# def Region2Poly(reg):
#     poly = [[reg[i-1],reg[i]] for i in range(len(reg))]
#     return poly


# isRayIntersectsSegment：判断点射线是否与边相交
def isRayIntersectsSegment(poi, s_poi, e_poi): #[x,y] [lng,lat]
    #输入：判断点，边起点，边终点，都是[lng,lat]格式数组
    if s_poi[1]==e_poi[1]: #排除与射线平行、重合，线段首尾端点重合的情况
        return False
    if s_poi[1]>poi[1] and e_poi[1]>poi[1]: #线段在射线上边
        return False
    if s_poi[1]<poi[1] and e_poi[1]<poi[1]: #线段在射线下边
        return False
    if s_poi[1]==poi[1] and e_poi[1]>poi[1]: #交点为下端点，对应spoint
        return False
    if e_poi[1]==poi[1] and s_poi[1]>poi[1]: #交点为下端点，对应epoint
        return False
    if s_poi[0]<poi[0] and e_poi[1]<poi[1]: #线段在射线左边
        return False

    xseg=e_poi[0]-(e_poi[0]-s_poi[0])*(e_poi[1]-poi[1])/(e_poi[1]-s_poi[1]) #求交
    if xseg<poi[0]: #交点在射线起点的左侧
        return False
    return True  #排除上述情况之后


# isPointWithinRegion：判断点是否在区域内
def isPointWithinRegion(poi, reg):
    #输入：点，区域（四个顶点列表）
    sinsc=0 #交点个数
    for i in range(len(reg)): #循环每条边
        s_poi=reg[i-1]
        e_poi=reg[i]
        if isRayIntersectsSegment(poi, s_poi, e_poi):
            sinsc+=1 #有交点就加1

    return True if sinsc%2==1 else  False


# ShowPointMarker：绘制当前点位置标记
def ShowPointMarker(poi, marker):
    plt.text(poi[0],poi[1]+30,marker,fontsize=10,color='violet')


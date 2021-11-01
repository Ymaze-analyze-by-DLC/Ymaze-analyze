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
    def __init__(self, x, size):
        self.x0 = [x[i] for i in [2,5,8]]
        self.x1 = [x[i] for i in [0,1,2,8]]
        self.x2 = [x[i] for i in [2,3,4,5]]
        self.x3 = [x[i] for i in [5,6,7,8]]
        self.map = GenerateMap([self.x0, self.x1, self.x2, self.x3], size)
    def PointInRegion(self, poi, isnum=  False):
        # 横纵坐标对换是因为图像第0维是列数（横坐标），第1维是行数（纵坐标）
        # 而map是矩阵，其第0维是行数（纵坐标），第1维是行数（横坐标）
        marker = ['Out', 'Reg 1', 'Reg2', 'Reg 3', 'Reg 0']
        pos = int(self.map[poi[1]][poi[0]])
        if isnum:
            return pos
        else:
            return marker[pos]
    
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
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frames = []
        for i in range(1,total_frames+1):
            process_bar(i/total_frames)
            ret, frame = cap.read() 
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            frames.append(frame)
        cap.release()
        print("\nVideo loaded: " + filename)
        print("video info: FPS={}; SIZE={}; FRAMES={}".format(video_fps,video_size,total_frames))
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
    # x = [list(x[i]) for i in range(len(x))]
    x = [[round(x[i][0]), round(x[i][1])] for i in range(len(x))]
    print('Area marked: ', x)
    return Area(x, img.shape)

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

# GenerateMap：产生区域映射谱矩阵
def GenerateMap(regs:list, size:tuple):
    # 注意这里的size是获取关键帧shape获得的，其横纵坐标是矩阵的，与图像横纵坐标相反
    # 横纵坐标对换是因为图像第0维是列数（横坐标），第1维是行数（纵坐标）
    # 而map是矩阵，其第0维是行数（纵坐标），第1维是行数（横坐标）
    reg_map = np.zeros(size)
    for i in range(len(regs)):
        if i == 0:
            cv2.fillConvexPoly(reg_map, np.array(regs[i]), (len(regs)))
        else:
            cv2.fillConvexPoly(reg_map, np.array(regs[i]), (i))
    return reg_map

def PointInRegion(MAP,poi):
    
    return str(MAP[poi[1]][poi[0]]) 

# ShowPointMarker：绘制当前点位置标记
def ShowPointMarker(poi, marker):
    plt.plot(poi[0],poi[1],'o',color='violet')
    plt.text(poi[0],poi[1]+30,marker,fontsize=10,color='violet')


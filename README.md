# Ymaze-analyze

utils.py
1. 使用LoadVideo()读取视频，如： vd = LoadVideo(), 选择文件，读取后返回 vd 是一个 Video 类对象
2. 读取视频后通过 vd.SetRefFrame() 选择参考帧，括号里填整数即选择第几帧作为参考，此项可忽略则默认第10帧
3. 使用 area = MarkArea(vd.ref_frame) 在参考帧上标注区域，按顺序点击9个拐点，顺序如图formpic.png所示，
标记后返回 area 是一个 Area 类对象
4. 通过 marker = area.PointInRegion(poi) 判断点poi在哪个小区域内，poi 为一列表存储该点横纵坐标信息
如[100, 150]，返回 marker 为一字符串如 'Reg 0'，具体代表哪个区域参照formpic.png
5. area.DrawRegions() 可以在figure内高亮显示所有区域；
ShowPointMarker(poi, marker) 可以在figure上标记点 poi 的 marker
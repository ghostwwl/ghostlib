#! /usr/bin/env python
#-*- coding:GBK -*-

#*************************************
# FileName: maxarea.py
# Author  : wule
# Email   : ghostwwl@gmail.com
# Date    : 2010.2.25
# Note    : 图片最大联通区域获取
#           用来识别图片主体 
#	    对拍摄商品照片 自动找到商品主体 然后裁剪
#*************************************

import sys, os
from opencv import cv
from opencv import highgui
#from opencv import matlab_syntax
from glob import glob
import random
from GFunc import message
   
def get_maxarea(filename, dstpath, position=16, border=50, dst_width=800, debug=1):
    # 调节position 和 cvThreshold里的参数 来实现复杂图片目标识别
    dstfile = os.path.join(dstpath, 'd_%s' % os.path.basename(filename))
    if os.path.exists(dstfile): return
    image = highgui.cvLoadImage (filename)
    
    if not image:
        print "Error loading image '%s'" % filename
        return
    
    gray = cv.cvCreateImage (cv.cvSize (image.width, image.height), 8, 1)
    edge = cv.cvCreateImage (cv.cvSize (image.width, image.height), 8, 1)
    cv.cvCvtColor (image, gray, cv.CV_BGR2GRAY)
    cv.cvNot (gray, edge)    
    # 高斯滤波 
    #cv.cvSmooth(edge, edge, cv.CV_GAUSSIAN)
    # 还是用中值滤波
    cv.cvSmooth(edge, edge, cv.CV_MEDIAN, 3, 0, 0, 0)
    # 对图片进行腐蚀 去背景干扰
    cv.cvErode(edge, edge)
    cv.cvCanny (gray, edge, position, position * 4, 3)
    # 连接相近的边缘
    cv.cvSmooth(edge, edge, cv.CV_GAUSSIAN)
    # 连通小区域
    cv.cvDilate(edge, edge)
    # 设定轮廓阈值
    #cv.cvThreshold(edge,edge,position*1.0,255,cv.CV_THRESH_BINARY)
    if debug == 1: 
        col_edge = cv.cvCreateImage (cv.cvSize (image.width, image.height), 8, 3)
        cv.cvSetZero (col_edge)
        cv.cvCopy (image, col_edge, edge)
    
    # 分配内存
    store = cv.cvCreateMemStorage(0)
    # 获取所有轮廓
    num_contours, contours = cv.cvFindContours(edge, store, cv.sizeof_CvContour, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE )
    # 获取物体外轮廓
    #num_contours, contours = cv.cvFindContours(edge, store, cv.sizeof_CvContour, cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_SIMPLE)
    
    maxArea = 0
    max2Area = 0
    contmax = None
    contmax2 = None
    for contour in contours.hrange():
        # 绘画区所有区域
        if debug == 1:
            color = cv.CV_RGB( random.randint(0,255)&255, random.randint(0,255)&255, random.randint(0,255)&255 )
            cv.cvDrawContours( col_edge, contour, color, color, -1, cv.CV_FILLED, 8 )
        # 图片中找到我们需要的目标 一般是最大连通区域
        #获取当前轮廓面积
        area = abs(cv.cvContourArea( contour ))
        #print area
        if area > maxArea:
            contmax2 = contmax
            max2Area = maxArea
            contmax = contour
            maxArea = area
        elif max2Area < area < maxArea:
            contmax2 = contour
            max2Area = area
    if debug == 1:
        print 'FindContours:', num_contours
        print 'MaxArea:',maxArea
        print 'SecondArea:', max2Area
    
    # 获取最大区域矩形块
    aRect = cv.cvBoundingRect( contmax, 0 )
    #bRect = cvBoundingRect( contmax1, 0 )
    
    # 识别最大联通区域扩展边框
    x = max(0, aRect.x - border)
    y = max(0, aRect.y - border)
    width = min(image.width, aRect.x + aRect.width + border) - x
    height = min(image.height, aRect.y + aRect.height + border) - y
    rcenter = cv.cvPoint2D32f(x + width/2.0, y + height/2.0)
    dstimg = cv.cvCreateImage (cv.cvSize (width, height), image.depth, image.nChannels)
    
    #原始区域的不加边框
    #rcenter = cv.cvPoint2D32f(aRect.x + aRect.width/2.0, aRect.y + aRect.height/2.0)
    #dstimg = cv.cvCreateImage (cv.cvSize (aRect.width, aRect.height), 8, 3)
    #cv.cvSetZero(dstimg)
    
    # 获取我们需要的矩形区域
    cv.cvGetRectSubPix(image, dstimg, rcenter)
    
    # 对结果图片进行缩放
    rate = float(width) / height
    dst_height = dst_width / rate
    outImg = cv.cvCreateImage(cv.cvSize(int(dst_width), int(dst_height)), dstimg.depth, dstimg.nChannels)
    # 缩放的时候使用像素关系重采样(缩放时效果最好的插值算法)，避免缩小后出现水波纹
    cv.cvResize(dstimg, outImg, cv.CV_INTER_AREA)
    highgui.cvSaveImage(dstfile, outImg)
    
    # 保存识别过程图片用于调试
    if debug == 1:
        debug_img = os.path.join(dstpath, 'cur_debug.jpg')
        highgui.cvSaveImage(debug_img, col_edge)
    
    # 内存释放
    cv.cvReleaseImage(image)
    cv.cvReleaseImage(outImg)
    cv.cvReleaseImage(dstimg)
    cv.cvReleaseImage(gray)
    cv.cvReleaseImage(edge)
    cv.cvReleaseMemStorage(store)
    if debug == 1:
        cv.cvReleaseImage(col_edge)
        del col_edge
    del image, outImg, dstimg, gray, edge, store
    
    
def main(inpath, dstpath, position=16, border=50, dstwidth=800, debug=0):
    imagefiles = glob(os.path.join(inpath, '*.jpg'))
    if not os.path.exists(dstpath):
        message('dst save path %s not exists!' % dstpath, 2)
        try:
            os.makedirs(dstpath)
            message('create dir %s ok' % dstpath)
        except Exception, e: message(str(e), 3)
    for filename in imagefiles:
        try:
            get_maxarea(filename, dstpath, position, border, dstwidth, debug)
            message('Identification picture [ %s ] OK' % filename)
        except Exception, e:
            message('Identification picture [ %s ] err.(%s)' % (filename, str(e)), 3)
    message('------- END -------')
    

if __name__ == '__main__':
    if len(sys.argv) < 3:
        message('UseAge: maxarea.py inpath dstpath position border dstwidth debug')
        sys.exit()
    inpath = sys.argv[1]
    dstpath = sys.argv[2]
    position = 16
    border = 50
    dstwidth = 800
    debug = 1
    if len(sys.argv) == 4:
        position = int(sys.argv[3])
    elif len(sys.argv) == 5:
        position = int(sys.argv[3])
        border = int(sys.argv[4])
    elif len(sys.argv) == 6:
        position = int(sys.argv[3])
        border = int(sys.argv[4])
        dstwidth = int(sys.argv[5])
    elif len(sys.argv) == 7:
        position = int(sys.argv[3])
        border = int(sys.argv[4])
        dstwidth = int(sys.argv[5])
        debug = int(sys.argv[6])
        
    main(inpath, dstpath, position, border, dstwidth, debug)

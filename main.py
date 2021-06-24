import AppKit
import pyautogui
import argparse
import os
import time
import cv2
import shutil
import numpy as np

imglist=[]

def mosaic(img,args):
    if args.strength==1:
        return img
    small = cv2.resize(img, None, fx=args.strength, fy=args.strength, interpolation=cv2.INTER_NEAREST)
    mosaiced=cv2.resize(small, img.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)
    if args.exclock==True:
        height, width, channels = img.shape
        #[y1:y2,x1:x2]
        mosaiced[0:min(height,70), width-min(width,300):width] = img[0:min(height,70), width-min(width,300):width] 
    return mosaiced

def reduce_img_size(img,args):
    if args.reduce==1.0:
        return img
    return cv2.resize(img, None, fx=args.reduce, fy=args.reduce, interpolation=cv2.INTER_NEAREST)

def shoot_interval(args,key): 
    global imglist
    counter=0
    while (not args.length) or (counter*args.interval<args.length*args.fps):
        screenshot = pyautogui.screenshot()#'./temp/screenshot_{}_{}.png'.format(key,counter)
        open_cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        imglist.append( reduce_img_size( mosaic( open_cv_image,args),args ) )
        counter+=1
        time.sleep(args.interval)

def make_video(args,key):
    global imglist
    print("making video...")
    if len(imglist)<1:
        sys.exit()
    height, width, channels = imglist[0].shape
    print(height, width, channels)
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    video = cv2.VideoWriter('./save/timelapse_{}.mp4'.format(key),fourcc, args.fps, (width,height),isColor=True)
    if not video.isOpened():
        print("ERROR: video can't be opened")
        sys.exit() 
    for img in imglist:
        video.write(img)
        cv2.imwrite('test.png',img)
    video.release()
    print('made video!')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", help="set shooting interval (second, defalt is 60)",default=60,type=int)
    parser.add_argument("--fps", help="set fps of video(second, defalut is 20.0)",default=20.0,type=float)
    parser.add_argument("--length", help="set max length of video(second, defalut is infinity)",default=None,type=int)
    parser.add_argument("--strength", help="set strength of mosaic(defalut is 0.05, 1 is no mosaic)",default=0.05,type=float)
    parser.add_argument("--exclock", help="exclude mosaic from upper right (mac's clock region)(default=True)",default=True,type=bool)
    parser.add_argument("--reduce", help="reduce image size(default=1.0)",default=1.0,type=float)
    args = parser.parse_args()
    key=int(time.time())
    try:
        shoot_interval(args,key)
    finally:
        make_video(args,key)

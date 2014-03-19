#!/usr/bin/env python2.7

import cv2
import numpy as np
from collections import deque
import sys

import argparse

parser = argparse.ArgumentParser(description='Time Scope -- when you reallly need some sweet rolling shutter effects')
parser.add_argument('-o', '--output', default=None, help="Filename to output to (leave out for no file output)")

class TimeScope(object):
    def __init__(self, shape, line_size=1, profile=None):
        self.line_size = line_size
        self.profile = profile or (lambda block_num : block_num // line_size // 2)
        self.num_blocks = shape[0] // line_size

        self.queues = [deque(maxlen=self.profile(i*line_size)) for i in xrange(self.num_blocks)]
        self.cur_frame = np.empty(shape, dtype=np.uint8)
        self.empty = np.zeros((line_size,) + shape[1:], dtype=np.uint8)

    def add_frame(self, frame):
        ls = self.line_size
        for i, queue in enumerate(self.queues):
            a = i*ls
            b = (i+1)*ls
            queue.append(frame[a:b,:,:])

    def get_frame(self):
        ls = self.line_size
        for i, queue in enumerate(self.queues):
            a = i*ls
            b = (i+1)*ls
            try:
                self.cur_frame[a:b,:,:] = queue[0]
            except IndexError:
                self.cur_frame[i:i+ls,:,:] = self.empty
        return self.cur_frame


if __name__ == "__main__":
    args = parser.parse_args()
    filename = args.output

    cv2.namedWindow("preview")
    vc = cv2.VideoCapture(0)

    if vc.isOpened(): # try to get the first frame
        rval, frame = vc.read()
    else:
        rval = False
    
    timescope = TimeScope(frame.shape, line_size=2)
    if filename: 
        fourcc = cv2.cv.CV_FOURCC(*'DIVX')
        out = cv2.VideoWriter(filename, fourcc, 25.0, frame.shape[-2::-1])
    while rval:
        cur_frame = timescope.get_frame()
        cv2.imshow("preview", cur_frame)
        if filename:
            out.write(cur_frame)
    
        rval, frame = vc.read()
        timescope.add_frame(frame)
    
        key = cv2.waitKey(20)
        if key == 27: # exit on ESC
            break
    
    if filename:
        out.release()
    vc.release()
    cv2.destroyWindow("preview")

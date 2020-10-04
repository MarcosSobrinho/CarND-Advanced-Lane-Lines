import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

#Sobel calculations

def abs_sobel_thresh(img, orient='x', sobel_kernel=5, thresh=(30, 255), img_type = 'color'):
    
    if img_type == 'color':
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    elif img_type == 'gray':
        gray = img
    
    if orient == 'x':
        sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize = sobel_kernel)
    elif orient == 'y':
        sobel = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize = sobel_kernel)
        
    abs_sobel = np.absolute(sobel)
    scaled_sobel = np.uint8(255*abs_sobel/np.max(abs_sobel))
    binary_mask = np.zeros_like(scaled_sobel)
    binary_mask[(scaled_sobel >= thresh[0]) & (scaled_sobel <= thresh[1])] = 1
    return binary_mask

def mag_sobel_thresh(img, sobel_kernel=5, mag_thresh=(30, 255), img_type = 'color'):
    
    if img_type == 'color':
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    elif img_type == 'gray':
        gray = img

    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize = sobel_kernel)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize = sobel_kernel)
    abs_sobel = np.sqrt(sobel_x**2 + sobel_y**2)
    
    scaled_sobel = np.uint8(255*abs_sobel/np.max(abs_sobel))
    binary_mask = np.zeros_like(scaled_sobel)
    binary_mask[(scaled_sobel >= mag_thresh[0]) & (scaled_sobel <= mag_thresh[1])] = 1
    
    return binary_mask 

def dir_threshold(img, sobel_kernel=5, thresh=(0, np.pi/2), img_type = 'color'):
    
    if img_type == 'color':
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    elif img_type == 'gray':
        gray = img
        
    sobel_x = np.absolute(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize = sobel_kernel))
    sobel_y = np.absolute(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize = sobel_kernel))
    
    arg = np.arctan2(sobel_y, sobel_x)
    binary_mask = np.zeros_like(arg)
    binary_mask[(arg >= thresh[0]) & (arg <= thresh[1])] = 1
    
    return binary_mask

#HLS transformations

def s_channel_threshold(img, thresh=(130, 255)):
    hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
    s_channel = hls[:,:,2]
    
    s_binary = np.zeros_like(s_channel)
    s_binary[(s_channel >= thresh[0]) & (s_channel <= thresh[1])] = 1
    return s_channel, s_binary

def h_channel_threshold(img, thresh=(15, 100)):
    hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
    h_channel = hls[:,:,0]
    
    h_binary = np.zeros_like(h_channel)
    h_binary[(h_channel >= thresh[0]) & (h_channel <= thresh[1])] = 1
    return h_channel, h_binary

# Perspective transform

def warp(img):
    
    img_size = (img.shape[1], img.shape[0])
    
    src = np.float32([
            [200, 700],
            [1110, 700],
            [590, 450],
            [690, 450]
        ])
    
    dst = np.float32([
            [200, 700],
            [950, 700],
            [200, 0],
            [950, 0],
        ])
    
    M = cv2.getPerspectiveTransform(src, dst)
    M_inv = cv2.getPerspectiveTransform(dst, src)
    
    warped = cv2.warpPerspective(img, M, img_size, flags=cv2.INTER_LINEAR)
    
    return warped, M, M_inv
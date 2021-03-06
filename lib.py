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
            [1280 - 200, 700],
            [590, 450],
            [1280 - 590, 450]
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

# Fit polynomials

def find_lane_pixels(binary_warped, nwindows):
    # Take a histogram of the bottom half of the image
    histogram = np.sum(binary_warped[binary_warped.shape[0]//2:,:], axis=0)
    # Create an output image to draw on and visualize the result
    out_img = np.dstack((binary_warped, binary_warped, binary_warped))
    # Find the peak of the left and right halves of the histogram
    # These will be the starting point for the left and right lines
    midpoint = np.int(histogram.shape[0]//2)
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    # HYPERPARAMETERS
    # Choose the number of sliding windows
    
    # Set the width of the windows +/- margin
    margin = 100
    # Set minimum number of pixels found to recenter window
    minpix = 50

    # Set height of windows - based on nwindows above and image shape
    window_height = np.int(binary_warped.shape[0]//nwindows)
    # Identify the x and y positions of all nonzero pixels in the image
    nonzero = binary_warped.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    # Current positions to be updated later for each window in nwindows
    leftx_current = leftx_base
    rightx_current = rightx_base

    # Create empty lists to receive left and right lane pixel indices
    left_lane_inds = []
    right_lane_inds = []

    # Step through the windows one by one
    for window in range(nwindows):
        # Identify window boundaries in x and y (and right and left)
        win_y_low = binary_warped.shape[0] - (window+1)*window_height
        win_y_high = binary_warped.shape[0] - window*window_height
        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin
        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin
        
        # Identify the nonzero pixels in x and y within the window #
        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
        (nonzerox >= win_xleft_low) &  (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & 
        (nonzerox >= win_xright_low) &  (nonzerox < win_xright_high)).nonzero()[0]
        
        # Append these indices to the lists
        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)
        
        # If you found > minpix pixels, recenter next window on their mean position
        if len(good_left_inds) > minpix:
            leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:        
            rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

    # Concatenate the arrays of indices (previously was a list of lists of pixels)
    try:
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
    except ValueError:
        # Avoids an error if the above is not implemented fully
        pass

    # Extract left and right line pixel positions
    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds] 
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]

    return leftx, lefty, rightx, righty, out_img


def fit_polynomial(binary_warped, nwindows):
    # Find our lane pixels first
    leftx, lefty, rightx, righty, out_img = find_lane_pixels(binary_warped, nwindows)

    # Fit a second order polynomial to each using `np.polyfit`
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)

    # Generate x and y values for plotting
    ploty = np.linspace(0, binary_warped.shape[0]-1, binary_warped.shape[0] )
    try:
        left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
        right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]
    except TypeError:
        # Avoids an error if `left` and `right_fit` are still none or incorrect
        print('The function failed to fit a line!')
        left_fitx = 1*ploty**2 + 1*ploty
        right_fitx = 1*ploty**2 + 1*ploty

    ## Visualization ##
    # Colors in the left and right lane regions
    out_img[lefty, leftx] = [255, 0, 0]
    out_img[righty, rightx] = [0, 0, 255]

    # Plots the left and right polynomials on the lane lines
    # plt.plot(left_fitx, ploty, color='yellow')
    # plt.plot(right_fitx, ploty, color='yellow')

    return out_img, left_fitx, right_fitx

def unwarp(warped, undist, Minv, left_fitx, right_fitx):
    # Create an image to draw the lines on
    warp_zero = np.zeros_like(warped).astype(np.uint8)
    color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

    # Recast the x and y points into usable format for cv2.fillPoly()
    ploty = np.linspace(0, warped.shape[0]-1, warped.shape[0] )
    pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
    pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
    pts = np.hstack((pts_left, pts_right))

    # Draw the lane onto the warped blank image
    cv2.fillPoly(color_warp, np.int_([pts]), (0,255, 0))

    # Warp the blank back to original image space using inverse perspective matrix (Minv)
    newwarp = cv2.warpPerspective(color_warp, Minv, (undist.shape[1], undist.shape[0])) 
    # Combine the result with the original image
    result = cv2.addWeighted(undist, 1, newwarp, 0.3, 0)
    
    return result

def calculateCurvature(fitx, fity):
    xm_per_pix = 3.7/700
    ym_per_pix = 30/720
    
    fitx *= xm_per_pix
    fity *= ym_per_pix
    
    i = int(0.5*fitx.size)
    
    dxy = (fitx[i+1] - fitx[i-1]) / (fity[i+1] - fity[i-1])
    ddxy = (fitx[i+1] - fitx[i]) / (fity[i+1] - fity[i])
    ddxy -= ((fitx[i] - fitx[i-1]) / (fity[i] - fity[i-1]))
    ddxy /= (fity[i+1] - fity[i-1])
    
    r_c = (1 + dxy**2)**1.5
    r_c /= np.abs(ddxy)
    
    return r_c

def calculateDisplacement(right_fitx, left_fitx):
    img_center = 1280/2
    lane_center = 0.5*(right_fitx[700] + left_fitx[700])
    xm_per_pix = 3.7/700
    return np.abs(lane_center - img_center)*xm_per_pix

def addText(img, radius, displacement = 0.0):    
    rad_line = "Curvature Radius: " + "{:.2f}".format(radius) + " m"
    dis_line = "Displacement: " + "{:.2f}".format(displacement) + " m"
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, rad_line, (10, 70), font, 2.5, (255, 0, 0), 3)
    cv2.putText(img, dis_line, (10, 140), font, 2.5, (255, 0, 0), 3)
    
    return img
    
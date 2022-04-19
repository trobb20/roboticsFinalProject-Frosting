#!/usr/bin/env python3
#####################################################################
### Created by Megan Jenney
### Last Edited 17 April 2022
### 
### Intro to Robotics and Mechanics
### Tufts University Spring 2022
### Department of Mechanical Engineering
### Megan Jenney and Jennifer Liu
###
### Final Project: Robot Cake Maker
### Image Processing Team
### This script processes an image uploaded through Airtable, scales
###     it to the correct shape for the cake, and processes contour
###     lines along which frosting will be dispensed.
### Background and image contours are sent as seaprate lists of
###     coordinates in G-code ( [x,y,e] ) format.
### Images are assumed to have a white background and have clear
###     outlines, such as clipart or a logo.
#####################################################################

import numpy as np
import cv2
import requests
import urllib.request

## function definitions
def imgFromAirtable():
    base_id = 'appuhn9X6CJyPGaho'
    img_table = 'image'
    # read from file
    api_key = open('api_key.txt').read()
    headers = {"Authorization": "Bearer " + api_key}

    query = "sort%5B0%5D%5Bfield%5D=Created"
    url = "https://api.airtable.com/v0/" + base_id + "/" + img_table + "?" + query

    params = ()
    response = requests.get(url, params=params, headers=headers).json()

    rcd_len = len(response["records"])
    image_url = response["records"][rcd_len-1]["fields"]["Image"][0]["url"]
    img_file, headers = urllib.request.urlretrieve(image_url)

    return cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)

def rowsToAdd(pix_col, pix_row):
    in_pix_ratio = pix_col / 6
    corr_rows = in_pix_ratio * 7.5
    add_rows = abs(int(corr_rows) - pix_row)
    
    if not add_rows % 2 == 0:
        add_top = int(add_rows / 2 + 0.5)
        add_btm = int(add_rows / 2 - 0.5)
    else:
        add_top = int(add_rows / 2)
        add_btm = int(add_rows / 2)
    
    return (add_top, add_btm)

def colsToAdd(pix_row, pix_col):
    in_pix_ratio = pix_row / 7.5
    corr_cols = in_pix_ratio * 6
    add_cols = abs(int(corr_cols) - pix_col)
    
    if not add_cols % 2 == 0:
        add_lft = int(add_cols / 2 + 0.5)
        add_rgt = int(add_cols / 2 - 0.5)
    else:
        add_lft = int(add_cols / 2)
        add_rgt = int(add_cols / 2)
    
    return (add_lft, add_rgt)

def addRows(add_top, add_btm, img):
    pix_col = np.shape(img)[1]
    
    top_shape = (add_top, pix_col)
    top = np.full(top_shape, 0)
    btm_shape = (add_btm, pix_col)
    btm = np.full(btm_shape, 0)
    
    return np.concatenate((top, img, btm))

def addCols(add_lft, add_rgt, img):
    pix_row = np.shape(img)[0]
    
    lft_shape = (pix_row, add_lft)
    lft = np.full(lft_shape, 0)
    rgt_shape = (pix_row, add_rgt)
    rgt = np.full(rgt_shape, 0)
    
    return np.concatenate((lft, img, rgt), axis=1)

def changeImgRatio(rows, cols, img):
    pan_ratio = 7.5 / 6
    img_ratio = rows / cols

    if img_ratio < pan_ratio:
        add_top, add_btm = rowsToAdd(cols, rows)
        return addRows(add_top, add_btm, img)
        
    elif img_ratio > pan_ratio:
        add_lft, add_rgt = colsToAdd(rows, cols)
        return addCols(add_lft, add_rgt, img)
    else:
        return img

def getToDimensions(img):
    in_to_mm = 25.4
    pan_wth = 6 * in_to_mm
    pan_hgt = 7.5 * in_to_mm
    pan_shape = int(pan_wth), int(pan_hgt)

    wth_ratio = pan_wth / img.shape[0]
    hgt_ratio = pan_hgt / img.shape[1]

    return cv2.resize(img, pan_shape, wth_ratio, hgt_ratio, cv2.INTER_AREA)

def getImgCoords(contours):
    coordinates = []
    
    for line in contours[0]:
        num_coords = len(line)
        for point_num in range(num_coords):
            coord = line[point_num][0]
            if (point_num == 0) or (num_coords-point_num <=5):
                coord = np.append(coord, 0)
            else:
                coord = np.append(coord, 1)
        
            coordinates.append(coord)

    # return to original pos
    coordinates.append([0,0,0])

    return np.asarray(coordinates)

def getImg():
    grayscale_img = imgFromAirtable()
    _, binary_img = cv2.threshold(grayscale_img, 128, 255, cv2.THRESH_BINARY)
    inv_img = cv2.bitwise_not(binary_img)
    rows = np.shape(binary_img)[0]
    cols = np.shape(binary_img)[1]
    resized_img = changeImgRatio(rows, cols, inv_img).astype('uint8')
    cv2.imwrite("resized_image.jpeg", resized_img)

    dim_img = getToDimensions(resized_img)
    cv2.imwrite("dim_image.jpeg", dim_img)

    ctrs = cv2.findContours(dim_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return (getImgCoords(ctrs), dim_img)

def getPos(rows, cols, spacing):
    num_x_y = int(1 / spacing)
    x = np.linspace(0, cols, num_x_y)
    y = np.linspace(0, rows, num_x_y)
    Y,X = np.meshgrid(y,x)

    return np.column_stack([X.ravel(), Y.ravel()]).astype(int)

def reverseBgdLines(positions, spc_inv):
    rev_coords = []
    for i in range(spc_inv):
        temp_crd_list = positions[(i*spc_inv):(((i+1)*spc_inv))]
        if (i+1) % 2 == 0:
            for j in reversed(range(spc_inv)):
                rev_coords.append(temp_crd_list[j])
        else:
            for j in range(spc_inv):
                rev_coords.append(temp_crd_list[j])

    return rev_coords

def gcodeBgdCoords(coords, num_coords):
    coordinates = []
    for i in range(num_coords):
        if (i == 0) or ((num_coords - i) <= 10):
            coord = np.append(coords[i], 0)
        else:
            coord = np.append(coords[i], 1)
        
        coordinates.append(coord)

    # return to original pos
    coordinates.append([0,0,0])

    return np.asarray(coordinates)

def getBgdCoords(positions, spacing):
    num_coords = int(len(positions))
    spc_inv = int(1/spacing)

    rev_coords = reverseBgdLines(positions, spc_inv)

    return gcodeBgdCoords(rev_coords, num_coords)

def getBgd(img):
    blank = np.zeros(img.shape, dtype='uint8')

    blank_rows = blank.shape[0]
    blank_cols = blank.shape[1]
    spacing_pt = .04
    positions = getPos(blank_rows, blank_cols, spacing_pt)

    return getBgdCoords(positions.tolist(), spacing_pt)

def run():
    img_coordinates, dim_img = getImg()
    np.savetxt("img_coordinates.csv", img_coordinates, delimiter=',')

    bgd_coordinates = getBgd(dim_img)
    np.savetxt("bgd_coordinates.csv", bgd_coordinates, delimiter=',')

if __name__ == '__main__':
    run()

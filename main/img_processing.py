#!/usr/bin/env python3
#####################################################################
### Created by Megan Jenney
### Last Edited 19 April 2022
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
### Images are assumed to have a white background and clear outlines,
###     such as clipart or a logo.
#####################################################################

import numpy as np
import cv2
import requests
import urllib.request

def __imgFromAirtable():
    """
    Get last image submitted to Airtable form.

    Requires existence of text file containing the API key of a user
    with Airtable base edit access.

    Returns
    -------
    np.ndarray
        Array of image submitted in grayscale.
    """
    base_id = 'appuhn9X6CJyPGaho'
    img_table = 'image'
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

def __rowsToAdd(pix_col, pix_row):
    """Calculate number of blank rows to add to top and bottom of image."""
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

def __colsToAdd(pix_row, pix_col):
    """Calculate number of blank columns to add to left and right of image."""
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

def __addRows(add_top, add_btm, img):
    """Add calculated number of blank rows to top and bottom of image."""
    pix_col = np.shape(img)[1]
    
    top_shape = (add_top, pix_col)
    top = np.full(top_shape, 0)
    btm_shape = (add_btm, pix_col)
    btm = np.full(btm_shape, 0)
    
    return np.concatenate((top, img, btm))

def __addCols(add_lft, add_rgt, img):
    """Add calculated number of blank columns to left and right of image."""
    pix_row = np.shape(img)[0]
    
    lft_shape = (pix_row, add_lft)
    lft = np.full(lft_shape, 0)
    rgt_shape = (pix_row, add_rgt)
    rgt = np.full(rgt_shape, 0)
    
    return np.concatenate((lft, img, rgt), axis=1)

def __changeImgRatio(img):
    """
    Change ratio of image sides to ratio of pan dimensions.
    
    To refrain from stretching, adds blank columns or rows to top and
        bottom or left and right of image, keeping the image
        centered.

    Parameters
    ----------
    img : np.ndarray
        Array of pixels holding image to transform.
    
    Returns
    -------
    np.ndarray
        Array of pixels with correct overall dimensions and original
        image centered.
    """
    rows = np.shape(img)[0]
    cols = np.shape(img)[1]
    
    pan_ratio = 7.5 / 6
    img_ratio = rows / cols

    if img_ratio < pan_ratio:
        add_top, add_btm = __rowsToAdd(cols, rows)
        return __addRows(add_top, add_btm, img)
        
    elif img_ratio > pan_ratio:
        add_lft, add_rgt = __colsToAdd(rows, cols)
        return __addCols(add_lft, add_rgt, img)
    else:
        return img

def __getToDimensions(img):
    """Resizes image so 1 pixel translates to a 1 mm square."""
    in_to_mm = 25.4
    pan_wth = 6 * in_to_mm
    pan_hgt = 7.5 * in_to_mm
    pan_shape = int(pan_wth), int(pan_hgt)

    wth_ratio = pan_wth / img.shape[0]
    hgt_ratio = pan_hgt / img.shape[1]

    return cv2.resize(img, pan_shape, wth_ratio, hgt_ratio, cv2.INTER_AREA)

def __getImgCoords(contours):
    """
    Transfer contour coordinates to G-code [x, y, e] format.
    
    The first and last 5 coordinates of each contour line have an e
        value of 0, indicating no extrusion should occur. All other
        line coordinates have an e value of 1, representing extrusion.
    The last coordinate of the returned array returns the extruder to
        its original position.

    Parameters
    ----------
    contours : tuple
        Set of contour lines and their coordinates. Size is equal to
        the number of contour lines found.
    
    Returns
    -------
    np.ndarray
        All coordinates for all lines in G-code format, including
        return point at end.
    """
    coordinates = []
    
    for line in contours:
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

def __getImg():
    """Get coordinates of line contours from uploaded image."""
    grayscale_img = __imgFromAirtable()
    
    _, binary_img = cv2.threshold(grayscale_img, 128, 255, cv2.THRESH_BINARY)
    inv_img = cv2.bitwise_not(binary_img)
    
    resized_img = __changeImgRatio(inv_img).astype('uint8')
    cv2.imwrite("resized_image.jpeg", resized_img)

    dim_img = __getToDimensions(resized_img)
    cv2.imwrite("dim_image.jpeg", dim_img)

    ctrs = cv2.findContours(dim_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return (__getImgCoords(ctrs[0]), dim_img)

def __getPos(rows, cols, spacing):
    num_x_y = int(1 / spacing)
    x = np.linspace(0, cols, num_x_y)
    y = np.linspace(0, rows, num_x_y)
    Y,X = np.meshgrid(y,x)

    return np.column_stack([X.ravel(), Y.ravel()]).astype(int)

def __reverseBgdLines(positions, spc_inv):
    """Mirror order of coordinates for every other line."""
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

def __gcodeBgdCoords(coords, num_coords):
    """Apply G-code formatting to background coordinates."""
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

def __getBgdCoords(positions, spacing):
    """
    Get background coordinates from contours covering cake face.
    
    Parameters
    ----------
    positions : list
        List of all coordinates to cover full cake face.
    spacing : float
        Relative space between each coordinate.
    
    Returns
    -------
    np.ndarray
        All coordinates to cover cake in G-code format, including
        return point at end.
    """
    num_coords = int(len(positions) / 2)
    spc_inv = int(1/spacing)

    rev_coords = __reverseBgdLines(positions, spc_inv)
        
    return __gcodeBgdCoords(rev_coords, num_coords)

def __getBgd(img):
    """
    Get coordinates of background contours to cover full cake face.
    
    Parameters
    ----------
    img : np.ndarray
        Array for image obtained from __getImg method

    Returns
    -------
    np.ndarray
        All coordinates to cover cake in G-code format, including
        return point at end.
    """
    blank = np.zeros(img.shape, dtype='uint8')

    blank_rows = blank.shape[0]
    blank_cols = blank.shape[1]
    spacing_pt = .04
    positions = __getPos(blank_rows, blank_cols, spacing_pt)

    return __getBgdCoords(positions.tolist(), spacing_pt)

def run():
    img_coordinates, dim_img = __getImg()
    np.savetxt("img_coordinates.csv", img_coordinates, delimiter=',')

    bgd_coordinates = __getBgd(dim_img)
    np.savetxt("bgd_coordinates.csv", bgd_coordinates, delimiter=',')

if __name__ == '__main__':
    run()

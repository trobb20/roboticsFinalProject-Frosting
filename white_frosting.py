from pickle import FALSE, TRUE
import requests
import json
import urllib.request
import cv2
import numpy as np

# generate blank canvas based on resized image
image = cv2.imread("image.jpg") # replace image.jpg with resized image
print(image.shape)
blank = np.zeros(image.shape, dtype='uint8')
cv2.imwrite('blank.jpg', blank)

# create points
spacing_pt = .05

print(type(image.shape[0]))
num_x = int(image.shape[1]/(image.shape[1]*spacing_pt))
num_y = int(image.shape[0]/(image.shape[0]*spacing_pt))
x = np.linspace(0, image.shape[1], num_x)
y = np.linspace(0, image.shape[0], num_y)
Y,X = np.meshgrid(y,x)

positions = np.column_stack([X.ravel(), Y.ravel()]).astype(int)

print(sorted)


for (x,y) in (sorted):
    cv2.circle(blank, (x,y), 1, (0,0,255), -1)

cv2.imwrite('blankwithdots.jpg', blank)
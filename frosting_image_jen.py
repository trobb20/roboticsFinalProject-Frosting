import requests
import json
import urllib.request
import cv2
import numpy as np

## Airtable API ##
api_key = "keyxxxxxxxxxxxxxx" # enter API key here!
headers = {"Authorization": "Bearer " + api_key}

# contact Jennifer with your email so that she can add you as a collaborator on Airtable!
base_id = "appVtGBa7OdMUkrAI" # this is the base ID of Airtable database
table_name = "Image Submission Form"
url = "https://api.airtable.com/v0/" + base_id + "/Features?" + "sort%5B0%5D%5Bfield%5D=Created"

params = ()
response = requests.get(url, params=params, headers=headers)
airtable_response = response.json() 

# Let's make it human readable
with open ('output.txt', 'w') as f:
    f.write(json.dumps(airtable_response, indent = 2))

image_url = airtable_response["records"][len(airtable_response["records"])-1]["fields"]["Image"][0]["url"]
print(image_url)

## Get Contours / Coordinates ##

image_url = 'https://www.seekpng.com/png/detail/184-1840292_duck-clipart-yellow-duck.png'

urllib.request.urlretrieve(image_url, "ducks.jpg")

image = cv2.imread("ducks.jpg")
blank = np.zeros(image.shape, dtype='uint8')

def external_contours(image, bg):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,30,200)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(contours) # this retrieves raw coordinates
    fin = cv2.drawContours(blank, contours, -1, (0,255,0),3)
    cv2.imwrite('duck_extcontours.jpg', fin)

def all_contours(image, bg):
    gray= cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges= cv2.Canny(gray,30,200)
    contours, hierarchy= cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    print(contours) # this retrieves raw coordinates
    cnt = contours[-1]
    fin = cv2.drawContours(blank, [cnt], 0, (0,255,0), 3)
    cv2.imwrite('duck_allcontours.jpg', fin)

external_contours(image, blank)
all_contours(image, blank)
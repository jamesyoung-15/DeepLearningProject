from skimage.transform import resize

# screen capture
import mss
# frame processing
import cv2
from PIL import Image

# gym environment
import gymnasium as gym
from gymnasium import spaces

# ocr
import pytesseract

import numpy as np
import time

import matplotlib.pyplot as plt

def resize_img(img):
    """
    Image to pass in
    :param img: numpy array image
    :return: resized image
    """
    im = resize(img, (200, 66, 3))
    im_arr = im.reshape((200, 66, 3))
    return im_arr

gameScreen = {"top": 740, "left": 960, "width": 640, "height": 480}

image = np.array(mss.mss().grab(gameScreen))[:,:,:3]

im_arr = resize_img(image)

cv2.imshow('image', image)
cv2.waitKey()
cv2.imshow('image', im_arr)
cv2.waitKey()
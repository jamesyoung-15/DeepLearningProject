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

text = {"top": 880, "left": 1150, "width": 250, "height": 100} # Time text, when game is done it  will disappear


image = np.array(mss.mss().grab(text))[:,:,:3]


cv2.imshow('image', image)
cv2.waitKey()
ocr = pytesseract.image_to_string(image,config="--psm 6")

print(ocr)
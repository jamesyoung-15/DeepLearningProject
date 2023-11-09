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


class MarioKart64Env(gym.Env):
    # setup environment action, observation shapes, etc.
    def __init__(self):
        super().__init__()
        self.observation_space = spaces.Box(low=0,high=255, shape=(1,83,100),dtype=np.uint8)
        # actions: forward, left, right, reverse
        self.action_space = spaces.Discrete(4)
        # area to extract
        self.capture = mss()
        # for my 2k monitor, might want to find a way to have consistent screen
        self.game_screen = {"top": 720, "left": 960, "width": 640, "height": 480}

    # action to take in game
    def step(self, action):
        pass
    # visualize game
    def render(self):
        pass
    # restart game
    def reset(self):
        pass
    # get screen and process frame
    def getObservation(self):
        pass
    # race finished
    def finishGame(self):
        pass

env = MarioKart64Env()

print(env.action_space.sample())
# screen capture
import mss
# frame processing
import cv2
from PIL import Image

# gym environment
import gymnasium as gym
from gymnasium import spaces

# stable baseline3
from stable_baselines3.common.env_checker import check_env


# ocr
import pytesseract

# other utils
import numpy as np
import time
import matplotlib.pyplot as plt
import subprocess
import os

class MarioKart64Env(gym.Env):
    # setup environment action, observation shapes, etc.
    def __init__(self):
        super().__init__()
        self.observation_space = spaces.Box(low=0,high=255, shape=(480,640,3),dtype=np.uint8)
        # actions: forward, left, right
        self.action_space = spaces.Discrete(2)
        # area to extract
        self.capture = mss.mss()
        # for my 2k monitor, might want to find a way to have consistent screen
        self.gameScreen = {"top": 740, "left": 960, "width": 640, "height": 480}
        self.lapCounterLocation = {"top": 760, "left": 1150, "width": 25, "height": 60} # current lap
        # self.timeTextLocation = {"top": 760, "left": 1340, "width": 80, "height": 50} # Time text, when game is done it  will disappear
        self.finishText = {"top": 790, "left": 1330, "width": 250, "height": 50} # using Lap Time text as indicator for finished game
        self.reverseText = {"top": 880, "left": 1200, "width": 150, "height": 80} # reverse text
        self.currentLap = 1


    # action to take in game
    def step(self, action):
        action_map = {
            0: "Left",
            1: "Right",
            2: "Shift",
            3: "Reverse"
            
        }
        duration = 0.5
        if action!=3:
            # Simulate Shift key press
            subprocess.call(["xdotool", "keydown", action_map[action]])
            time.sleep(duration)
            # release
            subprocess.call(["xdotool", "keyup", action_map[action]])
        # reverse
        else:
            # Simulate Shift key press
            subprocess.call(["xdotool", "keydown", "Down"])
            subprocess.call(["xdotool", "keydown", "Control"])
            time.sleep(duration)
            # release
            subprocess.call(["xdotool", "keyup", "Down"])
            subprocess.call(["xdotool", "keyup", "Control"])

        
        # check if game is done
        finishGameImage, isFinishOcr, done = self.finishGame()
        # get new observation
        newObs = self.getObservation()

        reward = 0
        lapImage, lapOcr, detectLap = self.getLap()

        # print(detectLap)
        if detectLap>self.currentLap:
            reward+=100
            self.currentLap = detectLap
        
        revImage, revOcr, reverse = self.checkReverse()

        if reverse:
            reward-=100
            print("Going wrong way")


        # info dict
        info = {}

        # limit steps
        truncated = False
        return newObs, reward, done, truncated, info
        
    # visualize game
    def render(self):
        cv2.imshow('Game', np.array(self.capture.grab(self.gameScreen))[:,:,:3])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.close()
    # restart game
    def reset(self, seed=None):
        time.sleep(1)
        # Get the screen resolution
        screen_info = self.getScreenRes()
        screen_width = int(screen_info['width'])
        screen_height = int(screen_info['height'])
        
        # Calculate the center coordinates
        center_x = int(screen_width / 2)
        center_y = int(screen_height / 2) + 20

        # Move the mouse cursor to the center of the screen
        subprocess.call(["xdotool", "mousemove", str(center_x), str(center_y)])

        time.sleep(0.1)
        # Simulate a mouse click
        subprocess.call(["xdotool", "click", "1"])
        time.sleep(0.1)
        # Simulate F7 key press
        subprocess.call(["xdotool", "keydown", "F7"])

        # Simulate F7 key release
        subprocess.call(["xdotool", "keyup", "F7"])
        time.sleep(0.5)
        info = {}
        return self.getObservation(), info

    # get monitor resolution with xrandr (linux)    
    def getScreenRes(self):
        output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
        resolution = output.split()[0].split(b'x')
        return {'width': resolution[0].decode("utf-8"), 'height': resolution[1].decode("utf-8")}

    # get screen and process frame
    def getObservation(self):
        # capture screen
        screenshot = np.array(self.capture.grab(self.gameScreen))
        # RGBA -> RGB
        imageArray = np.flip(screenshot[:, :, :3], 2)
        return imageArray
    
    # check if going wrong way by checking if reverse string shows up
    def checkReverse(self):
        image = np.array(self.capture.grab(self.reverseText), dtype=np.uint8)
        ocr = pytesseract.image_to_string(image,config="--psm 6")
        reverse = False
        if 'rev' in ocr or 'REV' in ocr:
            reverse = True
        return image, ocr, reverse
    # get current lap from text with ocr
    def getLap(self):
        image = np.array(self.capture.grab(self.lapCounterLocation), dtype=np.uint8)
        ocr = pytesseract.image_to_string(image,config='--psm 10')
        lapDetected = 1
        if '1' in ocr or 'i' in ocr:
            lapDetected = 1
        elif '2' in ocr:
            lapDetected = 2
        elif '3' in ocr or 'E' in ocr:
            lapDetected = 3
        else:
            lapDetected = -1
        return image, ocr, lapDetected

    # race finished
    def finishGame(self):
        image = np.array(self.capture.grab(self.finishText), dtype=np.uint8)
        # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # cv2.imshow('thresh', image)
        # cv2.waitKey()
        ocr = pytesseract.image_to_string(image,config="--psm 6")
        
        # ocr should read lap time if game done
        completedStrings = ['LAP TIME', ' LAP TIME']
        finished = False
        if 'LAP' in ocr:
            finished = True
        return image, ocr, finished

    # close rendered screens
    def close(self):
        cv2.destroyAllWindows()



env = MarioKart64Env()



# for episode in range(10):
#     obs = env.reset()
#     subprocess.call(["xdotool", "keydown", "Shift"])
#     done = False
#     totalReward = 0
#     while not done:
#         obs, reward, done, info = env.step(env.actionSpace.sample())
#         totalReward += reward
#     print(f'Total reward for episode {episode} is {totalReward}')
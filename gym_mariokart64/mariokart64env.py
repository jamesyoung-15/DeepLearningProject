# screen capture
import mss
# frame processing
import cv2
from skimage.transform import resize
# from PIL import Image

# gym environment
import gymnasium as gym
from gymnasium import spaces

# stable baseline3
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3 import DQN
from stable_baselines3.common.results_plotter import load_results, ts2xy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.env_util import make_vec_env

# ocr
# import pytesseract

# other utils
import numpy as np
import time
import matplotlib.pyplot as plt
import subprocess
import os
import threading
from collections import deque


# own libraries
import gym_mariokart64.m64py.m64 as m64

class MarioKart64Env(gym.Env):
    # setup environment action, observation shapes, etc.
    def __init__(self):
        """ Constructor """
        super().__init__()
        # observation space size of 640x480x3 (rbg) screen
        self.observation_space = spaces.Box(low=0,high=255, shape=(66,200,3),dtype=np.uint8)
        # actions: forward-left, forward-right, forward
        self.action_space = spaces.Discrete(3)
        
        # area to extract
        self.capture = mss.mss()
        # default to 2k, use set_game_screen function to change
        self.game_screen = {"top": 740, "left": 960, "width": 640, "height": 480}

        # ocr stuff
        # self.lap_counter_location = {"top": 760, "left": 1150, "width": 25, "height": 60} # current lap
        # self.time_text_location = {"top": 760, "left": 1340, "width": 80, "height": 50} # Time text, when game is done it  will disappear
        # self.finish_text = {"top": 790, "left": 1330, "width": 250, "height": 50} # using Lap Time text as indicator for finished game
        # self.reverse_text = {"top": 880, "left": 1200, "width": 150, "height": 80} # reverse text
        
        # virtual memory meaning from memory map
        self.progress_address = 0x801644D0
        self.speed_address = 0x800F6BBC
        # self.x_pos_address = 0x800F69A4
        # self.y_pos_address = 0x800F69AC
        # self.z_pos_address = 0x800F69A8
        self.lap_address = 0x80164390

        # game info
        self.current_lap = 0
        self.progress = 0 # progress value at start of race
        self.speed = 0
        self.speed_threshold = 1070000000 # speed when bumping into wall
        self.speed_low_threshold = 1060000000
        self.speed_high_threshold = 1080000000
        self.good_progress_threshold = 440000
        self.highest_lap = 0 # prevent from going forward and backward to count as lap
        self.highest_progress = 0
        self.speed_queue_size = 8
        self.progress_queue_size = 10
        self.speed_queue = deque(maxlen= self.speed_queue_size) # holds n frames speed
        self.progress_queue = deque(maxlen = self.progress_queue_size) # holds last 15 progress value
        # populate queue
        for i in range(self.speed_queue_size):
            self.speed_queue.append(1165844420)
        for i in range(self.progress_queue_size):
            self.progress_queue.append(1100000000)

        # emulator init
        self.game = m64.M64Py()
        self.rom_path = None
        self.plugin_path = None
        self.core_path = None

    def set_game_screen(self, useDefault=True, left=None, top=None):
        """ Set the game screen to capture the emulator. Assumes emulator is running 640x480 at centre of screen. """
        if useDefault:
            return
        if left and top:
            self.game_screen = {"top": top, "left": left, "width": 640, "height": 480}
        else:
            screen_info = self.get_screen_res()
            screen_width = int(screen_info['width'])
            screen_height = int(screen_info['height'])
            left = int(screen_width / 2) - 320
            top = int(screen_height / 2) - 240 + 20
            self.game_screen = {"top": top, "left": left, "width": 640, "height": 480}
        print (self.game_screen)

    def set_paths(self, core_path, plugin_path, rom_path):
        """ Set core, plugin, and rom file paths. Can be relative (ie. ./directory/) or absolute (ie. /home/jamesyoung/m64p) """
        self.core_path = core_path
        self.rom_path = rom_path
        self.plugin_path = plugin_path

    def start_game(self):
        """ Run the emulator """
        if self.core_path and self.rom_path and self.plugin_path:
            self.game.run_emulator(self.core_path, self.plugin_path, self.rom_path)

        else:
            raise Exception("Please specify core, plugin, rom paths with set_paths function")

    # action to take in game
    def step(self, action):
        """ Gym step """
        action_map = {
            0: "Left",
            1: "Right",
            2: "Shift",
            # 3: "Reverse"
            
        }
        # print(action_map[action])
        duration = 0.4
        if action==0 or action==1:
            # Simulate Shift key press
            subprocess.call(["xdotool", "keydown", "Shift"])
            subprocess.call(["xdotool", "keydown", action_map[action]])
            time.sleep(duration)
            # release
            subprocess.call(["xdotool", "keyup", action_map[action]])
            subprocess.call(["xdotool", "keyup", "Shift"])
        else:
            subprocess.call(["xdotool", "keydown", action_map[action]])
            time.sleep(duration+0.1)
            subprocess.call(["xdotool", "keyup", action_map[action]])


        # get new observation
        new_obs = self.get_observation()

        # reward function
        reward = 0

        # get updated game info: done checks if game is finished (ie. lap>3), new_lap stores latest lap, new_progress checks latest progress, new_speed for latest speed
        done = self.finish_game()
        new_lap = self.get_lap()
        new_progress = self.get_progress()
        self.speed = self.get_speed()
        progress_diff = new_progress - self.progress
        # compare updated game info to previous values
        if not done:
            # big reward for new lap
            if new_lap>self.highest_lap and new_lap!=1:
                reward+=200
            # reward for making new progress and going fast
            if new_progress>self.highest_progress and self.speed>self.speed_high_threshold:
                factor = min(int(5*(progress_diff/self.good_progress_threshold)),20)
                # print("good: " + str(factor))
                reward+=factor
            # reward for making progress and moderate speed
            elif new_progress>self.highest_progress and self.speed>self.speed_threshold:
                factor = min(int((progress_diff/self.good_progress_threshold)),5)
                # print("meh: " + str(factor))
                reward += factor
            # punish for going wrong direction
            elif new_progress<self.progress:
                reward-=10
            # small reward kart for going fast
            if self.speed>self.speed_high_threshold:
                reward+=1
            # punish for going slow
            elif self.speed<self.speed_low_threshold:
                reward-=1
        # reward kart for finishing
        else:
            reward+=100000

        # stop early if going backward too much
        if new_lap<self.current_lap:
            reward-=500
            print("Stopped! Wrong way!")
            done = True
        
        # stop early if for the last few frames speed has been too slow
        self.progress_queue.append(new_progress)
        self.speed_queue.append(self.speed)
        if sum(self.speed_queue)/len(self.speed_queue) < self.speed_low_threshold:
            reward-=200
            print("Stopped! Too slow!")
            done = True
        if max(self.progress_queue) < self.highest_progress:
            reward-=200
            print("Stopped! Not enough progress!")
            done = True

        # update previous value to updated values
        self.current_lap = new_lap
        self.progress = new_progress
        if self.current_lap>self.highest_lap:
            self.highest_lap = self.current_lap
        if self.progress>self.highest_progress:
            self.highest_progress = self.progress
        
        # info dict
        info = {}
        # limit steps
        truncated = False
        return new_obs, reward, done, truncated, info
        
    # visualize game
    def render(self):
        """ Visualize game, not necessary """
        cv2.imshow('Game', np.array(self.capture.grab(self.game_screen))[:,:,:3])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.close()

    # restart game
    def reset(self, seed=None):
        """ Restart the game """
        time.sleep(1)
        self.reset_variables()
        # Get the screen resolution
        screen_info = self.get_screen_res()
        screen_width = int(screen_info['width'])
        screen_height = int(screen_info['height'])
        
        # Calculate the center coordinates
        center_x = int(screen_width / 2)
        center_y = int(screen_height / 2) + 25

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
        time.sleep(0.2)
        # let kart move forward to start at lap 1
        subprocess.call(["xdotool", "keydown", "Shift"])
        time.sleep(1.5)
        subprocess.call(["xdotool", "keyup", "Shift"])
        info = {}
        return self.get_observation(), info

    def reset_variables(self):
        # game info
        self.current_lap = 0
        self.progress = 0 # progress value at start of race
        self.speed = 0
        self.highest_lap = 0 # prevent from going forward and backward to count as lap
        self.highest_progress = 0
    
        # populate queue
        for i in range(self.speed_queue_size):
            self.speed_queue.append(1165844420)
        for i in range(self.progress_queue_size):
            self.progress_queue.append(1100000000)

    # get monitor resolution with xrandr (linux)    
    def get_screen_res(self):
        """ Use xrandr (Linux) to get the screen resolution, returns dictionary (eg. {'width': 1920, 'height': 1080}) """
        output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
        resolution = output.split()[0].split(b'x')
        return {'width': resolution[0].decode("utf-8"), 'height': resolution[1].decode("utf-8")}

    # get screen and process frame
    def get_observation(self):
        """ Grab screen with mss, return np image array """
        # capture screen
        image_array = np.array(self.capture.grab(self.game_screen))[:,:,:3]
        # resize image
        im = resize(image_array, (66, 200, 3))
        image_array = im.reshape((66, 200, 3))
        return image_array

    def get_lap(self):
        """ Read the lap memory info to get lap, returns lap number """
        if self.game.game_started:
            #  lap starts at -1 so we add one
            return self.game.read_memory(self.lap_address)+1
    
    def get_progress(self):
        """ Get progress of kart in race """
        if self.game.game_started:
            return self.game.read_memory(self.progress_address)

    def get_speed(self):
        """ Get speed of car"""
        if self.game.game_started:
            return self.game.read_memory(self.speed_address)

    # check if race is finished
    def finish_game(self):
        """ Check if race is finished, return bool """
        if self.current_lap > 3:
            print("Race Completed!!")
            return True
        return False

    # close rendered screens
    def close(self):
        """ Close cv2 windows if needed """
        cv2.destroyAllWindows()


class TrainLoggingCallback(BaseCallback):
    def __init__(self, check_freq, save_path, verbose=1):
        super(TrainLoggingCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.save_path = save_path
    
    def __init__callback(self):
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)
        
    def _on_step(self):
        if self.n_calls % self.check_freq == 0:
            model_path = os.path.join(self.save_path, 'best_model_{}'.format(self.n_calls))
            self.model.save(model_path)
        return True

class SaveOnBestTrainingRewardCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).

    :param check_freq: (int)
    :param log_dir: (str) Path to the folder where the model will be saved.
      It must contains the file created by the ``Monitor`` wrapper.
    :param verbose: (int)
    """
    def __init__(self, check_freq: int, log_dir: str, verbose=1):
        super(SaveOnBestTrainingRewardCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, 'best_model')
        self.best_mean_reward = -np.inf

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:

          # Retrieve training reward
          x, y = ts2xy(load_results(self.log_dir), 'timesteps')
          if len(x) > 0:
              # Mean training reward over the last 100 episodes
              mean_reward = np.mean(y[-100:])
              if self.verbose > 0:
                print("Num timesteps: {}".format(self.num_timesteps))
                print("Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(self.best_mean_reward, mean_reward))

              # New best model, you could save the agent here
              if mean_reward > self.best_mean_reward:
                  self.best_mean_reward = mean_reward
                  # Example for saving best model
                  if self.verbose > 0:
                    print("Saving new best model to {}".format(self.save_path))
                  self.model.save(self.save_path)

        return True



""" Below are examples using ocr """
# # check if going wrong way by checking if reverse string shows up
# def checkReverse(self):
#     image = np.array(self.capture.grab(self.reverseText), dtype=np.uint8)
#     ocr = pytesseract.image_to_string(image,config="--psm 6")
#     reverse = False
#     if 'rev' in ocr or 'REV' in ocr:
#         reverse = True
#     return image, ocr, reverse
# # get current lap from text with ocr
# def getLap(self):
#     image = np.array(self.capture.grab(self.lapCounterLocation), dtype=np.uint8)
#     ocr = pytesseract.image_to_string(image,config='--psm 10')
#     lapDetected = 1
#     if '1' in ocr or 'i' in ocr:
#         lapDetected = 1
#     elif '2' in ocr:
#         lapDetected = 2
#     elif '3' in ocr or 'E' in ocr:
#         lapDetected = 3
#     else:
#         lapDetected = -1
#     return image, ocr, lapDetected

# # race finished
# def finishGame(self):
#     image = np.array(self.capture.grab(self.finishText), dtype=np.uint8)
#     # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#     # cv2.imshow('thresh', image)
#     # cv2.waitKey()
#     ocr = pytesseract.image_to_string(image,config="--psm 6")
    
#     # ocr should read lap time if game done
#     completedStrings = ['LAP TIME', ' LAP TIME']
#     finished = False
#     if 'LAP' in ocr:
#         finished = True
#     return image, ocr, finished
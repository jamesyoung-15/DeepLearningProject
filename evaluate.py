import threading
import time
import subprocess
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3 import DQN
import os
import cv2
# import pdb; pdb.set_trace()

# my libraries
import gym_mariokart64.mariokart64env as mk64gym
from torch_network.wrappers import SkipFrame 

# paths
lib_path = "./gym_mariokart64/m64py/libmupen64plus.so.2"
plugin_path = "./gym_mariokart64/m64py/"
rom_path = "./rom/mariokart64.n64"
tensorboard_dir = 'logs/'
log_dir = 'tmp/'


env = mk64gym.MarioKart64Env()
env.set_game_screen(useDefault=True)
env.set_paths(lib_path, plugin_path, rom_path)

# create thread for concurrency
thread = threading.Thread(target=env.start_game)
thread.start()
# sleep to prevent reading memory before emulator starts
time.sleep(9)


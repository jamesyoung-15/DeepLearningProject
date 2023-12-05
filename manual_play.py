import numpy as np
import gymnasium as gym
from stable_baselines3.common.evaluation import evaluate_policy

from imitation.algorithms import bc
from imitation.data import rollout
from imitation.data.wrappers import RolloutInfoWrapper
from imitation.policies.serialize import load_policy
from imitation.util.util import make_vec_env
from manual_input.agent import HumanAgent
from manual_input.keyboard import KeyboardController
from gymnasium.utils.play import PlayPlot, play

import gym_mariokart64.mariokart64env as mk64gym
import subprocess
import threading
import time

# paths
lib_path = "./gym_mariokart64/m64py/libmupen64plus.so.2"
plugin_path = "./gym_mariokart64/m64py/"
rom_path = "./rom/mariokart64.n64"
tensorboard_dir = 'logs/'
log_dir = 'tmp/'


player = HumanAgent()


env = mk64gym.MarioKart64Env(render_mode="rgb_array")
env.set_game_screen(useDefault=True)
env.set_paths(lib_path, plugin_path, rom_path)
# env = SkipFrame(env, skip=3)
# env = FrameStack(env, num_stack=3)

# create thread for concurrency
thread = threading.Thread(target=env.start_game)
thread.start()
# sleep to prevent reading memory before emulator starts
time.sleep(9)

# test env
for episode in range(5):
    obs = env.reset()
    done = False
    totalReward = 0
    while not done:
        obs, reward, done, truncated, info = env.step(player.train())
        print("Reward: " + str(reward))
        totalReward += reward
    print(f'Total reward for episode {episode} is {totalReward}')



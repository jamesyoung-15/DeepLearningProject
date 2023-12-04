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


def main(existing_model=None):
    # paths
    lib_path = "./gym_mariokart64/m64py/libmupen64plus.so.2"
    plugin_path = "./gym_mariokart64/m64py/"
    rom_path = "./rom/mariokart64.n64"
    tensorboard_dir = 'logs/'
    log_dir = 'tmp/'


    env = mk64gym.MarioKart64Env()
    env.set_game_screen(useDefault=False,top=350,left=640)
    env.set_paths(lib_path, plugin_path, rom_path)
    # create thread for concurrency
    thread = threading.Thread(target=env.start_game)
    thread.start()
    # sleep to prevent reading memory before emulator starts
    time.sleep(9)

    
    # check observation
    # env.reset()
    # # image = env.get_observation()
    # image = env.get_observation_full()
    # cv2.imshow('image', image)
    # cv2.waitKey()
    # time.sleep(5)

    # test env
    # for episode in range(2):
    #     obs = env.reset()
    #     subprocess.call(["xdotool", "keydown", "Shift"])
    #     done = False
    #     totalReward = 0
    #     while not done:
    #         obs, reward, done, truncated, info = env.step(env.action_space.sample())
    #         print("Reward: " + str(reward))
    #         totalReward += reward
    #     print(f'Total reward for episode {episode} is {totalReward}')

    # make directories
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(tensorboard_dir, exist_ok=True)
    env = Monitor(env, log_dir)
    callback = mk64gym.SaveOnBestTrainingRewardCallback(check_freq=1000, log_dir=log_dir)

    # create dqn model
    if existing_model:
        print("Using existing model")
        model = DQN.load(existing_model,env, tensorboard_log=tensorboard_dir)
    else:
        model = DQN('CnnPolicy', 
                env, 
                # learning_rate=1e-4,
                # batch_size= 192, # https://arxiv.org/pdf/1803.02811.pdf
                tensorboard_log=tensorboard_dir, 
                verbose=1, 
                buffer_size=100000, 
                learning_starts=2000)

    # train model
    model.learn(total_timesteps=100000, callback=callback)

if __name__ == '__main__':
    main()
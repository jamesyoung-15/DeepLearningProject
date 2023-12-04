import threading
import time
# import pdb; pdb.set_trace()
# my libraries
import gym_mariokart64.mariokart64env as mk64gym
import subprocess
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3 import DQN

def main(existing_model=None):
    # paths
    lib_path = "./gym_mariokart64/m64py/libmupen64plus.so.2"
    plugin_path = "./gym_mariokart64/m64py/"
    rom_path = "./rom/mariokart64.n64"
    CHECKPOINT_DIR = './train/'
    LOG_DIR = './logs/'


    env = mk64gym.MarioKart64Env()
    env.set_paths(lib_path, plugin_path, rom_path)
    # create thread for concurrency
    thread = threading.Thread(target=env.start_game)
    thread.start()
    # sleep to prevent reading memory before emulator starts
    time.sleep(9)
    # obs = env.reset()

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


    callback = mk64gym.TrainLoggingCallback(check_freq=10000, save_path=CHECKPOINT_DIR)

    # create dqn model
    if existing_model:
        print("Using existing model")
        model = DQN.load(existing_model,env, tensorboard_log=LOG_DIR)
    else:
        model = DQN('CnnPolicy', 
                env, 
                learning_rate=1e-4,
                # batch_size= 192, # https://arxiv.org/pdf/1803.02811.pdf
                tensorboard_log=LOG_DIR, 
                verbose=1, 
                buffer_size=100000, 
                learning_starts=5000)

    # train
    model.learn(total_timesteps=100000, callback=callback)

if __name__ == '__main__':
    main()
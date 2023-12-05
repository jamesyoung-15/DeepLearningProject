import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

import random, datetime
from pathlib import Path
import threading
import time

import gymnasium as gym
from gymnasium.wrappers import FrameStack, GrayScaleObservation, TransformObservation

from torch_network.metrics import MetricLogger
from torch_network.agent import MarioKartAgent
from torch_network.wrappers import ResizeObservation, SkipFrame

import gym_mariokart64.mariokart64env as mk64gym

# Initialize Super Mario environment
env = mk64gym.MarioKart64Env()

# paths
lib_path = "./gym_mariokart64/m64py/libmupen64plus.so.2"
plugin_path = "./gym_mariokart64/m64py/"
rom_path = "./rom/mariokart64.n64"
tensorboard_dir = 'logs/'
log_dir = 'tmp/'

# Apply Wrappers to environment
env = SkipFrame(env, skip=4)
env = GrayScaleObservation(env, keep_dim=False)
env = ResizeObservation(env, shape=84)
env = TransformObservation(env, f=lambda x: x / 255.)
env = FrameStack(env, num_stack=4)

env.set_game_screen(useDefault=True)
env.set_paths(lib_path, plugin_path, rom_path)


# create thread for concurrency
thread = threading.Thread(target=env.start_game)
thread.start()
# sleep to prevent reading memory before emulator starts
time.sleep(9)


env.reset()

save_dir = Path('checkpoints') / datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
save_dir.mkdir(parents=True)

checkpoint = None # Path('checkpoints/2020-10-21T18-25-27/mario.chkpt')
kart_agent = MarioKartAgent(state_dim=(4, 84, 84), action_dim=env.action_space.n, save_dir=save_dir, checkpoint=checkpoint)

logger = MetricLogger(save_dir)

episodes = 60000

### for Loop that train the model num_episodes times by playing the game
for e in range(episodes):

    state, _ = env.reset()

    # Play the game!
    while True:

        # 3. Show environment (the visual) [WIP]
        # env.render()

        # 4. Run agent on the state
        action = kart_agent.act(state)

        # 5. Agent performs action
        next_state, reward, done, truncated, info = env.step(action)

        # 6. Remember
        kart_agent.cache(state, next_state, action, reward, done)

        # 7. Learn
        q, loss = kart_agent.learn()

        # 8. Logging
        logger.log_step(reward, loss, q)

        # 9. Update state
        state = next_state

        # 10. Check if end of game
        if done:
            break

    logger.log_episode()

    if e % 10 == 0:
        logger.record(
            episode=e,
            epsilon=kart_agent.exploration_rate,
            step=kart_agent.curr_step
        )
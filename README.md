# DeepRL MarioKart64
My project that uses Deep Reinforced Learning to play MarioKart64. Specfically, the project uses Deep Q-Learning as described by [this paper](https://arxiv.org/abs/1312.5602). The project uses debugger build of [Mupen64Plus emulator](https://mupen64plus.org/docs/) and wraps it with Farama's [Gymnasium](https://gymnasium.farama.org/) library to simplify training.

## Instructions

### Setup
See [this page](./setup.md) for full instructions to setup.

### Usage

## More About the Project

### Gym Environment
There is an existing Gym Environments for Mupen64Plus: [gym-mupen64plus](https://github.com/bzier/gym-mupen64plus). However I decided create my own environment wrapper to be able read game memory.

### Emulator
For emulating N64 I used Mupen64Plus (M64P) with Glide64mk plugin. To enable debugging to access the memeory maps, build the M64P from source with debugging flag. I used Glide64mk instead of Rice video plugin as Rice video plugin stuttered on my system.

#### Used Keyboard commands
Default: [Documentation](https://mupen64plus.org/wiki/index.php/KeyboardSetup)

##### Mupen64Plus Menu Commands

|Key|Description|
|--- |--- |
|Escape|Quit the emulator|
|0-9|Select virtual 'slot' for save/load state (F5 and F7) commands|
|F5|Save emulator state|
|F7|Load emulator state|
|F9|Reset emulator|
|F10|slow down emulator by 5%|
|F11|speed up emulator by 5%|
|F12|take screenshot|
|Alt-Enter|Toggle between windowed and fullscreen|
|p or P|Pause on/off|
|m or M|Mute/unmute sound|
|g or G|Press "Game Shark" button (only if cheats are enabled)|
|/ or ?|single frame advance while paused|
|F|Fast Forward (playback at 250% normal speed while F key is pressed)|
|[|Decrease volume|
|]|Increase volume|

#### Controller to Keyboard Mapping:

|N64 Controller Action|Keys|
|--- |--- |
|Analog Pad|Arrow Keys (left, right, down, up)|
|C Up/Left/Down/Right|"I", "J", "K", "L"|
|DPad Up/Left/Down/Right|"W", "A", "S", "D"|
|Z trigger|"z"|
|Left trigger|"x"|
|Right trigger|"c"|
|Start|"Enter" ("Return")|
|A button|"left shift"|
|B button|"left control"|
|Select Mempack|","|
|Select Rumblepack|"."|



#### Memory Map
Todo: use memory to get player info for more info (eg. use current progress, speed, etc.).

|Address|Info|
|--- |--- |
|0x1644D0 | Current progress |
|0x0F6BBC | Velocity |
|0x0F69A4 | X Position |
|0x0F69AC | Y Position |
|0xF69A8 | Z Position |

Resources: 
- https://hack64.net/wiki/doku.php?id=mario_kart_64:memory_map
- https://github.com/weatherton/BizHawkMarioKart64/blob/master/MarioKart64_AutoTransmission.lua
- https://tasvideos.org/GameResources/N64/MarioKart64
- https://wulfebw.github.io/post/ssb64-rl-01/

#### Reading from Mupen64Plus memory
Use Mupen64Plus C++ API. To store into Python variable, will use Python ctype.

### Resources
https://www.grumpyoldnerd.com/post/reinforcement-learning-part-5-super-mario-kart
http://cs231n.stanford.edu/reports/2017/pdfs/624.pdf
https://cs229.stanford.edu/proj2012/LiaoYiYang-RLtoPlayMario.pdf
https://www.andrew-shen.net/ssb64.pdf
https://arxiv.org/pdf/1312.5602.pdf
https://devpost.com/software/deepkart64#updates
https://drive.google.com/file/d/1iFMzAvM9RlOaZzcsg4HZTQZCcz-dXtqA/view
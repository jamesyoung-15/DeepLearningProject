# DeepRL MarioKart64
Ongoing course project that tries to use deep reinforced learning to play MarioKart64.

## Setup
Recommend use Python virtual environment. Install requirements from `requirements.txt` with Pip. Project setup for Linux (Arch btw).

### Creating and Activating Environment
[Venv Documentation](https://docs.python.org/3/library/venv.html)

Creating venv:
``` bash
python -m venv /path/to/new/virtual/environment
```

Activating venv:
``` bash
source <venv>/bin/activate
```

Installing requirements
```bash
pip install -r requirements.txt
```

## Emulator
Using Mupen64Plus with Glide64mk plugin. On Arch installed [this](https://aur.archlinux.org/packages/mupen64plus-video-parallel-git) package from AUR. Either use parallel video plugin or Glide64mk instead of Rice video plugin as Rice video plugin stuttered on my system.

### Used Keyboard commands
Default: [Documentation](https://mupen64plus.org/wiki/index.php/KeyboardSetup)

#### Mupen64Plus Menu Commands

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


## Gym Environment
There are existing Gym Environments for Mupen64Plus: [gym-mupen64plus](https://github.com/bzier/gym-mupen64plus) . However I decided create my own environment wrapper to read game memory.





## Memory Map
Todo: use memory to get player info for more info (eg. use current progress, speed, etc.).

|Address|Info|
|--- |--- |
|0x1644D0: | Current progress |
|0x0F6BBC: | Velocity |
|0x0F69A4: | X Position |
|0x0F69AC: | Y Position |
|0xF69A8: | Z Position |

Resources: 
- https://hack64.net/wiki/doku.php?id=mario_kart_64:memory_map
- https://github.com/weatherton/BizHawkMarioKart64/blob/master/MarioKart64_AutoTransmission.lua
- https://tasvideos.org/GameResources/N64/MarioKart64
- https://wulfebw.github.io/post/ssb64-rl-01/

## Reading from Mupen64Plus memory
Use Mupen64Plus C++ API. To store into Python variable, will use Python ctype.

## Resources
https://www.grumpyoldnerd.com/post/reinforcement-learning-part-5-super-mario-kart
http://cs231n.stanford.edu/reports/2017/pdfs/624.pdf
https://cs229.stanford.edu/proj2012/LiaoYiYang-RLtoPlayMario.pdf
https://www.andrew-shen.net/ssb64.pdf
https://arxiv.org/pdf/1312.5602.pdf
https://devpost.com/software/deepkart64#updates
https://drive.google.com/file/d/1iFMzAvM9RlOaZzcsg4HZTQZCcz-dXtqA/view
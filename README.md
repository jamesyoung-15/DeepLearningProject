# DeepRL MarioKart64
Project that uses deep reinforced learning to play MarioKart64. Ongoing course project. Uses Farama's Gymnasium (fork of OpenAI's Gym library) environment.

<!-- ## Setup
Recommend use Python virtual environment. Install requirements from `requirements.txt` with Pip.  -->

## Gym Environments
For existing solution, currently using [gym-mupen64plus](https://github.com/bzier/gym-mupen64plus) for quick testing. However will later create own environment wrapper.

## Memory Map
Potential todo, use memory to get player info for more info (eg. use current progress, speed, etc.).

0x1644D0: Current progress
0x0F6BBC: Velocity
0x0F69A4: X Position
0x0F69AC: Y Position
0xF69A8: Z Position

Resources: 
- https://hack64.net/wiki/doku.php?id=mario_kart_64:memory_map
- https://github.com/weatherton/BizHawkMarioKart64/blob/master/MarioKart64_AutoTransmission.lua
- https://tasvideos.org/GameResources/N64/MarioKart64
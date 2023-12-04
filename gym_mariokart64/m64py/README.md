# Mupen64Plus Python
Python script to run Mupen64plus with memory read option. Based off of [Mupen64Plus-UI-Python](https://github.com/mupen64plus/mupen64plus-ui-python/tree/master)

## Custom Run with Python
### General Flow

1. Load core library (libmupen64plus.so) and set function pointers
2. Call CoreGetVersion, check core version and capabilities
3. Call CoreStartup to initialize the core library
4. Load front-end configuration from core config API or through own mechanism
5. Find plugins, open dynamic libraries, call PluginStartup for each
6. Enter message loop for user interaction
7. If user selects ROM and presses Play:
   - Load and de-compress the ROM
   - Use CoreDoCommand to open the ROM
   - Call CoreAttachPlugin to attach selected plugins to core
   - Use CoreDoCommand to start emulation
   - When emulation is finished, call CoreDetachPlugin on all plugins, then close the ROM
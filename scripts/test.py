import ctypes
import subprocess
import time
import os
import sys


# Load the Mupen64Plus API library
libm64p = ctypes.CDLL("libmupen64plus.so.2")

# Initialize Mupen64Plus
libm64p.m64p_init()

# Load the ROM file
rom_path = "<path_to_your_rom_file>"
libm64p.m64p_plugin_startup(rom_path.encode())

# Specify the memory address to monitor
memory_address = 0x80000000

# Continuously monitor the memory address
while True:
    # Read the value at the memory address
    value = ctypes.c_uint32()
    libm64p.m64p_dbg_read_mempak(rom_path.encode(), memory_address, ctypes.byref(value))

    print(f"Memory Address 0x{memory_address:X}: {value.value}")

    # Delay between memory reads (adjust as needed)
    time.sleep(1)

# Cleanup and exit
libm64p.m64p_core_cleanup()
libm64p.m64p_exit()
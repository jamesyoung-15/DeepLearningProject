import ctypes
import subprocess
import time
import os
import sys

""" Global Variables """
# File locations
MUPEN_PATH = "./test/mupen64plus"
DYNLIB_PATH = "./test/libmupen64plus.so.2"
CONFIG_PATH = "~/.config/mupen64plus/"
ROM_PATH = "../rom/mariokart64.n64"

# Mupen64plus info, taken from header files
CORE_API_VERSION = 0x020001
CONSOLE_UI_VERSION = 0x020509
CORE_API_VERSION  = 0x020001
CONFIG_API_VERSION = 0x020301
# M64 Type
M64ERR_SUCCESS = 0
M64MSG_ERROR = 1
M64MSG_WARNING = 2
M64MSG_INFO = 3
M64MSG_STATUS = 4
M64MSG_VERBOSE = 5

# commands
M64CMD_ROM_OPEN = 1
M64CMD_ROM_CLOSE = 2
M64CMD_ROM_GET_HEADER = 3
M64CMD_ROM_GET_SETTINGS = 4
M64CMD_EXECUTE = 5
# plugins
M64PLUGIN_NULL = 0
M64PLUGIN_RSP = 1
M64PLUGIN_GFX = 2
M64PLUGIN_AUDIO = 3
M64PLUGIN_INPUT = 4
M64PLUGIN_CORE = 5
PLUGIN_ORDER = [
    M64PLUGIN_GFX,
    M64PLUGIN_AUDIO,
    M64PLUGIN_INPUT,
    M64PLUGIN_RSP
]
PLUGIN_DEFAULT = {
    M64PLUGIN_RSP: "mupen64plus-rsp-hle.so",
    M64PLUGIN_GFX: "mupen64plus-video-glide64mk2.so",
    # M64PLUGIN_GFX: "mupen64plus-video-rice.so", # default video plugin
    M64PLUGIN_AUDIO: "mupen64plus-audio-sdl.so",
    M64PLUGIN_INPUT: "mupen64plus-input-sdl.so"
}
PLUGIN_NAME = {
    M64PLUGIN_NULL: b"NULL",
    M64PLUGIN_RSP: b"RSP",
    M64PLUGIN_GFX: b"Video",
    M64PLUGIN_AUDIO: b"Audio",
    M64PLUGIN_INPUT: b"Input"
}
PLUGIN_MAP = {
        M64PLUGIN_RSP: {},
        M64PLUGIN_GFX: {},
        M64PLUGIN_AUDIO: {},
        M64PLUGIN_INPUT: {}
}

def debug_callback(context, level, message):
    if level <= M64MSG_ERROR:
        sys.stderr.write("%s: %s\n" % (context.decode(), message.decode()))
    elif level == M64MSG_WARNING:
        sys.stderr.write("%s: %s\n" % (context.decode(), message.decode()))
    elif level == M64MSG_INFO or level == M64MSG_STATUS:
        sys.stderr.write("%s: %s\n" % (context.decode(), message.decode()))

def state_callback(context, param, value):
    if param == M64CORE_VIDEO_SIZE:
        pass
    elif param == M64CORE_VIDEO_MODE:
        pass

DEBUGFUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
STATEFUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_int)

DEBUG_CALLBACK = DEBUGFUNC(debug_callback)
STATE_CALLBACK = STATEFUNC(state_callback)




# Load the Mupen64Plus API library
m64p = ctypes.cdll.LoadLibrary(DYNLIB_PATH)

# start core
rval = m64p.CoreStartup(ctypes.c_int(CORE_API_VERSION), None, None, ctypes.c_char_p(b"Core"), DEBUG_CALLBACK, ctypes.c_char_p(b"State"), STATE_CALLBACK)
if rval!=M64ERR_SUCCESS:
    raise Exception("Error!")

# load rom
romLength = ctypes.c_int(os.path.getsize(ROM_PATH))
f = open(ROM_PATH, "rb")
romFile = f.read()
f.close()
romBuffer = ctypes.c_buffer(romFile)
romTest = m64p.CoreDoCommand(M64CMD_ROM_OPEN, romLength, ctypes.byref(romBuffer))

def pluginVersion(handle):
    try:
        type_ptr = ctypes.pointer(ctypes.c_int())
        ver_ptr = ctypes.pointer(ctypes.c_int())
        api_ptr = ctypes.pointer(ctypes.c_int())
        name_ptr = ctypes.pointer(ctypes.c_char_p())
        cap_ptr = ctypes.pointer(ctypes.c_int())
        rval = handle.PluginGetVersion(type_ptr, ver_ptr, api_ptr, name_ptr, cap_ptr)
    except AttributeError:
        raise Exception("Plugin version error.")
    except OSError as err:
        raise Exception("Plugin version error.")
    else:
        if rval == M64ERR_SUCCESS:
            return (type_ptr.contents.value, ver_ptr.contents.value, api_ptr.contents.value,
                        name_ptr.contents.value.decode(), cap_ptr.contents.value)
        else:
            raise Exception("Plugin version error.")

# load plugin function
def pluginLoad(pluginPath=None):
    try:
        pluginHandle = ctypes.cdll.LoadLibrary(pluginPath)
        version = pluginVersion(pluginHandle)
        if version:
            plugin_type, plugin_version, plugin_api, plugin_desc, plugin_cap = version
            plugin_name = os.path.basename(pluginPath)
            PLUGIN_MAP[plugin_type][plugin_name] = (pluginHandle, pluginPath, PLUGIN_NAME[plugin_type], plugin_desc, plugin_version)
        else:
            print("Load plugin error")
    except OSError as e:
        raise Exception("Plugin Load error: %s" % e)

# start plugin function
def pluginStartup(handle, name):
    rval = handle.PluginStartup(ctypes.c_void_p(m64p._handle),name, DEBUG_CALLBACK)
    if rval != M64ERR_SUCCESS:
        raise Exception("Fail to start plugin.")

# load plugins
for key, value in PLUGIN_DEFAULT.items():
    path = "./test/" + value
    print(path)
    pluginLoad(path)

# start plugins
for plugin_type in PLUGIN_MAP.keys():
    for plugin_map in PLUGIN_MAP[plugin_type].values():
        (plugin_handle, plugin_path, plugin_name, plugin_desc, plugin_version) = plugin_map
        # pluginStartup(plugin_handle, plugin_name)
        print(plugin_map)


# attach plugin to core
for pluginType in PLUGIN_ORDER:
    print(pluginType)
    # retVal = m64p.CoreAttatchPlugin(ctypes.c_int(pluginType), ctypes.c_void_p())

print(PLUGIN_MAP)
# execute

# detatch plugins


# close rom

# close core
m64p.CoreShutdown()

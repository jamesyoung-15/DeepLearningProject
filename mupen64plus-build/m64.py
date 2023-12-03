# This script is based on mupen64plusui-python (https://github.com/mupen64plus/mupen64plus-ui-python)
# Refer to the Mupen64Plus API as well for C++ APIs (https://www.mupen64plus.org/wiki/index.php/Mupen64Plus_v2.0_Core_Config)




import ctypes
import subprocess
import time
import os
import sys

# header file defines
from m64py.defs import *

# Library locations
MUPEN_PATH = "./test/mupen64plus"
DYNLIB_PATH = "./test/libmupen64plus.so.2"
# ROM Path
ROM_PATH = "../rom/mariokart64.n64"

def debug_callback(context, level, message):
    if level <= M64MSG_ERROR:
        sys.stderr.write("%s: %s\n" % (context.decode(), message.decode()))
    elif level == M64MSG_WARNING:
        sys.stderr.write("%s: %s\n" % (context.decode(), message.decode()))
    elif level == M64MSG_INFO or level == M64MSG_STATUS:
        sys.stderr.write("%s: %s\n" % (context.decode(), message.decode()))
    elif level == M64MSG_VERBOSE and VERBOSE:
        sys.stderr.write("%s: %s\n" % (context.decode(), message.decode()))


def state_callback(context, param, value):
    if param == M64CORE_VIDEO_SIZE:
        pass
    elif param == M64CORE_VIDEO_MODE:
        pass

DEBUGFUNC = C.CFUNCTYPE(None, C.c_char_p, C.c_int, C.c_char_p)
STATEFUNC = C.CFUNCTYPE(None, C.c_char_p, C.c_int, C.c_int)

DEBUG_CALLBACK = DEBUGFUNC(debug_callback)
STATE_CALLBACK = STATEFUNC(state_callback)

class M64:
    pluginMap = {
        M64PLUGIN_RSP: {},
        M64PLUGIN_GFX: {},
        M64PLUGIN_AUDIO: {},
        M64PLUGIN_INPUT: {}
    }

    def __init__(self):
        """Constructor"""
        self.m64p = None
        self.config = None

    def getHandle(self):
        """Return core library handle"""
        return self.m64p

    def coreLoad(self, path=None):
        """Load core"""
        try:
            if path:
                self.m64p = ctypes.cdll.LoadLibrary(path)
            else:
                raise Exception("No path specified")
        except Exception as err:
            self.m64p = None
            print(err)
    
    def coreStart(self, path):
        """Start Core"""
        rval = self.m64p.CoreStartup(
            ctypes.c_int(CORE_API_VERSION), None, ctypes.c_char_p(os.path.dirname(path).encode()),
            ctypes.c_char_p(b"Core"), DEBUG_CALLBACK, ctypes.c_char_p(b"State"), STATE_CALLBACK)
        if rval == M64ERR_SUCCESS:
            # self.config = Config(self)
            pass
        else:
            print("Error starting core library")
    
    def coreShutdown(self):
        """Shutdown core"""
        if self.m64p:
            self.m64p.CoreShutdown()
        return M64ERR_SUCCESS
    
    def getPluginVersion(self, handle, path):
        """Retrieve plugin info"""
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

    def pluginLoadIndividual(self, path=None):
        """Load a plugin from passed path"""
        try:
            pluginHandle = ctypes.cdll.LoadLibrary(path)
            version = self.getPluginVersion(pluginHandle, path)
            if version:
                pluginType, pluginVersion,  pluginAPI, pluginDesc, pluginCap  = version
                pluginName = os.path.basename(path)
                self.pluginMap[pluginType][pluginName] = (pluginHandle, path, PLUGIN_NAME[pluginType], pluginDesc, pluginVersion)
        except OSError as e:
            raise Exception("Error loading plugin")
    
    def pluginLoadAll(self, pluginLocation):
        """Load all the default plugins from defs.py"""
        for key, value in PLUGIN_DEFAULT.items():
            path = pluginLocation + value
            print(path)
            pluginLoadIndividual(path)
    
    def pluginStartup(self, handle, name, desc):
        """Start plugin"""
        rval = handle.PluginStartup(ctypes.c_void_p(self.m64p._handle), name, DEBUG_CALLBACK)
        if rval!=M64ERR_SUCCESS:
            raise Exception("Error starting plugin")

    def pluginShutdown(self, handle, desc):
        """Shutdown plugin"""
        rval = handle.PluginShutdown()

    def pluginAttach(self, plugins):
        """Attach plugins to core"""
        pass

    def pluginDetatch(self):
        """Detatch plugin from core"""
        pass

    def romOpen(self, romPath):
        """Open ROM file"""
        # load rom
        romLength = ctypes.c_int(os.path.getsize(romPath))
        try:
            f = open(romPath, "rb")
        except IOError:
            raise IOError("ROM does not exist. Check path")
        romFile = f.read()
        f.close()
        romBuffer = ctypes.c_buffer(romFile)
        romTest = self.m64p.CoreDoCommand(M64CMD_ROM_OPEN, romLength, ctypes.byref(romBuffer))
        if romTest!=M64ERR_SUCCESS:
            raise Exception("Failed to open ROM")
        del romBuffer
        
    def romClose(self):
        """Close ROM file"""
        self.m64p.CoreDoCommand(M64CMD_ROM_CLOSE)

    def romGetHeader(self):
        """Get header data of ROM"""
        pass

    def romGetSettings(self):
        """Get settings of ROM"""
        pass

    def startEmulator(self):
        """Start emulator and run ROM"""
        rval = self.m64p.CoreDoCommand(M64CMD_EXECUTE,0,None)
        if rval!=M64ERR_SUCCESS:
            print("Couldn't start emulator")

    def stopEmulator(self):
        """Stop emulator"""
        rval = self.m64p.CoreDoCommand(M64CMD_STOP,0,None)
    
    def stateLoad(self, statePath=" ~/.local/share/mupen64plus/save/"):
        """Load a saved state file from current slot"""
        path = ctypes.c_char_p(statePath.encode())
        rval = self.m64p.CoreDoCommand(M64CMD_STATE_LOAD, ctypes.c_int(1), path)
        if rval!=M64ERR_SUCCESS:
            print("Failed to load state")
    
    

    
    

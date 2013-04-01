# coding: utf-8
# Telldus python library
# by Stefan Midjich 2013 Ⓐ 

# This was made for my Kraft web interface so the plan is to let this library 
# grow organically with features added as I need/gain access to more devices 
# and sensors. 
# On the wishlist are sensors for humidity and temperature. 

## Changelog
# 2013-03-29
#   Starting with regular selflearning on/off switches

from platform import system as OS
from ctypes import c_char_p, c_void_p, CDLL

# Default library locations
_DEFAULT_LIBRARY_MACOS = '/Library/Frameworks/TelldusCore.framework/TelldusCore'
_DEFAULT_LIBRARY_LINUX = '/usr/local/lib/libtelldus-core.so'

## Defining pre-proc macros from the telldus-core lib
TELLSTICK_SUCCESS = 0

# Supported methods
METHOD_TURNON = 1
METHOD_TURNOFF = 2
METHOD_LEARN = 32

# Device types
TELLSTICK_TYPE_DEVICE = 1
TELLSTICK_TYPE_GROUP = 2
TELLSTICK_TYPE_SCENE = 3

# Class constructor, for handling input validation before calling lower 
# layered C-API wrappers. 
class Telldus:
    # Class initialiser, load the shared object and its symbols, do some 
    # pre-processing. 
    def __init__(self, *kw):
        # Support to pass custom library name/path to class
        if kw:
            library = kw.get('library', _DEFAULT_LIBRARY_LINUX)
        else: # Load some defaults based on system
            if OS() == 'Darwin':
                library = _DEFAULT_LIBRARY_MACOS
            else: # Default fallback is always Linux
                library = _DEFAULT_LIBRARY_LINUX

        # Load telldus-core library. Also makes C interface available to 
        # higher level. 
        self.tdso = CDLL(library)

        # Initiate library
        self._init_telldus()
        self.number_of_devices = self._get_number_of_devices()

    # Wrappers for functions in telldus-core, for handling type conversions and 
    # freeing up memory. 
    def _init_telldus(self):
        self.tdso.tdInit()

    def _get_number_of_devices(self):
        return self.tdso.tdGetNumberOfDevices()

    def _get_id(self, device_index):
        return self.tdso.tdGetDeviceId(device_index)

    def _get_name(self, device_id):
        # Because tdGetName returns a char* we first receive a void*
        get_name_func = self.tdso.tdGetName
        get_name_func.restype = c_void_p

        name_p = get_name_func(device_id)

        # Convert void* to char* and copy char* from C library to local 
        # Python str.
        name = c_char_p(name_p).value

        # Free void* from memory of C library
        # For some reason it crashes everytime it tries to free memory on Mac,
        # so I hope I can just skip that step because it's not working. 
        if OS() != 'Darwin':
            self.tdso.tdReleaseString(name_p)
            name_p = None

        # Return the copied Python str
        return name

    # Largely same concept as _get_name
    def _get_protocol(self, device_id):
        get_protocol_func = self.tdso.tdGetProtocol
        get_protocol_func.restype = c_void_p

        protocol_p = get_protocol_func(device_id)

        protocol = c_char_p(protocol_p).value

        self.tdso.tdReleaseString(protocol_p)
        protocol_p = None

        return protocol

    def _get_device_type(self, device_id):
        return self.tdso.tdGetDeviceType(device_id)

    def _methods(self, device_id, methods):
        return self.tdso.tdMethods(device_id, methods)

    def _turn_on(self, device_id):
        return self.tdso.tdTurnOn(device_id)

    def _turn_off(self, device_id):
        return self.tdso.tdTurnOff(device_id)

    ## "Public" methods here, for use by higher levels
    # Get the first device by default
    def get_device_by_index(self, index=0):
        if not isinstance(index, int):
            index = 0
        return self._get_id(index)

    def turn_on(self, device_id):
        if not isinstance(device_id, int):
            raise TypeError
        return self._turn_on(device_id)

    def turn_off(self, device_id):
        if not isinstance(device_id, int):
            raise TypeError
        return self._turn_off(device_id)

    def recount_devices(self):
        self.number_of_devices = self._get_number_of_devices()

    # Generator to iterate through all devices
    def Devices(self, group=False):
        current = 0
        high = self.number_of_devices

        # Loop every device index
        while current <= high:
            device_index = current
            device_id = self._get_id(current)
            device_name = self._get_name(device_id)
            device_type = self._get_device_type(device_id)
            device_methods = self._methods(device_id, (
                METHOD_TURNON|
                METHOD_TURNOFF|
                METHOD_LEARN
            ))

            if group and device_type != TELLSTICK_TYPE_GROUP:
                current += 1
                continue

            if not group and device_type != TELLSTICK_TYPE_DEVICE:
                current += 1
                continue

            # Return useful info about each device
            yield (
                device_index, 
                device_id, 
                device_name,
                device_methods,
            )
            current += 1

    # Generator to iterate through all groups
    def Groups(self):
        return self.Devices(group=True)

# Exception for TD class, handling errors thrown by C-API or internal errors.
class TelldusException(Exception):
    def __init__(self, errstr):
        self.errstr = errstr

    def __str__(self):
        return repr(self.errstr)

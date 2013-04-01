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
from ctypes import c_int, c_char_p, c_void_p, CDLL

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
TYPE_DEVICE = 1
TYPE_GROUP = 2
TYPE_SCENE = 3

# Class constructor, for handling input validation before calling lower 
# layered C-API wrappers. 
class Telldus(object):
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

        # Internal list of devices
        self.devices = []

    ## Wrappers for functions in telldus-core, for handling type conversions and 
    # freeing up memory. These should stay as true to the C API as possible 
    # while converting values to Python objects. 
    def _init_telldus(self):
        return self.tdso.tdInit()

    def _add_device(self):
        return self.tdso.tdAddDevice()

    def _get_number_of_devices(self):
        return self.tdso.tdGetNumberOfDevices()

    # Returns 0 when device is not found, instead of -1 as API docs claim. 
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

    def _set_name(self, device_id, device_name):
        set_name_func = self.tdso.tdSetName
        set_name_func.argtypes = [c_int, c_char_p]

        return set_name_func(device_id, device_name)

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

    ## "Public" methods here, for use by higher levels. These should 
    # Pythonize output and use Exceptions when possible. 
    # Get the first device by default
    def get_device_by_index(self, index=0):
        if not isinstance(index, int):
            index = 0

        dev_id = self._get_id(index)

        if dev_id < 1:
            return False
        return dev_id

    def recount_devices(self):
        self.number_of_devices = self._get_number_of_devices()

    # Generator to iterate through all devices. This returns a class instance 
    # of Device, which contains more Device-specific methods. 
    def Devices(self, group=False):
        device = None
        current = 0
        high = self.number_of_devices

        # Loop every device index
        while current <= high:
            self.recount_devices()

            # If number of devices has changed, return new devices and rebuild
            # internal list. 
            if self.number_of_devices != len(self.devices):
                # Prepare relevant values
                device_index = current
                device_id = self._get_id(current)
                device_name = self._get_name(device_id)
                device_type = self._get_device_type(device_id)

                # Init the Device class
                device = Device(
                    self,
                    index = device_index,
                    id = device_id,
                    name = device_name,
                    type = device_type
                )

                try:
                    self.devices[current] = device
                except(IndexError):
                    self.devices.append(device)
            else:
                device = self.devices[current]

            # Handle counter for groups
            if group and device_type != TYPE_GROUP:
                current += 1
                continue

            # Handle counter for devices
            if not group and device_type != TYPE_DEVICE:
                current += 1
                continue

            # TODO: Scenes

            # Return the class
            yield device
            current += 1

    # Generator to iterate through all groups
    def Groups(self):
        return self.Devices(group=True)

# This class will create the device if it does not exist. 
class Device(object):
    def __init__(self, Telldus, **kw):
        self._td = Telldus

        # Get device arguments, with default values
        self.index = kw.get('index', 0)
        self.id = kw.get('id', 0)
        self.name = kw.get('name', 'My device')
        self.type = kw.get('type', TYPE_DEVICE)

        # Check if device parameters are ok
        dev_id = self._td.get_device_by_index(self.index)
        if not dev_id:
            # Device does not exist, attempt to create with parameters given.
            dev_id = self._td._add_device()
            if dev_id < 0:
                raise TDDeviceException('Failed to create new device')

            self.id = dev_id
            # Because the C-API can't return the index we need to reset it 
            # on new devices. 
            self.index = None

            # Append this new device to the internal list of the "superclass"
            self._td.devices.append(self)
            self._td.recount_devices()

            # Set the name of the new device according to params provided. 
            self.set_name(self.name)
        else:
            # Device does exist, adjust parameters accordingly. We obey the
            # index given at class init blindly here, and we don't trust the 
            # user provided parameters. 
            if self.id != dev_id:
                self.id = dev_id

            dev_name = self._td._get_name(self.id)
            if self.name != dev_name:
                self.name = dev_name

            dev_type = self._td._get_device_type(self.id)
            if self.type != dev_type:
                self.type = dev_type

    def set_name(self, device_name):
        device_id = self.id

        res = self._td._set_name(device_id, device_name)
        return bool(res)

    def get_name(self):
        device_id = self.id

        device_name = self._td._get_name(device_id)
        if device_name == '':
            return False
        return device_name

    def get_id(self):
        return self.id

    def get_index(self):
        return self.index

    def turn_on(self):
        device_id = self.id

        res = self._td._turn_on(device_id)
        if res == TELLSTICK_SUCCESS:
            return True
        return False

    def turn_off(self, device_id):
        device_id = self.id

        res = self._td._turn_off(device_id)
        if res == TELLSTICK_SUCCESS:
            return True
        return False

# Exception for TD class, handling errors thrown by C-API or internal errors.
class TDException(Exception):
    def __init__(self, errstr):
        self.errstr = errstr

    def __str__(self):
        return repr(self.errstr)

class TDDeviceException(TDException):
    def __init__(self, errstr):
        self.errstr = errstr

    def __str__(self):
        return repr(self.errstr)

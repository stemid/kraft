# coding: utf-8
# Telldus python library
# by Stefan Midjich 2013 Ⓐ
#    Stewart Rutledge 2013

# This was made for the Kraft web interface so the plan is to let this library
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
_DEFAULT_LIBRARY_LINUX = 'libtelldus-core.so'

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

    ## Wrappers for functions in libtelldus-core, for handling type conversions 
    # and freeing up memory. These should stay as true to the C API as possible
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

    # Sets the various parameters (see set_house function)
    def _set_parameter(self, device_id, parameter, parm_value):
        set_parameter_func = self.tdso.tdSetDeviceParameter
        try:
            parameter
            parm_value
        except:
            raise
        # Both parameter and parm_value need to be strings, if an integer is passed to parm_value it results in a seg fault. NOT GOOD!
        return set_parameter_func(device_id, str(parameter), str(parm_value))

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

    def _learn(self, device_id):
        return self.tdso.tdLearn(device_id)

    ## End of wrapper functions for libtelldus-core

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
    def Devices(self):
        # Re-count devices in internal counter
        self.recount_devices()

        device = None
        current = 0
        high = self.number_of_devices

        # Loop every device index
        while current != high:
            if self.number_of_devices < 1:
                # No devices, need to add some.
                raise StopIteration
            else:
                device_index = current

            # Decide on using internal devices list or building a new one.
            if self.number_of_devices == len(self.devices):
                device = self.devices[current]
            else:
                # Init the Device class
                device = Device(
                    self,
                    index = device_index
                )

                # If the device index exists in the list, simply update it.
                try:
                    self.devices[current] = device
                except(IndexError):
                    # If not, append it.
                    self.devices.append(device)

            # Increment counter
            current += 1

            # Return the class
            yield device

    # Generator to iterate through all groups
    def Groups(self):
        return self.Devices(group=True)

# This class will create the device if it does not exist.
class Device(object):
    def __init__(self, telldus, **kw):
        # Telldus class instance for use in this class. It's not quite
        # subclassing but it does the job. Probably room for improvement. 
        self._td = telldus

        # Get device arguments, with default values
        self.index = kw.get('index', 0)

        # Check if device parameters are ok
        dev_id = self._td.get_device_by_index(self.index)
        if not dev_id:
            # Device does not exist, attempt to create with parameters given.
            dev_id = self._td._add_device()

            if not bool(dev_id):
                raise TDDeviceException('Failed to create new device')

            self._device_id = dev_id
            # Because the C-API can't return the index we need to reset it
            # on new devices.
            self.index = None
            # TODO: Perhaps recount_devices and guess the index?

            # Append this new device to the internal list of the "superclass"
            self._td.devices.append(self)
            self._td.recount_devices()
        else:
            # Device does exist, adjust parameters accordingly.
            self._device_id = dev_id

    def set_name(self, device_name):
        device_id = self._device_id

        res = self._td._set_name(device_id, device_name)
        self._device_name = res
        return bool(res)

    @property
    def device_name(self):
        device_id = self._device_id

        device_name = self._td._get_name(device_id)
        if device_name == '':
            return False
        self._device_name = device_name
        return device_name

    def set_house(self, house_id):
        device_id = self._device_id

        res = self._td._set_parameter(device_id, 'House', house_id)
        self.house_id = res
        return bool(res)

    @property
    def device_house(self):
        return self.house_id

    @property
    def device_id(self):
        return self._device_id

    @property
    def device_index(self):
        return self.index

    def learn(self):
        method = self._td._methods(self._device_id, METHOD_LEARN)
        if method == METHOD_LEARN:
            res = self._td._learn(self._device_id)
            if res == TELLSTICK_SUCCESS:
                return True
            else:
                raise TDDeviceException('Could not teach device')
        raise TDDeviceException('Device does not support learn')

    @property
    def device_type(self):
        # Neat trick since everything is an object and str() calls the
        # __str__ method in any object, not just classes.
        def __str__(self):
            if self.type == 2:
                return 'Group'
            if self.type == 3:
                return 'Scene'
            return 'Device'
        return self.type

    # TODO: def is_group
    # TODO: def is_device

    def turn_on(self):
        device_id = self._device_id

        res = self._td._turn_on(device_id)
        if res == TELLSTICK_SUCCESS:
            return True
        return False

    def turn_off(self):
        device_id = self._device_id

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

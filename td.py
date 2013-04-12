# coding: utf-8
# Telldus python library
# by Stefan Midjich Ⓐ
#    Stewart Rutledge

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
_DEFAULT_LIBRARY_LINUX = 'libtelldus-core.so.2'

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

    # Gets parameters from device
    def _get_device_parameter(self, device_id, param_key='', default_value=''):
        get_parameter_func = self.tdso.tdGetDeviceParameter
        get_parameter_func.restype = c_void_p
        get_parameter_func.argtypes = [c_int, c_char_p, c_char_p]

        param_p = get_parameter_func(device_id, param_key, default_value)
        param = c_char_p(param_p).value

        if OS() != 'Darwin':
            self.tdso.tdReleaseString(param_p)
            param_p = None

        return param

    # Sets the various parameters (see Device.house property)
    def _set_device_parameter(self, device_id, param_key='', param_value=''):
        set_parameter_func = self.tdso.tdSetDeviceParameter

        # Both parameter and parm_value need to be strings, if an integer is 
        # passed to parm_value it results in a segfault. NOT GOOD!
        return set_parameter_func(device_id, str(param_key), str(param_value))

    # Largely same concept as _get_name
    def _get_protocol(self, device_id):
        get_protocol_func = self.tdso.tdGetProtocol
        get_protocol_func.restype = c_void_p

        protocol_p = get_protocol_func(device_id)
        protocol = c_char_p(protocol_p).value

        if OS() != 'Darwin':
            self.tdso.tdReleaseString(protocol_p)
            protocol_p = None

        return protocol

    def _set_protocol(self, device_id, protocol):
        set_protocol_func = self.tdso.tdSetProtocol
        set_protocol_func.restype = c_void_p
        set_protocol_func.argtypes = [c_int, c_char_p]

        return set_protocol_func(device_id, protocol)

    def _get_device_type(self, device_id):
        return self.tdso.tdGetDeviceType(device_id)

    def _get_model(self, device_id):
        get_model_func = self.tdso.tdGetModel
        get_model_func.restype = c_void_p

        model_p = get_model_func(device_id)
        model = c_char_p(model_p).value

        if OS() != 'Darwin':
            self.tdso.tdReleaseString(model_p)
            model_p = None

        return model

    def _set_model(self, device_id, model_name=''):
        if not len(model_name):
            raise ValueError('"model_name" cannot be empty string')
        set_model_func = self.tdso.tdSetModel
        set_model_func.argtypes = [c_int, c_char_p]

        return set_model_func(device_id, str(model_name))

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

# This class will create the device if it does not exist.
class Device(object):
    def __init__(self, telldus, **kw):
        # Telldus class instance for use in this class. It's not quite
        # subclassing but it does the job. 
        if isinstance(telldus, Telldus):
            self._td = telldus
        else:
            raise TypeError('First argument must be Telldus instance')

        # Get device arguments, with default values
        self.index = kw.get('index', 0)

        # Check if device exists based on index given
        dev_id = self._td.get_device_by_index(self.index)
        if not dev_id:
            # Device does not exist, attempt to create with parameters given.
            dev_id = self._td._add_device()

            if not bool(dev_id):
                raise TDDeviceError('Failed to create new device')

            # Save new device ID
            self._device_id = dev_id

            # Because the C-API can't return the index we need to reset it
            # on new devices.
            self.index = None
            # TODO: Perhaps recount_devices and guess the index?
        else:
            # Device does exist, save/update its device ID
            self._device_id = dev_id

        # Append this new device to the internal list of the "superclass"
        self._td.devices.append(self)
        self._td.recount_devices()
        
        # Init parameters dictionary
        self.parameters = {}

    ## Methods here

    # Set parameters for the device
    def set_parameter(self, parameter=None, value=''):
        device_id = self._device_id

        if not parameter:
            raise ValueError('"parameter" is required argument')

        res = self._td._set_device_parameter(device_id, parameter, value)

        if res is True:
            self.parameters[parameter] = value
        return bool(res)

    # Get a parameter of the device
    def get_parameter(self, parameter=None, default_value=None):
        device_id = self._device_id

        if not parameter:
            raise ValueError('"parameter is required argument')

        value = self._td._get_device_parameter(device_id, parameter, '')

        if bool(value) is False:
            return default_value
        return value

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

    def learn(self):
        method = self._td._methods(self._device_id, METHOD_LEARN)
        if method == METHOD_LEARN:
            res = self._td._learn(self._device_id)
            if res == TELLSTICK_SUCCESS:
                return True
            else:
                raise TDDeviceError('Could not teach device')
        raise TDDeviceError('Device does not support learn')

    # TODO: def is_group
    # TODO: def is_device

    ## Define all properties here

    # Device.device_name property
    @property
    def name(self):
        device_id = self._device_id

        device_name = self._td._get_name(device_id)
        if device_name == '':
            raise TDDeviceError('Device not found')

        return device_name

    @name.setter
    def name(self, device_name=''):
        device_id = self._device_id

        res = self._td._set_name(device_id, device_name)
        return bool(res)

    @name.deleter
    def name(self):
        device_id = self._device_id

        res = self._td._set_name(device_id, '')
        return bool(res)

    @property
    def model(self):
        device_id = self._device_id
        return self._td._get_model(device_id)

    @model.setter
    def model(self, model):
        device_id = self._device_id
        try:
            res = self._td._set_model(device_id, model)
        except:
            raise

    @property
    def protocol(self):
        device_id = self._device_id
        return self._td._get_protocol(device_id)

    @protocol.setter
    def protocol(self, protocol):
        device_id = self._device_id
        try:
            self._td._set_protocol(device_id, protocol)
        except:
            raise

    # Read-only properties
    @property
    def house(self):
        device_id = self._device_id
        house = self.get_parameter('house')
        return house

    @house.setter
    def house(self, house):
        device_id = self._device_id
        return self.set_parameter('house', house)

    @property
    def unit(self):
        device_id = self._device_id
        return self.get_parameter('unit')

    @unit.setter
    def unit(self, unit=''):
        device_id = self._device_id
        return self.set_parameter('unit', unit)

    @property
    def id(self):
        return self._device_id

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    @index.deleter
    def index(self):
        del self._index

    @property
    def type(self):
        # Neat trick since everything is an object and str() calls the
        # __str__ method in any object, not just classes.
        def __str__(self):
            if self.type == 2:
                return 'Group'
            if self.type == 3:
                return 'Scene'
            return 'Device'
        return self.type

# Exception for TD class, handling errors thrown by C-API or internal errors.
class TDError(Exception):
    def __init__(self, errstr):
        self.errstr = errstr

    def __str__(self):
        return repr(self.errstr)

class TDDeviceError(TDException):
    def __init__(self, errstr):
        self.errstr = errstr

    def __str__(self):
        return repr(self.errstr)

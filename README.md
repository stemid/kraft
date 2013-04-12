# Kraft

Work in progress to create a web interface for the Tellstick and some devices connected to it that can power on/off lamps in my home so far. 


This example assumes you have both a tellstick.conf file filled with devices (which are then irretated on in "for device in tell.Devices" as well as the telldusd daemon running.

The goal is to eventually get around these requirements and allow a direct iteraction with, at the very least, no configuration file.

### Example of learning a new device

Initiating the Device class with a new index will create a new, blank, device. Initiating it with an existing index will take over an existing device. 

    >>> import td
    >>> t = td.Telldus()
    >>> d = td.Device(t, index=8)
    >>> d.model = 'selflearning-switch'
    >>> d.protocol
    'everflourish'
    >>> d.model
    'selflearning-switch'
    >>> d.house
    >>> d.unit
    >>> d.house = '1488'
    >>> d.unit = '1'
    >>> d.house
    '1488'
    >>> d.unit
    '1'
    >>> d.learn()
    True
    >>> d.turn_off()
    True

### Example of iterating over existing devices

    >>> import td
    >>> tell = td.Telldus()
    >>> devices = []
    >>> for device in tell.Devices():
    ...  devices.append(device)
    ...
    >>> devices
    [<td.Device object at 0x1099a5710>, <td.Device object at 0x1099a53d0>, <td.Device object at 0x1099a56d0>, <td.Device object at 0x1099a5810>, <td.Device object at 0x1099a5fd0>, <td.Device object at 0x1099af090>, <td.Device object at 0x1099af110>, <td.Device object at 0x1099af190>, <td.Device object at 0x1099f2890>]
    >>> devices[0].get_name()
    'testar'
    >>> devices[1].get_name()
    'Sovrum'
    >>> devices[2].get_name()
    'UNKNOWN'
    >>> devices[3].get_name()
    'Lampa 1'
    >>> devices[3].turn_on()
    True
    >>> devices[3].turn_off()
    True
    >>> len(devices)
    9
    >>> devices[8].get_name()
    'Vardagsrum'
    >>> devices[7].get_name()
    'lol'

## Files

  * td.py library is to handle C-API wrapping.
  * kraft.py is the web.py application
  * api.py is the REST API
  * model.py is the DB API

## Roadmap

  * Avoid creating and editing tellstick.conf
  * Keep td.py library stateless of devices, prefer higher layers for this

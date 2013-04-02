Work in progress to create a web interface for the Tellstick and some devices connected to it that can power on/off lamps in my home so far. 

# Example

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

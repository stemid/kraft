# Kraft

Work in progress to create a web interface for the Tellstick and some devices connected to it that can power on/off lamps in my home so far. 

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
    >>> t = td.Telldus()
    >>> for device in t.Devices():
    ...  print "ID: %s, Name: %s" % (device.id, device.name)
    ...
    ID: 7, Name: testar
    ID: 11, Name: wut
    ID: 6, Name: Sovrum
    ID: 14, Name:
    ID: 10, Name: UNKNOWN
    ID: 5, Name: Lampa 1
    ID: 13, Name:
    ID: 4, Name: Fläkt
    ID: 9, Name: Vardagsrum lampa 1
    ID: 3, Name: Lampa 1
    ID: 12, Name:
    ID: 8, Name: lol
    ID: 2, Name: Vardagsrum

## Files

  * td.py library is to handle C-API wrapping.
  * kraft.py is the web.py application
  * api.py is the REST API
  * model.py is the DB API

## Roadmap

  * Avoid creating and editing tellstick.conf
  * Keep td.py library stateless of devices, prefer higher layers for this

import web
import re
#from td import Telldus, Device
#from db import DeviceDB, GroupDB
#td = Telldus()

# More or less there are two name spaces here: device and group.

urls = (
    '/device/power/([0-9+])/(off|on)', 'turn_off_and_on',
    '/device/add', 'add_device'
)

class turn_off_and_on:
    def GET(self, device_id, method):
        d = Device(td,id=device_id)
        on = re.match("^on$", method)
        off = re.match("^off$", method)
        try:
            if on:
                d.turn_on()
            if off:
                d.turn_off()
        except:
            return "Could not turn device %s %s" % (device_id, method)
            return "Turned device %s %s \n" % (device_id, method)

class add_device:
    def GET(self):
        query = web.input()
        try:
            query.name
            query.did
            query.protocol
        except AttributeError, n:
            return "%s is a requried field\n" % n
        else:
            return "Adding device with id: %s name: %s protocol: %s \n" % (query.did, query.name, query.protocol)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

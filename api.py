# coding: utf-8
# Kraft REST API
# by Stefan Midjich 2013 Ⓐ 
#    Stewart Rutledge 2013

# A very basic beginning to an api with a simple turn on/off function based on ID and some regexing

import web
import re
from td import Telldus, Device
td = Telldus()

urls = (
  '/([0-9])/turn/(off|on)', 'turn_off_and_on'
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

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()



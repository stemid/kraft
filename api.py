# coding: utf-8
# Kraft REST API
# by Stefan Midjich 2013 Ⓐ 
#    Stewart Rutledge 2013

import web
from td import Telldus, Device

# Initiate Telldus library
td = Telldus()

urls = (
    '/device/(off|on|parameter|model|protocol)', 'Device',
)

# Set to JSON output globally since this is pure REST API
web.header('Content-type', 'application/json')

class Device:
    def __init__(self):
        query = web.input(
            device_index = None,
            # TODO: device_name = None
        )

        if not device_index and not device_name:
            raise web.internalerror()

        # TODO: Only supports by index now, fix by name later. 
        # Initiate the device
        try:
            self._d = Device(td, index=query.device_index)
        except(TDDeviceError), e:
            web.internalerror()
            return json.dumps(dict(error=str(e)))

    # This is mostly to get properties of the device but also to call methods
    # like turn_on, turn_off and such. 
    def GET(self, device_index, method):
        if method == 'on':
            d.turn_on()
            return web.ok()

        if method == 'off':
            d.turn_off()
            return web.ok()

        if method == 'parameter':
            query = web.input(
                parameter = None,
                value = ''
            )

            if not query.parameter:
                raise web.badrequest()

            try:
                value = d.get_parameter(parameter)
            except:
                raise web.internalerror()

            if not value:
                raise web.notfound()

        if method == 'model':
            model = d.model
            if not model:
                raise web.notfound()

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()

if __name__.startswith('_mod_wsgi_'):
    application = app.wsgifunc()

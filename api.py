# coding: utf-8
# Kraft REST API
# by Stefan Midjich 2013 Ⓐ 
#    Stewart Rutledge 2013

import web
import td

# Initiate Telldus library
telldus = td.Telldus()

urls = (
    '/device/(off|on|parameter|model|protocol)', 'Device',
)

class Device:
    def __init__(self):
        from fnmatch import fnmatch

        # Set to JSON output
        web.header('Content-type', 'application/json')

        query = web.input(
            index = None,
            name = None
        )

        device = None

        # We have a device index
        if query.index:
            # Initiate the device
            try:
                self._d = td.Device(telldus, index=int(query.index))
            except(td.TDDeviceError), e:
                web.internalerror()
                return json.dumps(dict(error=str(e)))

        # We have a device name
        if query.name:
            # Find the device
            for device in telldus.Devices():
                if fnmatch(device.name, '%s*' % query.name):
                    break
                device = None

        # Use the device
        if not device:
            raise web.notfound()
        self._d = device

    # This is mostly to get properties of the device but also to call methods
    # like turn_on, turn_off and such. 
    def GET(self, method):
        if method == 'on':
            self._d.turn_on()
            return web.ok()

        if method == 'off':
            self._d.turn_off()
            return web.ok()

        if method == 'parameter':
            query = web.input(
                parameter = None,
                value = ''
            )

            if not query.parameter:
                raise web.badrequest()

            try:
                value = self._d.get_parameter(parameter)
            except:
                raise web.internalerror()

            if not value:
                raise web.notfound()

        if method == 'model':
            model = self._d.model
            if not model:
                raise web.notfound()

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()

if __name__.startswith('_mod_wsgi_'):
    application = app.wsgifunc()

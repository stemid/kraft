# Kraft web interface

import gettext
import web
from settings import Settings
s = Settings()
settings = s.config

import api
import td

# Initiate Telldus library
telldus = td.Telldus()

# Prepare localization
gettext.install('messages', settings['i18n_path'], unicode=True)
gettext.translation(
    'messages', 
    settings['i18n_path'], 
    languages=[
        settings['locale']
    ]
).install(True)

urls = (
    '/', 'Kraft',
    '/device/(off|on|learn|parameter|model|protocol)', 'api.Device',
    '/device', 'api.Device',
)

class Kraft:
    def __init__(self):
        self._devices = []
        for device in telldus.Devices():
            self._devices.append(device)

    def GET(self):
        tpl = web.template.render(
            settings['template_path'],
            base='base',
            globals = {
                'devices': self._devices,
                '_': _, # _ is automatically created by gettext.install()
            }
        )
        return tpl.index()

app = web.application(urls, globals())

if __name__ == '__main__':
    app.run()

if __name__.startswith('_mod_wsgi_'):
    application = app.wsgifunc()

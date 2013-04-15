# Kraft web interface

import web
from settings import Settings
s = Settings()
settings = s.config

urls = (
    '/', 'Kraft',
)

class Kraft:
    def GET(self):
        tpl = web.template.render(
            settings['template_path'],
            base='base',
        )
        return tpl.index()

app = web.application(urls, globals())

if __name__ == '__main__':
    app.run()

if __name__.startswith('_mod_wsgi_'):
    application = app.wsgifunc()

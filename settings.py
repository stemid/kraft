# Settings for kraft API and Web UI

# Edit this config block before attempting science.
config = {
    'debug': False,
    'template_path': 'templates',
    'static_path': 'static',
    'i18n_path': 'i18n',
    'locale': 'sv_SE',
}

# Try to avoid editing anything below this line, unless you're a nerd. 
from os.path import join, abspath, dirname

# Helpful functions for relative paths
here = lambda *p: join(abspath(dirname(__file__)), *p)
PROJECT_ROOT = here('.') # settings.py must be in PROJECT_ROOT already
root = lambda *p: join(abspath(PROJECT_ROOT), *p)

class Settings:
    def __init__(self, **kw):
        from fnmatch import filter

        self.config = config

        if kw.get('debug', None) in [True, False]:
            self.set_debug(status=kw.get('debug'))
        else:
            self.set_debug(status=config.get('debug', False))

        # Make all paths absolute
        settings = filter(config.keys(), '*_path')
        for setting in settings:
            config[setting] = root(config[setting])

    # Wrapper for web.py debug mode, just for no reason at all
    def set_debug(self, status=None):
        from web import config as webconfig

        if status is True:
            webconfig.debug = True
        elif status is False:
            webconfig.debug = False
        else:
            if webconfig.debug is True:
                webconfig.debug = False
            else:
                webconfig.debug = True
        self.config['debug'] = webconfig.debug

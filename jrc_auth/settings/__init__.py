from jrc_auth.settings.base import *

try:
    from jrc_auth.settings.local import *
except ImportError:
    print("Could not load local settings file: jrc_auth.settings.local")
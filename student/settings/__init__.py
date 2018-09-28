from sys import argv

if 'test' in argv:
    from .base import *
else:
    from .production import *

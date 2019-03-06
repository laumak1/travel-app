"""
context_processors.py
This file is dedicated for loading the assets json file and reading the dedicated bundle's name.
"""
import json
from os import path

from django.conf import settings

STATIC_ASSETS = None
STATIC_VENDOR_ASSETS = None

if not settings.WEBPACK_DEV_SERVER:
    ASSETS_JSON_FNAME = path.join(settings.STATIC_ASSETS_JSON)
    try:
        with open(ASSETS_JSON_FNAME, 'r') as f:
            JSON_DATA = json.load(f)
            STATIC_ASSETS = JSON_DATA['main']
            STATIC_VENDOR_ASSETS = JSON_DATA['vendors~main']
    except Exception:
        raise Exception('failed to read %s. was frontend built?' % ASSETS_JSON_FNAME)


# pylint: disable=unused-argument
def static_resources(request):
    """ used by base.html to figure out what statics to load """
    return {
        "WEBPACK_DEV_SERVER": settings.WEBPACK_DEV_SERVER,
        "static_assets": STATIC_ASSETS,
        "static_vendor_assets": STATIC_VENDOR_ASSETS,
    }

#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmcaddon

def useApiCache():
    return xbmcaddon.Addon().getSetting('useApiCache') == 'true'

def cacheExp():
    return int(xbmcaddon.Addon().getSetting('cacheExp'))

def useWidevine():
    return xbmcaddon.Addon().getSetting("drmToUse") == "0"

def debugLog():
    return xbmcaddon.Addon().getSetting('debugLog') == 'true'

#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmcaddon

__addon__ = xbmcaddon.Addon()


def useApiCache():
    return __addon__.getSetting('useApiCache') == 'true'


def cacheExp():
    return int(__addon__.getSetting('cacheExp'))


def useWidevine():
    return True  # int(__addon__.getSetting('cacheExp'))


def debugLog():
    return __addon__.getSetting('debugLog') == 'true'

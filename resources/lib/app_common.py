#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

from . import settings

version = xbmcaddon.Addon().getAddonInfo('version')
name = xbmcaddon.Addon().getAddonInfo('name')
plugin_name = name + ' - ' + version


addon_url = sys.argv[0]
addon_handle = int(sys.argv[1])
addon_id = xbmcaddon.Addon().getAddonInfo('id')
selfAddon = xbmcaddon.Addon(id=addon_id)
datapath = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
addonfolder = xbmc.translatePath(selfAddon.getAddonInfo('path'))
artfolder = os.path.join(addonfolder, 'resources', 'img')
watchedfolder = os.path.join(datapath, 'watched')
media_path = os.path.join(addonfolder, 'resources', 'media')

# paths
logopath = os.path.join(media_path, 'logos')
defaultlogo = defaultbanner = os.path.join(logopath, 'DefaultV2.png')
defaultbackdrop = ''


def translate(text):
    return selfAddon.getLocalizedString(text)


def log(message, logType='Info'):
    if logType.lower() == 'debug' and settings.debugLog() == False: return
    xbmc.log(msg='['+str(plugin_name)+'] ('+logType+') ' +
             str(message), level=xbmc.LOGDEBUG)


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split('&')
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

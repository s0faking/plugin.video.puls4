#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from .app_common import *
from .utils import *

_itemsToAdd = []


def addElement(title, fanart, icon, description, link, mode, channel='', duration=None, date='', isFolder=True,
               subtitles=None, width=768, height=432, showID=None):
    if fanart == '':
        fanart = defaultbanner
    if icon == '':
        icon = defaultbanner
    if description == '':
        description = (translate(30004))

    description = cleanText(description)
    title = cleanText(title)

    list_item = xbmcgui.ListItem(title)
    list_item.setInfo('video', {'title': title,
                                'Tvshowtitle': title,
                                'Sorttitle': title,
                                'Plot': description,
                                'Plotoutline': description,
                                'Aired': date,
                                'Studio': channel})

    list_item.setArt({'thumb': icon, 'icon': icon, 'fanart': fanart})
    list_item.setProperty('IsPlayable', str(not isFolder))

    if not duration:
        duration = 0
    if not isFolder:
        list_item.setInfo(type='Video', infoLabels={'mediatype': 'video'})
        list_item.addStreamInfo('video', {'codec': 'h264', 'duration': int(
            duration), 'aspect': 1.78, 'width': width, 'height': height})
        list_item.addStreamInfo(
            'audio', {'codec': 'aac', 'language': 'de', 'channels': 2})
        if subtitles != None:
            list_item.addStreamInfo('subtitle', {'language': 'de'})

    parameters = {'link': link, 'mode': mode, 'showID': showID}
    url = addon_url + '?' + encodeUrl(parameters)

    global _itemsToAdd
    _itemsToAdd.append((url, list_item, isFolder))


def addItemsToKodi(sort):
    xbmcplugin.setPluginCategory(addon_handle, 'Show')
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.addDirectoryItems(addon_handle, _itemsToAdd, len(_itemsToAdd))
    if sort:
        xbmcplugin.addSortMethod(
            addon_handle, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.endOfDirectory(addon_handle)
    log('callback done')


def play_video(url):
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    log('callback done')

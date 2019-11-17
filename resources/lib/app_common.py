#!/usr/bin/python
# -*- coding: utf-8 -*-
from future.standard_library import install_aliases
install_aliases()

import datetime
import gzip
import json
import os
import sys
import urllib.error
import urllib.request
from io import BytesIO as StringIO

import simplecache
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

from . import settings
from .xxtea import decryptBase64StringToStringss


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

common_cache = simplecache.SimpleCache()
_xxtea_key = '3543373833383336354337383634363635433738363633383236354337383330363435393543373833393335323435433738363533393543373833383332334635433738363633333344334235433738333836363335'


def get_data(url, forceFetch=False, noMatch=False):
    if not url:
        return url

    start = datetime.datetime.now()
    tag = ''
    data = ''

    forceFetch = forceFetch and not settings.useApiCache()

    cache = common_cache.get(url)
    if cache:
        try:
            tag = cache.get('tag')
            data = cache.get('data')
        except:
            data = cache

        if data and forceFetch:
            return json.loads(data)

    new_headers = {}
    if noMatch == True:
        new_headers.update({'If-None-Match': tag})
    new_headers.update(
        {'User-Agent': 'okhttp/3.10.0', 'Accept-Encoding': 'gzip'})

    try:
        request = urllib.request.urlopen(
            urllib.request.Request(url, headers=new_headers))
    except urllib.request.HTTPError as e:
        log(e.code)
        if noMatch and e.code == 304:
            return json.loads(data)
        failure = str(e)
        if hasattr(e, 'code') or hasattr(e, 'reason'):
            log('get_data ERROR: ' + url + ' / ' + failure)

        return json.loads(data)

    if request.info().get('Content-Encoding') == 'gzip':
        buffer = StringIO(request.read())
        deflatedContent = gzip.GzipFile(fileobj=buffer)
        data = deflatedContent.read()
    else:
        data = request.read()

    if noMatch:
        data = decryptBase64StringToStringss(data, _xxtea_key)
        common_cache.set(url, {'data': data, 'tag': request.info().get(
            'ETag')}, expiration=datetime.timedelta(days=200))
    else:
        common_cache.set(url, {'data': data, 'tag': ''}, expiration=datetime.timedelta(
            minutes=settings.cacheExp()))

    end = datetime.datetime.now()
    log('getData (' + str(int((end - start).total_seconds() * 1000)) + 'ms) ' + str(url))
    return json.loads(data)


def translate(text):
    return selfAddon.getLocalizedString(text)


def log(message, logType='Info'):
    if logType.lower() == 'debug' and settings.debugLog() == False:
        return
    xbmc.log(msg='['+str(plugin_name)+'] ('+logType+') ' +
             str(message), level=xbmc.LOGDEBUG)

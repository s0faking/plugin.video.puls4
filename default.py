#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmcaddon,base64,socket,datetime,time
from BeautifulSoup import BeautifulSoup
import os
import urlparse
import os.path
from xml.dom import Node;
from xml.dom import minidom;

version = "0.1.0"
plugin = "Puls 4 -" + version
author = "sofaking"

settings = xbmcaddon.Addon(id='plugin.video.puls4')
pluginhandle = int(sys.argv[1])
basepath = settings.getAddonInfo('path')
resourcespath = os.path.join(basepath,"resources")
mediapath =  os.path.join(resourcespath,"media")

base_url = "http://www.puls4.com"
show_url = "/video/sendungen"

logopath = os.path.join(mediapath,"logos")
bannerpath = os.path.join(mediapath,"banners")
backdroppath = os.path.join(mediapath,"backdrops")
defaultbackdrop = "http://goo.gl/XWnTc"
defaultbanner = os.path.join(bannerpath,"Default.png")
defaultlogo = os.path.join(logopath,"Default.png")

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
 

def parameters_string_to_dict(parameters):
        paramDict = {}
        if parameters:
            paramPairs = parameters[1:].split("&")
            for paramsPair in paramPairs:
                paramSplits = paramsPair.split('=')
                if (len(paramSplits)) == 2:
                    paramDict[paramSplits[0]] = paramSplits[1]
        return paramDict


def createListItem(name,banner,summary,runtime,backdrop,videourl,playable,folder):
        if backdrop == '':
               backdrop = defaultbackdrop
        if banner == '':
               banner = defaultbanner
        liz=xbmcgui.ListItem(cleanText(name), iconImage=banner, thumbnailImage=banner)
        liz.setInfo( type="Video", infoLabels={ "Title": cleanText(name) } )
        liz.setInfo( type="Video", infoLabels={ "Plot": cleanText(summary) } )
        liz.setInfo( type="Video", infoLabels={ "Plotoutline": cleanText(summary) } )
        liz.setInfo( type="Video", infoLabels={ "tvshowtitle": cleanText(name) } )
        liz.setInfo( type="Video", infoLabels={ "Runtime": runtime } )
        liz.setProperty('fanart_image',backdrop)
        liz.setProperty('IsPlayable', playable)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=videourl, listitem=liz, isFolder=folder)


def addFile(name,videourl,banner,summary,runtime,backdrop):
        if not mp4stream and not ".sdp" in videourl:
            videourl = convertToSD(videourl)
        videourl = convertToHD(videourl)
        createListItem(name,banner,summary,runtime,backdrop,videourl,'true',False)

def addDirectory(title,banner,backdrop,link,mode):
        parameters = {"link" : link,"title" : title,"banner" : banner,"backdrop" : backdrop, "mode" : mode}
        u = sys.argv[0] + '?' + urllib.urlencode(parameters)
        createListItem(title,banner,title,title,backdrop,u,'false',True)
    

def getCategories(url):
    html = opener.open("%s/video/sendungen" % url)
    html = html.read()
    suppn = BeautifulSoup(html)
    links = suppn.find('ul',{'id':'video-channel-small-slider'}).findAll('li')
    for link in links:
         anchor = link.find('a')
         if not "http://" in anchor['href']:
            link = "%s%s" % (base_url,anchor['href'])
            img = anchor.find('img')
            title = img['title']
            logo = img['src']
            addDirectory(title.encode('UTF-8'),logo,defaultbackdrop,link,'listShows')
         else:
            continue
         
    xbmcplugin.setContent(pluginhandle,'episodes')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.executebuiltin("Container.SetViewMode(503)")

def getMainMenu():
    addDirectory("Aktuell",defaultlogo,defaultbackdrop,"","getAktuelles")
    addDirectory("Sendungen",defaultlogo,defaultbackdrop,"","getSendungen")
    addDirectory("Top Videos",defaultlogo,defaultbackdrop,"","getTopVideos")
    addDirectory("Suchen",defaultlogo,defaultbackdrop,"","searchPhrase")
    xbmcplugin.setContent(pluginhandle,'episodes')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.executebuiltin("Container.SetViewMode(503)")
    xbmcplugin.setPluginFanart(int(sys.argv[1]), defaultbackdrop, color2='0xFFFF3300')

def cleanText(string):
    string = string.replace('\\n', '').replace("&#160;"," ").replace("&quot;","'").replace('&amp;', '&')
    return string

def playFile():
    player = xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER)
    player.play(playlist)
    if not player.isPlayingVideo():
        d = xbmcgui.Dialog()
        d.ok('VIDEO QUEUE EMPTY', 'The XBMC video queue is empty.','Add more links to video queue.')

def getTeaserBlock(html):
    suppn = BeautifulSoup(html)
    try:
      links = suppn.findAll('div',{'class':'bg_channelVideoTeaserMoreBlock'})
      for link in links:
         img = link.find('div',{'class':'bg_vidPic'}).find('img')['src']
         anchor = link.find('p').find('a')
         link = "%s%s" % (base_url,anchor['href'])
         title = anchor['title']
         addDirectory(title.encode('UTF-8'),img,defaultbackdrop,link,'listEpisode')
    except:
      pass

def getPageContent(url):
    try:
      url = urllib.unquote(url)
      html = opener.open(url)
      html = html.read()
    except:
      html = ""
    getMainTeaserBlock(html)
    getTeaserBlock(html)
    suppn = BeautifulSoup(html)
    links = suppn.findAll('div',{'class':re.compile(r'\bbg_append-bottom2\b')})
    for link in links:
       try:
         img = link.find('img')
         logo = img['src']
         anchor = link.find('p').find('a')
         fulllink = "%s%s" % (base_url,anchor['href'])
         title = anchor['title']
         type = link.find('a').find('div')
         if type != None:
             type = type.text
         addDirectory(title.encode('UTF-8'),logo,defaultbackdrop,fulllink,'listEpisode')
       except:
         pass
    getArchivShows(url)
    xbmcplugin.setContent(pluginhandle,'episodes')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.executebuiltin("Container.SetViewMode(503)")

def getMainTeaserBlock(html):
    suppn = BeautifulSoup(html)
    try:
      link = suppn.find('div',{'class':'bg_teaserContent'}).find('div')['onclick']
      fulllink = "%s%s" % (base_url, link.split("'")[1])
      logo = suppn.find('div',{'class':'bg_teaserContent'}).find('img')['src']
      title = suppn.find('div',{'class':'bg_teaserContent'}).find('h3').text
      addDirectory(title.encode('UTF-8'),logo,defaultbackdrop,link,'listEpisode')
    except:
      pass

def getVideo(url):
    url = urllib.unquote(url)
    if not "http://" in url:
       url = "%s%s" % (base_url,url) 
    html = opener.open(url)
    html = html.read()
    suppn = BeautifulSoup(html)
    jsVarReg = re.compile('p4_video_player.*?;')
    urlVarReg = re.compile('"url":".*?"')
    titleVarReg = re.compile('"ga_label":".*?"')
    imgVarReg = re.compile('http://files.puls4.com.*?"') 
    try:
       jsVars = jsVarReg.search(html).group()
       link = urlVarReg.search(jsVars).group().split('"')[3].replace('\/','/')
       title = titleVarReg.search(jsVars).group().split('"')[3]
       image = imgVarReg.search(jsVars).group().replace('"','')
       desc = suppn.find('div',{'id':'bg_fotoBig'}).find('div',{'class':'span-24'}).find('p').text.replace("&quot;"," | ")
       createListItem(title.encode('UTF-8'),image,desc.encode('UTF-8'),desc.encode('UTF-8'),defaultbackdrop,link,'true',False)     
    except:
       pass
    xbmcplugin.setContent(pluginhandle,'episodes')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.executebuiltin("Container.SetViewMode(503)")

def getArchivShows(url):
    url = urllib.unquote(url)
    url = "%s/archiv" % url
    html = opener.open(url)
    html = html.read()
    suppn = BeautifulSoup(html)
    blocks = suppn.findAll('div',{'class':'bg_entryPic'})
    for block in blocks:
      try:
       img = block.find('img',{'class':'bg_imgMargin'})
       title = img['title']
       image = img['src']
       anchor = block.find('a',{'class':'bg_relativeBlock'})
       link = anchor['href']
       type = anchor.find('span')
       if type != None:
          type = type.text
       else:
          type = ""
       addDirectory(title.encode('UTF-8'),image,defaultbackdrop,link,'listEpisode')
      except:
       pass

def titleToFilename(title,base_path):
    title = title.encode('ascii','ignore').replace(" ",".").replace("&quot;","").replace("?","").replace("!","")
    return os.path.join(base_path, "%s.jpg" % title)

def getHeadlineShows(url):
    url = urllib.unquote(url)
    html = opener.open(url)
    html = html.read()
    suppn = BeautifulSoup(html)
    blocks = suppn.findAll('div',{'class':'panel slide'})
    for block in blocks:
       anchor = block.find('a')
       image = anchor.find('img')['src']
       infos = block.find('div',{'class':'bg_videoTeaserLayerText'})
       title = infos.find('h3').text
       logo = infos.find('img')['src']
       link = anchor['href']
       addDirectory(title.encode('UTF-8'),image,defaultbackdrop,link,'listEpisode')
    xbmcplugin.setContent(pluginhandle,'episodes')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.executebuiltin("Container.SetViewMode(503)")

def getTopVideos(url):
    html = opener.open(url)
    html = html.read()
    suppn = BeautifulSoup(html)
    blocks = suppn.findAll('ul',{'class':'bg_slotList'})
    patn = re.compile(r'\d{2}.\d{2}.\d{4}')
    for block in blocks:
       lists = block.findAll('li')
       for list in lists:
          link = list.find('a')['href']
          showTitle = list.find('strong').text
          title = list.find('a')['title']
          for match in patn.findall(list.text):
               date = match
          title =  "[%s] %s | %s" % (date,showTitle,title)
          addDirectory(title.encode('UTF-8'),defaultlogo,defaultbackdrop,link,'listEpisode')
    xbmcplugin.setContent(pluginhandle,'episodes')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.executebuiltin("Container.SetViewMode(503)")

def searchVideos():
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed()):
      searchurl = "%s/video/keywordSearch?f[keyword]=%s&gsa_collection_id=videos"%(base_url,keyboard.getText())
      getSearchedShows(searchurl)
    else:
      addDirectory("Keine Ergebnisse",defaultlogo,defaultbackdrop,"","")
    xbmcplugin.setContent(pluginhandle,'episodes')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.executebuiltin("Container.SetViewMode(503)")


def getSearchedShows(url):
    url = urllib.unquote(url)
    html = opener.open(url)
    html = html.read()
    suppn = BeautifulSoup(html)
    blocks = suppn.findAll('div',{'class':'bg_entryPic'})
    for block in blocks:
      try:
       img = block.find('img',{'class':'bg_imgMargin'})
       title = img['title']
       image = img['src']
       anchor = block.find('a',{'class':'bg_relativeBlock'})
       link = anchor['href']
       type = anchor.find('span')
       if type != None:
          type = type.text
       else:
          type = ""
       addDirectory(title.encode('UTF-8'),image,defaultbackdrop,link,'listEpisode')
      except:
       pass

#Getting Parameters
params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
title=params.get('title')
link=params.get('link')
logo=params.get('logo')
category=params.get('category')
backdrop=params.get('backdrop')


if mode == 'getAktuelles':
    getHeadlineShows("%s%s"%(base_url,"/video/sendungen"))
if mode == 'listShows':
    getPageContent(link)
if mode == 'getTopVideos':
    getTopVideos("%s%s"%(base_url,"/video/sendungen"))
if mode == 'listEpisode':
    getVideo(link)
if mode == 'getSendungen':
    getCategories(base_url)
if mode == 'searchPhrase':
    searchVideos()
else:
    getMainMenu()

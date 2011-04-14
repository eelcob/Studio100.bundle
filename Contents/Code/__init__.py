# -*- coding: utf-8 -*-
import re

###################################################################################################

PLUGIN_TITLE = 'Studio 100'
BASE_URL     = 'http://www.studio100tv.be'
OVERVIEW_RSS = '%s/rss' % BASE_URL
VIDEO_FILE   = '%s/videofile/%%s' % BASE_URL
PLAYER       = 'http://www.plexapp.com/player/player.php?clip=%s'

ART_DEFAULT  = 'art-default.jpg'
ICON_DEFAULT = 'icon-default.png'

###################################################################################################
def Start():
  Plugin.AddPrefixHandler('/video/studio100', MainMenu, PLUGIN_TITLE, ICON_DEFAULT, ART_DEFAULT)
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')

  MediaContainer.title1    = PLUGIN_TITLE
  MediaContainer.viewGroup = 'List'
  MediaContainer.userAgent = ''
  MediaContainer.art       = R(ART_DEFAULT)

  HTTP.CacheTime = CACHE_1DAY
  HTTP.Headers['User-agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.16'

###################################################################################################
def MainMenu():
  dir = MediaContainer()

  for f in HTML.ElementFromURL(OVERVIEW_RSS, errors='ignore').xpath('//h2[text()="Kanalen/Karakters"]/following-sibling::ul/li'):
    title = f.xpath('./strong')[0].text.strip()
    url = f.xpath('./a')[0].get('href')
    dir.Append(Function(DirectoryItem(TVShow, title=title, thumb=R(ICON_DEFAULT)), url=url))

  if len(dir) == 0:
    return MessageContainer('Geen programma\'s', 'Er werden geen programma\'s gevonden')
  else:
    return dir

####################################################################################################
def TVShow(sender, url):
  dir = MediaContainer(title2=sender.itemTitle)

  for e in XML.ElementFromURL(url, errors='ignore').xpath('/rss/channel/item'):
    title = e.xpath('./title')[0].text.strip()
    link = e.xpath('./link')[0].text.split('?', 1)[0].rsplit('/', 1)[1]
    video = VIDEO_FILE % link
    thumb = e.xpath('./enclosure')[0].text
    pubDate = e.xpath('./pubDate')[0].text
    date = Datetime.ParseDate(pubDate).strftime('%d/%m/%Y')
    dir.Append(WebVideoItem(PLAYER % String.Quote(video, usePlus=False), title=title, thumb=Function(GetThumb, url=thumb), infoLabel=date))

  if len(dir) == 0:
    return MessageContainer('Geen afleveringen', 'Er werden geen afleveringen gevonden')
  else:
    return dir

####################################################################################################
def GetThumb(url):
  try:
    data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON_DEFAULT))

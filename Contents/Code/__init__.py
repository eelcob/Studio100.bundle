# -*- coding: utf-8 -*-
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
import re

###################################################################################################

PLUGIN_TITLE               = 'Studio 100'
PLUGIN_PREFIX              = '/video/studio100'
BASE_URL                   = 'http://www.studio100tv.be'
OVERVIEW_RSS               = '%s/rss' % BASE_URL
VIDEO_FILE                 = '%s/videofile/%%s' % BASE_URL
PLAYER                     = 'http://www.plexapp.com/player/player.php?clip=%s'

# Art and icons
ART_DEFAULT                = 'art-default.png'
ICON_DEFAULT               = 'icon-default.png'

###################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE, ICON_DEFAULT, ART_DEFAULT)

  Plugin.AddViewGroup('Category', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')

  # Set the default MediaContainer attributes
  MediaContainer.title1    = PLUGIN_TITLE
  MediaContainer.viewGroup = 'Category'
  MediaContainer.userAgent = ''
  MediaContainer.art       = R(ART_DEFAULT)

  # Set the default cache time
  HTTP.SetCacheTime(CACHE_1DAY)
  HTTP.SetHeader('User-agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7')

###################################################################################################

def MainMenu():
  dir = MediaContainer()
  feeds = XML.ElementFromURL(OVERVIEW_RSS, isHTML=True, errors='ignore').xpath('/html/body//h2[text()="Kanalen/Karakters"]/following-sibling::ul/li')

  for f in feeds:
    title = f.xpath('./strong')[0].text.strip()
    url = f.xpath('./a')[0].get('href')
    dir.Append(Function(DirectoryItem(TVShow, title=title, thumb=R(ICON_DEFAULT)), url=url))

  return dir

####################################################################################################

def TVShow(sender, url):
  dir = MediaContainer(title2=sender.itemTitle)
  episodes = XML.ElementFromURL(url, errors='ignore').xpath('/rss/channel/item')

  for e in episodes:
    title = e.xpath('./title')[0].text.strip()
    link = e.xpath('./link')[0].text.split('?', 1)[0].rsplit('/', 1)[1]
    video = VIDEO_FILE % link
    thumb = e.xpath('./enclosure')[0].text
#   thumb = re.sub('([0-9]{1,})x([0-9]{1,})$', '640x360', thumb, 1)
    pubDate = e.xpath('./pubDate')[0].text
    date = Datetime.ParseDate(pubDate).strftime('%d/%m/%Y')
    dir.Append(WebVideoItem(PLAYER % String.Quote(video, usePlus=False), title=title, thumb=Function(GetThumb, url=thumb), infoLabel=date))

  return dir

####################################################################################################

def GetThumb(url):
  data = HTTP.Request(url, cacheTime=CACHE_1MONTH)
  if data:
    return DataObject(data, 'image/jpeg')
  else:
    return Redirect(R(ICON_DEFAULT))

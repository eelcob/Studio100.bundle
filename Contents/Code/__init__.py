# -*- coding: utf-8 -*-
###################################################################################################
NAME		 = 'Studio 100'
BASE_URL     = 'http://www.studio100tv.be'
OVERVIEW_RSS = '%s/rss' % BASE_URL
SEARCH_URL	 = '%s/zoek/%%s' % BASE_URL

ART			 = 'art-default.jpg'
ICON		 = 'icon-default.png'
ICON_SEARCH	 = 'search.png'

###################################################################################################
def Start():
	Plugin.AddPrefixHandler('/video/studio100', MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')

	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)
	
	VideoClipObject.thumb = R(ICON)
	
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:13.0) Gecko/20100101 Firefox/13.0.1'

###################################################################################################
def MainMenu():
	oc = ObjectContainer()
	
	for f in HTML.ElementFromURL(OVERVIEW_RSS, errors='ignore').xpath('//h2[text()="Kanalen/Karakters"]/following-sibling::ul/li'):
		title = f.xpath('./strong')[0].text.strip()
		url = f.xpath('./a')[0].get('href')
		oc.add(DirectoryObject(key = Callback(Episodes, url=url, title=title), title=title))
	
	if len(oc) == 0:
		oc	= ObjectContainer(header = "Geen Programmas", message = "Er werden geen programmas gevonden")
	
	oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.studio100", title='Zoeken', prompt='Zoeken', thumb=R(ICON_SEARCH)))

	
	return oc

####################################################################################################
def Episodes(url, title):

	oc = ObjectContainer(title2=title)
	
	for e in XML.ElementFromURL(url, errors='ignore').xpath('/rss/channel/item'):
		title = e.xpath('./title')[0].text.strip()	
		link = e.xpath('./link')[0].text.split('?', 1)[0]
			
		try:
			thumb = e.xpath('./enclosure')[0].text
		except:
			thumb = None
		try:
			pubDate = e.xpath('./pubDate')[0].text
			date = Datetime.ParseDate(pubDate)
		except:
			date = None
		
		oc.add(VideoClipObject(
				url = link,
				title = title,
				originally_available_at = date,
				thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
		))

	if len(oc) == 0:
		oc	= ObjectContainer(header = "Geen Afleveringen", message = "Er werden geen afleveringen gevonden")
	return oc
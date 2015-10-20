# -*- coding: utf-8 -*-
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _, SetIPTVPlayerLastHostError
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass, CDisplayListItem, RetHost, CUrlItem, ArticleContent
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, CSearchHistoryHelper, remove_html_markup, GetLogoDir, GetCookieDir, byteify
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common, CParsingHelper
import Plugins.Extensions.IPTVPlayer.libs.urlparser as urlparser
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.utils import clean_html
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
###################################################

###################################################
# FOREIGN import
###################################################
import re
import urllib
import base64
try:    import json
except: import simplejson as json
from Components.config import config, ConfigSelection, ConfigYesNo, ConfigText, getConfigListEntry
###################################################


###################################################
# E2 GUI COMMPONENTS 
###################################################
from Plugins.Extensions.IPTVPlayer.components.asynccall import MainSessionWrapper
from Screens.MessageBox import MessageBox
###################################################

###################################################
# Config options for HOST
###################################################
#config.plugins.iptvplayer.alltubetv_premium  = ConfigYesNo(default = False)
#config.plugins.iptvplayer.alltubetv_login    = ConfigText(default = "", fixed_size = False)
#config.plugins.iptvplayer.alltubetv_password = ConfigText(default = "", fixed_size = False)

def GetConfigList():
    optionList = []
    #if config.plugins.iptvplayer.alltubetv_premium.value:
    #    optionList.append(getConfigListEntry("  alltubetv login:", config.plugins.iptvplayer.alltubetv_login))
    #    optionList.append(getConfigListEntry("  alltubetv hasło:", config.plugins.iptvplayer.alltubetv_password))
    return optionList
###################################################


def gettytul():
    return 'http://filmovita.com/'

class Filmovita(CBaseHostClass):
    MAIN_URL    = 'http://filmovita.com/'
    SRCH_URL    = MAIN_URL + 'szukaj'
    DEFAULT_ICON_URL = 'http://skini.filmovita.com/grafika/logo.png'
    
    MAIN_CAT_TAB = [{'category':'list_movies',        'title': _('Main'),          'url':MAIN_URL, 'icon':DEFAULT_ICON_URL},
                    {'category':'genres_movies',      'title': _('Categories'),    'url':MAIN_URL, 'icon':DEFAULT_ICON_URL},
                    #{'category':'search',             'title': _('Search'), 'search_item':True},
                    #{'category':'search_history',     'title': _('Search history')} 
                   ]
 
    def __init__(self):
        CBaseHostClass.__init__(self, {'history':'Filmovita', 'cookie':'filmovita.cookie'})
        self.filterCache = {}
        self.seriesCache = {}
        self.seriesLetters = []
        
    def _getFullUrl(self, url):
        if 0 < len(url) and not url.startswith('http'):
            url =  self.MAIN_URL + url
        if not self.MAIN_URL.startswith('https://'):
            url = url.replace('https://', 'http://')
        return url

    def listsTab(self, tab, cItem, type='dir'):
        printDBG("Filmovita.listsTab")
        for item in tab:
            params = dict(cItem)
            params.update(item)
            params['name']  = 'category'
            if type == 'dir':
                self.addDir(params)
            else: self.addVideo(params)
        
    def listGenres(self, cItem, category):
        printDBG("Filmovita.listGenres")
        sts, data = self.cm.getPage(cItem['url'])
        if not sts: return 
        data = self.cm.ph.getDataBeetwenMarkers(data, '<ul class="sub-menu">', '</ul>', False)[1]
        data = re.compile('<a[^>]*?href="([^"]+?)"[^>]*?>([^<]+?)</a>').findall(data)
        tab = []
        for item in data:
            tab.append({'title':item[1], 'url':item[0]})
        defItem = dict(cItem)
        defItem['category'] = category
        self.listsTab(tab, defItem)
        
    def listMovies(self, cItem):
        printDBG("Filmovita.listMovies")
        
        url = cItem['url']
        page = cItem.get('page', 1)
        if page > 1:
            url += 'page/%d/' % page
            
        sts, data = self.cm.getPage(url)
        if not sts: return 
        
        if ('/page/%d/' % (page + 1)) in data:
            nextPage = True
        else: nextPage = False
        
        data = self.cm.ph.getDataBeetwenMarkers(data, '<article id=', '<div class="section clearfix">', True)[1]
        data = data.split('</article>')
        if len(data): del data[-1]
        
        for item in data:
            tmp = item.split('</h1>')
            url    = self.cm.ph.getSearchGroups(item, 'href="([^"]+?)"')[0]
            icon   = self.cm.ph.getSearchGroups(item, 'src="([^"]+?)"')[0]
            title  = tmp[0]
            desc   = tmp[1]
            params = dict(cItem)
            params.update( {'title': self.cleanHtmlStr( title ), 'url':self._getFullUrl(url), 'desc': self.cleanHtmlStr( desc ), 'icon':self._getFullUrl(icon)} )
            self.addVideo(params)
        
        if nextPage:
            params = dict(cItem)
            params.update( {'title':_('Next page'), 'page':page+1} )
            self.addDir(params)
        
    def listSearchResult(self, cItem, searchPattern, searchType):
        pass
        
    def getLinksForVideo(self, cItem):
        printDBG("Filmovita.getLinksForVideo [%s]" % cItem)
        urlTab = []
        
        sts, mainData = self.cm.getPage(cItem['url'])
        if not sts: return urlTab
        
        tmp = self.cm.ph.getDataBeetwenMarkers(mainData, '</iframe>', '</div>', False)[1]
        linksUrl = self.cm.ph.getSearchGroups(tmp, 'src="([^"]+?)"')[0]
        if 1 == self.up.checkHostSupport(linksUrl): 
            if 'videomega.tv/validatehash.php?' in linksUrl:
                sts, data = self.cm.getPage(linksUrl, {'header':{'Referer':cItem['url'], 'User-Agent':'Mozilla/5.0'}})
                if sts:
                    data = self.cm.ph.getSearchGroups(data, 'ref="([^"]+?)"')[0]
                    linksUrl = 'http://videomega.tv/view.php?ref={0}&width=700&height=460&val=1'.format(data)
                else:
                    linksUrl = ''
            if linksUrl != '':
                urlTab.append({'name':self.up.getHostName(linksUrl), 'url':linksUrl, 'need_resolve':1})
        
        linksUrl = self.cm.ph.getSearchGroups(mainData, 'src="(http[^"]+?\/links\/[^"]+?)"')[0] 
        printDBG("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR>>>>>>>>> " + linksUrl)
        if linksUrl != '':
            sts, data = self.cm.getPage(linksUrl)
            if not sts: return urlTab
            data = self.cm.ph.getDataBeetwenMarkers(data, '<body>', '</body>', False)[1]
            data = re.compile('<a[^>]*?href="([^"]+?)"[^>]*?>([^<]+?)</a>').findall(data)
            for item in data:
                name = item[1].split('servisu ')[-1]
                url  = item[0]
                #name = self.up.getHostName(url)
                urlTab.append({'name':name, 'url':url, 'need_resolve':1})
        
        return urlTab
        
    def getVideoLinks(self, baseUrl):
        printDBG("Filmovita.getVideoLinks [%s]" % baseUrl)
        urlTab = []
        
        if 'filmovita.com' in baseUrl:
            sts, data = self.cm.getPage(baseUrl)
            if not sts: 
                return []
            enigmav = self.cm.ph.getSearchGroups(data, '''data-enigmav=['"]([^'^"]+?)['"]''')[0]
            enigmav = enigmav.replace('-', '\\u00').replace('=', '\\u')
            try:
                data = byteify( json.loads('{"data":"%s"}' % enigmav) )['data']
                baseUrl = self.cm.ph.getSearchGroups(data, 'src="([^"]+?)"', 1, True)[0] 
            except:
                printExc()
                return []
        
        urlTab = self.up.getVideoLinkExt(baseUrl)
        return urlTab
        
    def getFavouriteData(self, cItem):
        return cItem['url']
        
    def getLinksForFavourite(self, fav_data):
        return self.getLinksForVideo({'url':fav_data})

    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)

        name     = self.currItem.get("name", '')
        category = self.currItem.get("category", '')
        printDBG( "handleService: |||||||||||||||||||||||||||||||||||| name[%s], category[%s] " % (name, category) )
        self.currList = []
        
    #MAIN MENU
        if name == None:
            self.listsTab(self.MAIN_CAT_TAB, {'name':'category'})
    #MOVIES
        elif category == 'genres_movies':
            self.listGenres(self.currItem, 'list_movies')
        elif category == 'list_movies':
            self.listMovies(self.currItem)
    #SEARCH
        elif category in ["search", "search_next_page"]:
            cItem = dict(self.currItem)
            cItem.update({'search_item':False, 'name':'category'}) 
            self.listSearchResult(cItem, searchPattern, searchType)
    #HISTORIA SEARCH
        elif category == "search_history":
            self.listsHistory({'name':'history', 'category': 'search'}, 'desc', _("Type: "))
        else:
            printExc()
        
        CBaseHostClass.endHandleService(self, index, refresh)
class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, Filmovita(), True, [CDisplayListItem.TYPE_VIDEO, CDisplayListItem.TYPE_AUDIO])

    def getLogoPath(self):
        return RetHost(RetHost.OK, value = [GetLogoDir('filmovitalogo.png')])
    
    def getLinksForVideo(self, Index = 0, selItem = None):
        retCode = RetHost.ERROR
        retlist = []
        if not self.isValidIndex(Index): return RetHost(retCode, value=retlist)
        
        urlList = self.host.getLinksForVideo(self.host.currList[Index])
        for item in urlList:
            retlist.append(CUrlItem(item["name"], item["url"], item['need_resolve']))

        return RetHost(RetHost.OK, value = retlist)
    # end getLinksForVideo
    
    def getResolvedURL(self, url):
        # resolve url to get direct url to video file
        retlist = []
        urlList = self.host.getVideoLinks(url)
        for item in urlList:
            need_resolve = 0
            retlist.append(CUrlItem(item["name"], item["url"], need_resolve))

        return RetHost(RetHost.OK, value = retlist)
    
    def converItem(self, cItem):
        hostList = []
        searchTypesOptions = [] # ustawione alfabetycznie
        searchTypesOptions.append((_("Movies"), "movies"))
        searchTypesOptions.append((_("Series"), "series"))
    
        hostLinks = []
        type = CDisplayListItem.TYPE_UNKNOWN
        possibleTypesOfSearch = None

        if 'category' == cItem['type']:
            if cItem.get('search_item', False):
                type = CDisplayListItem.TYPE_SEARCH
                possibleTypesOfSearch = searchTypesOptions
            else:
                type = CDisplayListItem.TYPE_CATEGORY
        elif cItem['type'] == 'video':
            type = CDisplayListItem.TYPE_VIDEO
        elif 'more' == cItem['type']:
            type = CDisplayListItem.TYPE_MORE
        elif 'audio' == cItem['type']:
            type = CDisplayListItem.TYPE_AUDIO
            
        if type in [CDisplayListItem.TYPE_AUDIO, CDisplayListItem.TYPE_VIDEO]:
            url = cItem.get('url', '')
            if '' != url:
                hostLinks.append(CUrlItem("Link", url, 1))
            
        title       =  cItem.get('title', '')
        description =  cItem.get('desc', '')
        icon        =  cItem.get('icon', '')
        
        return CDisplayListItem(name = title,
                                    description = description,
                                    type = type,
                                    urlItems = hostLinks,
                                    urlSeparateRequest = 1,
                                    iconimage = icon,
                                    possibleTypesOfSearch = possibleTypesOfSearch)
    # end converItem

    def getSearchItemInx(self):
        try:
            list = self.host.getCurrList()
            for i in range( len(list) ):
                if list[i]['category'] == 'search':
                    return i
        except:
            printDBG('getSearchItemInx EXCEPTION')
            return -1

    def setSearchPattern(self):
        try:
            list = self.host.getCurrList()
            if 'history' == list[self.currIndex]['name']:
                pattern = list[self.currIndex]['title']
                search_type = list[self.currIndex]['search_type']
                self.host.history.addHistoryItem( pattern, search_type)
                self.searchPattern = pattern
                self.searchType = search_type
        except:
            printDBG('setSearchPattern EXCEPTION')
            self.searchPattern = ''
            self.searchType = ''
        return

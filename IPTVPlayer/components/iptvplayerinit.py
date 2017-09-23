# -*- coding: utf-8 -*-

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, DownloadFile, eConnectCallback
###################################################
# FOREIGN import
###################################################
from Tools.BoundFunction import boundFunction
from enigma import eConsoleAppContainer
from Tools.Directories import resolveFilename, fileExists, SCOPE_PLUGINS
from Components.config import config, configfile
from Components.Language import language
import gettext
import os, sys
import threading
import time
###################################################

###################################################
# Globals
###################################################
gInitIPTVPlayer = True # is initialization of IPTVPlayer is needed
PluginLanguageDomain = "IPTVPlayer"
PluginLanguagePath = "Extensions/IPTVPlayer/locale"
gSetIPTVPlayerLastHostError = ""
gIPTVPlayerNotificationList = None

###################################################
def localeInit():
    lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
    os.environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
    printDBG(PluginLanguageDomain + " set language to " + lang)
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))

def TranslateTXT(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t

localeInit()
language.addCallback(localeInit)

def IPTVPlayerNeedInit(value=None):
    global gInitIPTVPlayer
    if value in [True, False]: gInitIPTVPlayer = value
    return gInitIPTVPlayer
    
def SetIPTVPlayerLastHostError(value=""):
    global gSetIPTVPlayerLastHostError
    gSetIPTVPlayerLastHostError = value

def GetIPTVPlayerLastHostError(clear=True):
    global gSetIPTVPlayerLastHostError
    tmp = gSetIPTVPlayerLastHostError
    if clear: gSetIPTVPlayerLastHostError = ""
    return tmp

class IPTVPlayerNotification():
    def __init__(self, title, message, type, timeout):
        self.title = str(title)
        self.message = str(message)
        self.type = str(type) # "info", "error", "warning"
        self.timeout = int(timeout)
        
    def __eq__(self, a):
        return not self.__ne__(a)
    
    def __ne__(self, a):
        if self.title != a.title or \
           self.type != a.type or \
           self.message != a.message or \
           self.timeout != a.timeout:
            return True
        return False

class IPTVPlayerNotificationList(object):
    
    def __init__(self):
        self.notificationsList = []
        self.mainLock = threading.Lock()
        # this flag will be checked with mutex taken 
        # to less lock check
        self.empty = True
        
    def clearQueue(self):
        with self.mainLock:
            self.notificationsList = []
            self.empty = True
        
    def isEmpty(self):
        try:
            if self.empty:
                return True
        except Exception:
            pass
        return False
    
    def push(self, message, type="message", timeout=5): #, allowDuplicates=True
        ret = False
        with self.mainLock:
            try:
                notification = IPTVPlayerNotification('IPTVPlayer', message, type, timeout)
                self.notificationsList.append(notification)
                self.empty = False
                ret = True
            except Exception:
                print(str(e))
        return ret

    def pop(self, popAllSameNotificationsAtOnce=True):
        notification = None
        with self.mainLock:
            try:
                notification = self.notificationsList.pop()
                if popAllSameNotificationsAtOnce:
                    newList = []
                    for item in self.notificationsList:
                        if item != notification:
                            newList.append(item)
                    self.notificationsList = newList
            except Exception as e:
                print(str(e))
                
            if 0 == len(self.notificationsList):
                self.empty = True
        return notification

gIPTVPlayerNotificationList = IPTVPlayerNotificationList()
def GetIPTVNotify():
    global gIPTVPlayerNotificationList
    return gIPTVPlayerNotificationList
    
class IPTVPlayerSleep(object):
    
    def __init__(self):
        self.mainLock = threading.Lock()
        self.timeout = 0
        self.startTimestamp = 0
        
    def Sleep(self, timeout):
        tmp = float(timeout)
        with self.mainLock:
            self.timeout = timeout
            self.startTimestamp = time.time()
        time.sleep(self.timeout)
        
    def getTimeout(self):
        ret = 0
        with self.mainLock:
            if self.timeout != 0:
                ret = int(self.timeout - (time.time() - self.startTimestamp))
                if ret <= 0:
                    self.timeout = 0
                    ret = 0
        return ret
    
gIPTVPlayerSleep = IPTVPlayerSleep()
def GetIPTVSleep():
    global gIPTVPlayerSleep
    return gIPTVPlayerSleep
        
        

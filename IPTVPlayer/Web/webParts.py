# -*- coding: utf-8 -*-
#### Local imports
from __init__ import _
import settings
from Plugins.Extensions.IPTVPlayer.iptvdm.iptvdh import DMHelper
from Plugins.Extensions.IPTVPlayer.version import IPTV_VERSION
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import GetHostsList, IsHostEnabled, SaveHostsOrderList, SortHostsList, GetLogoDir, GetHostsOrderList, getDebugMode, formatBytes
#### e2 imports
from Components.config import config

#### system imports
import os

########################################################
def formSUBMITvalue( inputHiddenObjects, caption, input_def = '' ):
	retTxt = '\n<form method="GET">'
	for inputObj in inputHiddenObjects:
		retTxt += '<input type="hidden" name="%s" value="%s">' % (inputObj[0], inputObj[1])
	retTxt += '<input type="submit" value="%s" %s></form>\n' % (caption, input_def)
	return retTxt
########################################################
def formGET( radioList ):
	radioList = radioList.strip()
	if radioList.endswith('</br>'):
		radioList = radioList[:-5]
	elif radioList.endswith('<br>'):
		radioList = radioList[:-4]
	if radioList.startswith('ERROR:'):
		return '\n<a><font color="#FFE4C4">%s</font></a>' % (radioList[6:])
	elif radioList.count('<input type="radio"') == 1:
		return '%s' % (radioList)
	else:
		return '\n<form method="GET">\n%s\n<input type="submit" value="%s"></form>\n' % (radioList, _('Save'))
########################################################
def removeSpecialChars(text):
    text = text.replace('\n', ' ').replace('\r', '').replace('\t', ' ').replace('"', "'").replace('  ', " ").strip()
    text = text.replace('&oacute;', 'ó').replace('&Oacute;', 'Ó')
    text = text.replace('&quot;', "'").replace('&#34;', "'").replace('&nbsp;', ' ').replace('&#160;', " ").replace('[/br]', "<br>")
    return text.strip()
########################################################
def IncludeHEADER(extraMetas = ''):
	tempText = """
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<meta http-equiv="cache-control" content="no-cache" />
	<meta http-equiv="pragma" content="no-cache" />
	<meta http-equiv="expires" content="0">
	%s
	<title>IPTVPlayer %s</title>
  <style>
    body {margin:0;}

    .topbar {overflow: hidden; background-color: #333; position: fixed; top: 0; width: 100%%; }
    .topbar a {float: left; display: block; color: #f2f2f2; text-align: center; padding: 14px 16px; text-decoration: none; font-size: 17px; }
    .bottombar {overflow: hidden; background-color: #333; position: fixed; bottom: 0; width: 100%%; }
    .bottombar a {float: left; display: block; color: #f2f2f2; text-align: center; padding: 14px 16px; text-decoration: none; font-size: 12px; }

    .main {padding: 16px; margin-top: 40px; margin-bottom: 40px; }
    p.DMlist {border: 2px solid red; border-radius: 5px; }

    .lnkbtn{display: block;  background-color: lightgrey; border: 1px solid black; text-align: center; text-decoration: none; padding: 5px 0px 5px 0px;color: black;font-size: 13px;}
    .lnkbtn:hover{background-color: #aaa;}
    .lnkbtn:visited{color: black;}



  </style>
</head>
""" % (extraMetas, IPTV_VERSION)
	return tempText
	
########################################################
def IncludeMENU():
	if settings.isActiveHostInitiated():
		tempText = """
  <div class="topbar">
    <a href="http://iptvplayer.vline.pl/" target="_blank"> <img border="0" alt="IPTVPlayer" src="./icons/iptvlogo.png" width="60" height="24"></a>
    <a href="/iptvplayer/usehost" >%s</a>
    <a href="/iptvplayer/downloader" >%s</a>
    <a href="/iptvplayer/logs" >%s</a>
  </div>
  <div class="bottombar">
    <a href="https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2/commits/master" target="_blank" >IPTVPlayer %s: <b><font color="#A9F5F2">%s</font></b></a>
    <a>, %s: <b>%s</b></a/>
  </div>
""" % ( _('Active host'), _('Download manager'), _('Logs'), _('version'), IPTV_VERSION, _('Web interface version'), settings.WebInterfaceVersion )
	else:
		tempText = """
  <div class="topbar">
    <a href="http://iptvplayer.vline.pl/" target="_blank"> <img border="0" alt="IPTVPlayer" src="./icons/iptvlogo.png" width="60" height="24"></a>
    <a href="/iptvplayer/" >%s</a>
    <a href="/iptvplayer/hosts" ">%s</a>
    <a href="/iptvplayer/downloader" >%s</a>
    <a href="/iptvplayer/settings" >%s</a>
    <a href="/iptvplayer/logs" >%s</a>
  </div>
  <div class="bottombar">
    <a href="https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2/commits/master" target="_blank" >IPTVPlayer %s: <b><font color="#A9F5F2">%s</font></b></a>
    <a>, %s: <b>%s</b></a/>
  </div>
""" % ( _('Information'), _('Selected hosts'), _('Download manager'), _('Settings'), _('Logs'), _('version'), IPTV_VERSION, _('Web interface version'), settings.WebInterfaceVersion )

	return tempText

########################################################
class Body():
	def __init__(self):
		pass
		
	def StartPageContent(self):
		tempText = '<body bgcolor=\"#666666\" text=\"#FFFFFF\">\n'
		tempText += '<form method="POST" action="--WEBBOT-SELF--">\n'
		tempText += IncludeMENU()
		tempText += '<div class="main">\n'
		tempText += '<p align="center"><b>%s</b></p>' % _('<font color="#FE642E">REMEMBER:</font></b> IPTVPlayer <b>IS ONLY</b> specialized Web browser. It does <b>NOT</b> host any materials!!!</font>')
		tempText += '</div></body>\n'
		return tempText
	########################################################
	def logsPageContent(self, status = ''):
		DBGFileName = ''
		tempText = '<body bgcolor=\"#666666\" text=\"#FFFFFF\">\n'
		tempText += IncludeMENU()
		tempText += '<div class="main">\n'
		if status ==  'deleteLogOK':
			tempText += '<p align="center"><b><font color="#ccE4C4">%s</font></b></p>' % _('Debug file has been deleted')
		elif status ==  'deleteLogError':
			tempText += '<p align="center"><b><font color="#FFE4C4">%s</font></b></p>' % _('Error during deletion of the debug file.')
		elif status ==  'deleteLogNO':
			tempText += '<p align="center"><b><font color="#ccE4C4">%s</font></b></p>' % _('Debug file does not exist - nothing to delete')
		elif getDebugMode() not in ['console','debugfile']:
			tempText += '<p align="center"><b><font color="#FFE4C4">%s</font></b></p>' % _('Debug option is disabled - nothing to display')
		elif getDebugMode() == 'console':
			tempText += '<p align="center"><b><font color="#FFE4C4">%s</font></b></p>' % _('Debug option set to console - nothing to display')
		elif os.path.exists('/hdd/iptv.dbg'):
			DBGFileName = '/hdd/iptv.dbg'
		elif os.path.exists('/tmp/iptv.dbg'):
			DBGFileName = '/tmp/iptv.dbg'
		else:
			tempText += '<p align="center"><b><font color="#FFE4C4">%s</font></b></p>' % _('Debug option set to debugfile, but file does not exist - nothing to display')
		if DBGFileName != '':
			tempText += '<table border="0"><td>%s</td>' % formSUBMITvalue([('cmd', 'getLog')], _("Download log file"))
			try:
				if os.path.getsize(DBGFileName) > 100000:
					LogDescr = _('%s file is %d MB in size. Last %d lines are:') % (DBGFileName, os.path.getsize(DBGFileName) >> 20, settings.MaxLogLinesToShow)
					tempText += '<td>%s</td>' % formSUBMITvalue([('cmd', 'deleteLog')], _("Delete log file"))
				else:
					LogDescr = _('%s file is %d KB in size. Last %d lines are:') % (DBGFileName, os.path.getsize(DBGFileName) / 1024 , settings.MaxLogLinesToShow)
			except:
				LogDescr = _('Last %d lines of the %s file are:') % (settings.MaxLogLinesToShow, DBGFileName)
			tempText += '</table>\n'
			tempText += '<p><b><font color="#FFE4C4">%s</font></b></p>' % LogDescr
			tempText += '<table border="1: style="width:520px; table-layout: fixed"><td><tt><p><font size="2">'
			logText=''
			with open(DBGFileName, 'r') as f:
				last_bit = f.readlines()[-settings.MaxLogLinesToShow:]
				for L in last_bit:
					if L.find('IPTVPlayerWidget.__init__') > 0:
						LogText = ''
					logText += L + '<br>\n'
			tempText += logText + '</font></p></tt></td></table>'
			tempText += formSUBMITvalue([('cmd', 'getLog')], _("Download log file"))
		tempText += '</div></body>\n'
		return tempText

	########################################################
	def getHostLogo(self, hostName):
		try:
			_temp = __import__('Plugins.Extensions.IPTVPlayer.hosts.host' + hostName, globals(), locals(), ['IPTVHost'], -1)
			logo = _temp.IPTVHost().getLogoPath().value[0]
			_temp = None
			if os.path.exists(logo):
				logo = '<img border="0" alt="hostLogo" src="./icons/logos/%s" width="120" height="40">' % logo.replace(GetLogoDir(),'')
			else:
				raise Exception
		except Exception:
			if os.path.exists(GetLogoDir('%slogo.png' % hostName)):
				logo = '<img border="0" alt="hostLogo" src="./icons/logos/%slogo.png" width="120" height="40">' % hostName
			else:
				logo = ""
		return logo
	########################################################
	def getCFGType(self, option):
		cfgtype = ''
		try:
			CFGElements = option.doException()
		except Exception, e:
			cfgtype = str(e).split("'")[1]
		return cfgtype
	########################################################
	def buildSettingsTable(self, List1, List2, exclList, direction):  #direction = '1>2'|'2>1'
		if direction == '2>1':
			tmpList = List1
			List1 = List2
			List2 = tmpList
			tmpList = None
		tableCFG = []
		for itemL1 in List1:
			if itemL1[0] in exclList or itemL1[0] in settings.excludedCFGs :
				continue
			for itemL2 in List2:
				if itemL2[1] == itemL1[1]:
					if direction == '1>2':
						confKey = itemL1
						ConfName = itemL1[0]
						ConfDesc = itemL2[0]
					elif direction == '2>1':
						confKey = itemL2
						ConfName = itemL2[0]
						ConfDesc = itemL1[0]
					CFGtype = self.getCFGType(itemL1[1])
					#print ConfName, '=' , CFGtype
					if CFGtype in ['ConfigYesNo','ConfigOnOff', 'ConfigEnableDisable', 'ConfigBoolean']:
						if int(confKey[1].getValue()) == 0 :
							CFGElements =  '<input type="radio" name="cmd" value="ON:%s">%s</input>' % (ConfName, _('Yes'))
							CFGElements += '<input type="radio" name="cmd" value="OFF:%s" checked="checked">%s</input>' % (ConfName, _('No'))
						else:
							CFGElements =  '<input type="radio" name="cmd" value="ON:%s" checked="checked">%s</input>' % (ConfName, _('Yes'))
							CFGElements += '<input type="radio" name="cmd" value="OFF:%s">%s</input>' % (ConfName, _('No'))
					elif CFGtype in ['ConfigInteger']:
						CFGElements = '<input type="number" name="%s" value="%d" />' %('INT:' + ConfName , int(confKey[1].getValue()))
					else:
						try:
							CFGElements = confKey[1].getHTML('CFG:' + ConfName)
						except Exception, e:
							CFGElements = 'ERROR:%s' % str(e)
					tableCFG.append([ConfName, ConfDesc, CFGElements])
		return tableCFG
	########################################################
	def settingsPageContent(self):
		usedCFG = []
		tempText = '<body bgcolor=\"#666666\" text=\"#FFFFFF\">\n<div class="main">\n'
		tempText += IncludeMENU()
		#build hosts settings section
		hostsCFG = '<table width="850px" border="1"><tbody>\n'
		hostsCFG += '<tr><td align="center" colspan="3"><p><font size="5" color="#9FF781">%s</font></p></td></tr>\n' % _('Hosts settings')
		for hostName in SortHostsList(GetHostsList()):
			# column 1 containing logo and link if available
			try:
				_temp = __import__('Plugins.Extensions.IPTVPlayer.hosts.host' + hostName, globals(), locals(), ['gettytul'], -1)
				title = _temp.gettytul()
			except Exception:
				continue # we do NOT use broken hosts!!!
			usedCFG.append("host%s" % hostName )
			
			logo = self.getHostLogo(hostName)
			if logo == "": logo = title
	
			if title[:4] == 'http':
				hostNameWithURLandLOGO = '<a href="%s" target="_blank">%s</a>' % (title, logo)
			else:
				hostNameWithURLandLOGO = '<a>%s</a>' % (logo)
			# Column 2 TBD
	
			# Column 3 enable/disable host in GUI
			if IsHostEnabled(hostName):
				OnOffState = formSUBMITvalue( [('cmd','OFF:host'+ hostName)], _('Disable'))
			else:
				OnOffState = formSUBMITvalue( [('cmd', 'ON:host'+ hostName)],  _('Enable'))

			# Column 4 host configuration options
			try:
				_temp = __import__('Plugins.Extensions.IPTVPlayer.hosts.host' + hostName, globals(), locals(), ['GetConfigList'], -1)
				OptionsList = _temp.GetConfigList()
			except Exception:
				OptionsList = []
	
			#build table row
			hostsCFG += '<tr>'
			hostsCFG += '<td style="width:120px">%s</td>' % hostNameWithURLandLOGO
			hostsCFG += '<td>%s</td>' % OnOffState 
			if len(OptionsList) == 0:
				hostsCFG += '<td><a>%s</a></td>' % "" # _('Host does not have configuration options')
			else:
				hostsCFG += '<td><table border="1" style="width:100%">'
				for item in self.buildSettingsTable(List2 = OptionsList, List1 = config.plugins.iptvplayer.dict().items(), exclList = usedCFG, direction = '2>1'):
					usedCFG.append(item[0])
					#print 'hostsCFG:',item[0], item[1],item[2]
					if item[0] == 'fake_separator':
						hostsCFG += '<tr><td colspan="2" align="center"><tt>%s</tt></td></tr>\n' % (item[1])
					else:
						hostsCFG += '<tr><td nowrap style="width:50%%"><tt>%s</tt></td><td>%s</td></tr>\n' % (item[1], formGET(item[2]))
				hostsCFG += '</table></td>'
			hostsCFG += '</tr>\n'
		hostsCFG += '</tbody></table>\n'
		#build plugin global settings
		pluginCFG = '<table width="850px" border="1"><tbody>\n'
		pluginCFG += '<tr><td align="center" colspan="2"><p><font size="5" color="#9FF781">%s</font></p></td></tr>\n' % _('Plugin global settings')
		from Plugins.Extensions.IPTVPlayer.components.iptvconfigmenu import ConfigMenu
		OptionsList = []
		ConfigMenu.fillConfigList(OptionsList, hiddenOptions=False)
		for item in self.buildSettingsTable(List1 = config.plugins.iptvplayer.dict().items(), List2 = OptionsList, exclList = usedCFG, direction = '2>1'):
			pluginCFG += '<tr><td><tt>%s</tt></td><td>%s</td></tr>\n' % (item[1], formGET(item[2]))
		
		pluginCFG += '</tbody></table>\n'
		tempText += pluginCFG + '<p><br</p>\n' + hostsCFG + '</div></body>\n'
		return tempText
	########################################################
	def hostsPageContent(self, htmlMessage = ''):
		tempText = '<body bgcolor=\"#666666\" text=\"#FFFFFF\">\n'
		tempText += IncludeMENU()
		tempText += '<div class="main">\n%s\n<table border="0" cellspacing="50px">\n<tbody>\n' % htmlMessage
		tempText += '<tr>'
		columnIndex = 1
		displayHostsList = SortHostsList(GetHostsList())
		if 0 == len(GetHostsOrderList()):
			try: displayHostsList.sort(key=lambda t : tuple('.'.join(str(t[0]).replace('://','.').replace('www.','').split('.')[1:-1]).lower()))
			except Exception: pass
		for hostName in displayHostsList:
			if hostName in settings.activeHostsHTML.keys():
				hostHTML = settings.activeHostsHTML[hostName]
			else:
				if hostName in ['localmedia','urllist']: # those are local host, nothing to do via web interface
					continue
				if not IsHostEnabled(hostName):
					continue
				# column 1 containing logo and link if available
				try:
					_temp = __import__('Plugins.Extensions.IPTVPlayer.hosts.host' + hostName, globals(), locals(), ['gettytul'], -1)
					title = _temp.gettytul()
					_temp = None
				except Exception:
					continue # we do NOT use broken hosts!!!
		
				logo = self.getHostLogo(hostName)
		
				if title[:4] == 'http' and logo == "":
					try:
						hostNameWithURLandLOGO = '<br><a href="./usehost?activeHost=%s" target="_blank"><font size="2" color="#58D3F7">%s</font></a>' % (hostName, '.'.join(title.replace('://','.').replace('www.','').split('.')[1:-1]))
					except Exception:
						hostNameWithURLandLOGO = '<br><a href="%s" target="_blank"><font size="2" color="#58D3F7">%s</font></a>' % (title, title)
				elif title[:4] == 'http' and logo != "":
					try:
						hostNameWithURLandLOGO = '<a href="./usehost?activeHost=%s">%s</a><br><a href="%s" target="_blank"><font size="2" color="#58D3F7">%s</font></a>' % (hostName, logo, title, '.'.join(title.replace('://','.').replace('www.','').split('.')[1:-1]))
					except Exception, e:
						print str(e)
						hostNameWithURLandLOGO = '<a href="%s" target="_blank">%s</a><br><a href="%s" target="_blank"><font size="2" color="#58D3F7">%s</font></a>' % (title, logo, title, _('visit site'))
				elif title[:4] != 'http' and logo != "":
					hostNameWithURLandLOGO = '<a href="./usehost?activeHost=%s">%s</a><br><a href="%s" target="_blank"><font size="2" color="#58D3F7">%s</font></a>' % (hostName, logo, title, title )
				else:
					hostNameWithURLandLOGO = '<br><a>%s</a>' % (title)
				# Column 2 TBD
		
				#build table row
				hostHTML = '<td align="center">%s</td>' % hostNameWithURLandLOGO
				settings.activeHostsHTML[hostName] = hostHTML
			
			tempText += hostHTML
			#tempText += '<td><button type="button" disabled>%s</button> </td>' % _('Enter')
			columnIndex += 1
			if columnIndex > 4:
				columnIndex = 1
				tempText += '</tr><tr>'
		tempText += '</tr>'
		tempText += '</tbody></table></div></body>\n'
		return tempText

	########################################################
	def downloaderPageContent(self, webDM, currList):
		DM_status = ''
		tempText = '<body bgcolor=\"#666666\" text=\"#FFFFFF\">\n'
		tempText += IncludeMENU()
		tempText += '<div class="main">\n'
		if webDM is None:
			tempText += '<table border="0" cellspacing="15px"><tbody>\n'
			tempText += '<td><b><font color="#FFE4C4">%s</font></b></td>' % _('Download manager is not initialized')
			tempText += '<td>' + formSUBMITvalue( [('cmd','initDM')], _("Initialize Download Manager")) + '</td>'
			tempText += '</tbody></table>\n'
		else:
			tempText += '<table border="0" cellspacing="15px"><tbody><tr>\n'
			if not webDM.isRunning():
				DM_status = _("STOPPED")
				tempText += '<td>' + formSUBMITvalue( [('cmd' , 'stopDM')], _("Stop"), 'disabled style="background-color:#ff6400"') + '</td>'
				tempText += '<td>' + formSUBMITvalue( [('cmd' , 'runDM')], _("Start"), 'style="background-color:#00FF00"') + '</td>'
			else:
				DM_status = _("STARTED")
				tempText += '<td>' + formSUBMITvalue( [('cmd' , 'stopDM')], _("Stop"), 'style="background-color:#ff6400"') + '</td>'
				tempText += '<td>' + formSUBMITvalue( [('cmd' , 'runDM')], _("Start"), 'disabled style="background-color:#00FF00"') + '</td>'
				#tempText += '<td><b><font color="#ccE4C4">%s</font></b></td>' % _('Start')
			tempText += '<td>' + formSUBMITvalue( [('cmd' , 'arvchiveDM')], _("Archive"), 'style="background-color:yellow"') + '</td>'
			tempText += '<td>' + formSUBMITvalue( [('cmd' , 'downloadsDM')], _("Downloads"), 'style="background-color:#0080FF"') + '</td></tr>\n'
			tempText += '<tr><td colspan="2">%s</td><td colspan="2">%s</td></tr>' % (_("Manager status: "), DM_status)
			tempText += '</tbody></table>\n'
			
			#display the list of downloads
			tempText += '<table  width="800px" cellspacing="5px"><tbody>\n'
			for item in currList:
				# Downloaded Size
				info1 = formatBytes(item.downloadedSize)
        
				# File Size
				if item.fileSize > 0:
					info1 += "/" + formatBytes(item.fileSize)
        
				elif item.totalFileDuration > 0 and item.downloadedFileDuration > 0:
					totalDuration = item.totalFileDuration
					downloadDuration = item.downloadedFileDuration
					totalDuration = str(timedelta(seconds=totalDuration))
					downloadDuration = str(timedelta(seconds=downloadDuration))
					if totalDuration.startswith('0:'):
						totalDuration = totalDuration[2:]
					if downloadDuration.startswith('0:'):
						downloadDuration = downloadDuration[2:]
					info1 = "{0}/{1} ({2})".format(downloadDuration, totalDuration, info1)

				# Downloaded Procent
				if item.downloadedProcent >= 0: info1 += ", " + str(item.downloadedProcent) + "%"
 
				# Download Speed
				info2 = info1 + ", " + formatBytes(item.downloadedSpeed) + "/s"
				
				try: fileName = item.fileName.split('/')[-1]
				except Exception: fileName = item.fileName
				if DMHelper.STS.WAITING == item.status:
					status = _("PENDING")
					icon = '<img border="0" src="./icons/iconwait1.png" width="64" height="64">'
					info = ''
					buttons = ''
				elif DMHelper.STS.DOWNLOADING == item.status:
					status = _("DOWNLOADING")
					icon = '<img border="0" src="./icons/iconwait2.png" width="64" height="64">'
					info = info2
					buttons = '<table><tbody><tr><td>%s</td><td>%s</td></tr></tbody></table>' % (
							formSUBMITvalue([('watchMovie' , item.fileName)], _("Watch")),
							formSUBMITvalue([('stopDownload' , item.downloadIdx)], _("Stop download")))
				
				elif DMHelper.STS.DOWNLOADED == item.status and item.url[:1] == '/': # for Archive section
					status = _("DOWNLOADED")
					icon = '<img border="0" src="./icons/icondone.png" width="64" height="64">'
					info = info1
					buttons = '<table><tbody><tr><td>%s</td><td>%s</td></tr></tbody></table>' % (
							formSUBMITvalue([('cmd' , 'arvchiveDM'),('cmd' , 'watchMovie'),('cmd' , item.fileName)], _("Watch")),
							formSUBMITvalue([('cmd' , 'arvchiveDM'),('cmd' , 'deleteMovie'),('cmd' , item.fileName)], _("Delete")))
				
				elif DMHelper.STS.DOWNLOADED == item.status:
					status = _("DOWNLOADED")
					icon = '<img border="0" src="./icons/icondone.png" width="64" height="64">'
					info = info1
					buttons = '<table><tbody><tr><td>%s</td><td>%s</td><td>%s</td></tr></tbody></table>' % (
							formSUBMITvalue([('watchMovie' , item.fileName)], _("Watch")),
							formSUBMITvalue([('downloadAgain' , item.downloadIdx)], _("Download again")),
							formSUBMITvalue([('removeMovie' , item.downloadIdx)], _("Delete")))
				elif DMHelper.STS.INTERRUPTED == item.status:
					status = _("ABORTED")
					icon = '<img border="0" src="./icons/iconerror.png" width="64" height="64">'
					info = info1
					buttons = '<table><tbody><tr><td>%s</td><td>%s</td><td>%s</td></tr></tbody></table>' % (
							formSUBMITvalue([('watchMovie' , item.fileName)], _("Watch")),
							formSUBMITvalue([('downloadAgain' , item.downloadIdx)], _("Download again")),
							formSUBMITvalue([('removeMovie' , item.downloadIdx)], _("Delete")))
				elif DMHelper.STS.ERROR == item.status:
					status = _("DOWNLOAD ERROR")
					icon = '<img border="0" src="./icons/iconwarning.png" width="64" height="64">'
					info = ''
					buttons = '<table><tbody><tr><td>%s</td><td>%s</td></tr></tbody></table>' % (
							formSUBMITvalue([('downloadAgain' , item.downloadIdx)], _("Download again")),
							formSUBMITvalue([('removeMovie' , item.downloadIdx)], _("Delete")))
				elif item.status == 'INFO':
					status = ''
					icon = '<img border="0" src="./icons/iconwarning.png" width="64" height="64">'
					info = ''
					buttons = ''
				else:
					status = ''
					icon = ''
					info = ''
					buttons = ''
				tempText += '<tr><td colspan="3" style="border: 1px solid red;"</td></tr>\n'
				tempText += '<tr><td rowspan="4" align="center">%s</td><td colspan="2"><b>%s</b></td></tr>\n' % (icon,fileName)
				tempText += '<tr><td><div style="text-indent: 20px">%s</div></td></tr>\n' % item.url
				tempText += '<tr><td>%s</td><td align="right">%s</td></tr>\n' %(info,status)
				tempText += '<tr><td colspan="3" align="right">%s</td></tr>\n' % (buttons)
			tempText += '<tr><td colspan="3" style="border: 1px solid red;"</td></tr>\n'
			tempText += '</tbody></table>\n'
		tempText += '</div></body>\n'
		return tempText
	########################################################
	def useHostSubMenu(self, isTop = True, LVL = 1 ):
		txt = '<table border="0" width="800px" cellspacing="5px"><tbody>\n'
		txtWarning = '<tr><td colspan="4" align="center"><p><b><font size="2" color="#FE642E">%s</font></b><font size="2">%s</font></p></td></tr>\n' % (
				      _('REMEMBER: '), _('accessing host via web <b>HAS LIMITED FUNCTIONALITY.</b> Use IPTVPlayer GUI version for full support!!!'))
		if isTop:
			txt += txtWarning
		txt += '<tr><td><br></td>'
		if settings.isCurrentItemSelected():
			txt += '<tr><td align="right">%s</td>' % formSUBMITvalue([('cmd','RefreshList')], _('Previous list'))
		else:
			if settings.activeHost['PathLevel'] <= 1:
				txt += '<tr><td align="right">%s</td>' % formSUBMITvalue([('cmd','PreviousList')], _('Previous list'), 'disabled' )
			else:
				txt += '<tr><td align="right">%s</td>' % formSUBMITvalue([('cmd','PreviousList')], _('Previous list'))
			txt += '<td style="width:10px" align="right">%s</td>' % formSUBMITvalue([('cmd','RefreshList')], _('Reload list'))
		txt += '<td style="width:10px" align="right">%s</td>' % formSUBMITvalue([('cmd','InitList')], _('Initial list'))
		txt += '<td style="width:10px" align="right">%s</td></tr>' % formSUBMITvalue([('cmd','hosts')], _('Return to hosts list'))
		if not isTop:
			txt += txtWarning
		txt += '</tbody></table><br>\n'
		return txt
	########################################################
	def buildItemsListTable(self, item, index):
		iIndex = index
		iName = removeSpecialChars(item.name)
		iDescr= removeSpecialChars(item.description)
		iType = item.type
		ListType = 'ListForItem'
		if iType == "CATEGORY":
			icon = '<img border="0" src="./icons/CategoryItem.png" width="64" height="64">'
		elif iType == "SEARCH":
			icon = '<img border="0" src="./icons/SearchItem.png" width="64" height="64">'
		elif iType == "VIDEO":
			ListType = 'ListForItem'
			icon = '<img border="0" src="%s" width="64">' % item.iconimage
			#icon = '<img border="0" src="./icons/VideoItem.png" width="64" height="64">'
		elif iType == "AUDIO":
			icon = '<img border="0" src="./icons/AudioItem.png" width="64" height="64">'
		else:
			icon = iType
		txt = '<tr><td colspan="2" style="border: 1px solid red;"></td></tr>\n'
		txt += '<tr><td rowspan="2" style="width:64px">%s</td>' % icon
		txt += '<td>%s</td></tr>' % formSUBMITvalue( [(ListType , iIndex)], _(iName), 'style="color: #DBA901;background: none;border: none;text-decoration: underline"')
		txt += '<tr><td style="text-indent: 40px">%s</td></tr>' % iDescr
		return txt
	########################################################
	def buildUrlsTable(self, item, index):
		iName= removeSpecialChars(item.name)
		iUrl= item.url #.replace("ext://url/","") #to chyba sss zrobil do wymuszenia extplayera przyklad pierwszatv
		iurlNeedsResolve= int(item.urlNeedsResolve)
		txt = '<tr><td colspan = "3" style="border: 1px solid red;"></td></tr>\n'
		if iUrl	in ['', 'fake','fakeUrl']:
			txt += '<td colspan="2" align="center">%s</td></tr>' % ( iName )
		else:
			if int(item.urlNeedsResolve) == 1:
				txt += '<td>%s</td><td>%s</td></tr>' % ( iName , formSUBMITvalue( [('ResolveURL' , index)], _('Download')) )
			else:
				#txt += '<td>%s</td><td>%s</td>' % ( iName , formSUBMITvalue( [('DownloadURL' , index)], _('Download')) )
				txt += '<td>%s</td><td><a href="/iptvplayer/usehost?DownloadURL=%d" class = "lnkbtn">%s</a></td>' % (iName, index, _('Add to downloader'))
				txt += '<td> <a href="%s" target="_blank" class = "lnkbtn">%s</a></td></tr>' % (iUrl, _('Watch'))
		return txt
	########################################################
	def useHostPageContent(self, errMSG = ''):
		tempText = '<body bgcolor=\"#666666\" text=\"#FFFFFF\">\n'
		tempText += IncludeMENU()
		tempText += '<div class="main">\n'
		#error msg
		if errMSG != '':
			tempText += '<p align="center"><b><font color="#FE642E">%s</font></b>, %s</p>' % ( _('Exception occured:'), errMSG )
		#Status table
		tempText += '<table border="0" cellspacing="5px"><tbody>\n'
		tempText += '<tr>'
		tempText += '<td align="right"><font color="#f0f0f0">%s</font></td><td><b><font color="#FFE4C4">%s</font></b></td>' % ( _('host:') , settings.activeHost['Name'] )
		tempText += '<td align="right"><font color="#f0f0f0">%s</font></td><td><b><font color="#FFE4C4">%s</font></b></td>' % ( _('Title:') , settings.activeHost['Title'] )
		#tempText += '</tr>\n'
		#tempText += '<tr>'
		tempText += '<td align="right"><font color="#f0f0f0">%s</font></td><td><b><font color="#FFE4C4">%s</font></b></td>' % ( _('Level:') , settings.activeHost['PathLevel'] )
		tempText += '<td align="right"><font color="#f0f0f0">%s</font></td><td><b><font color="#FFE4C4">%s</font></b></td>' % ( _('Path:') , settings.activeHost['Status'] )
		tempText += '</tr>\n'
		tempText += '</tbody></table>\n'
		tempText += self.useHostSubMenu() #Submenu table
		# main list
		if settings.isCurrentItemSelected():
			tempText += '<table border="0" cellspacing="15px"><tbody>\n'
			tempText += '<tr><td colspan = "3" style="border: 1px solid blue;">%s "<b>%s</b>"</td></tr>\n' % ( _('Links for') , settings.currItem['itemTitle'])
		else:
			tempText += '<table border="0" width="800px" cellspacing="5px"><tbody>\n'
		index=0
		#if type(settings.retObj.value) is list:
		if len(settings.retObj.value) > 0:
			for item in settings.retObj.value:
				if settings.isCurrentItemSelected():
					tempText += self.buildUrlsTable(item, index)
				else:
					tempText += self.buildItemsListTable(item, index)
				index += 1
		txt = '<tr><td colspan="3" style="border: 1px solid red;"></td></tr>\n'
		tempText += '</tbody></table>\n'
			# end main list
		if index > 10:
			tempText += '<tr><td><br></td>'
			tempText += self.useHostSubMenu(isTop = False) #Submenu table
		tempText += '</div></body>\n'
		return tempText
